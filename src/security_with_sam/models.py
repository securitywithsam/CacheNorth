from __future__ import annotations

import hashlib
import json
import platform
import re
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

import psutil

from .engine import detect_cpu_profile
from .security import confined_path
from .settings import SettingsStore


class GGUFError(ValueError):
    pass


_SIZES = {0: 1, 1: 1, 2: 2, 3: 2, 4: 4, 5: 4, 6: 4, 7: 1, 10: 8, 11: 8, 12: 8}
_INT_FORMATS = {0: "<B", 1: "<b", 2: "<H", 3: "<h", 4: "<I", 5: "<i", 7: "<?", 10: "<Q", 11: "<q"}
_FLOAT_FORMATS = {6: "<f", 12: "<d"}
_MAX_METADATA_ITEMS = 2_000_000
_MAX_STRING_BYTES = 16 * 1024 * 1024


def _read_exact(stream: BinaryIO, size: int) -> bytes:
    value = stream.read(size)
    if len(value) != size:
        raise GGUFError("The GGUF metadata is truncated.")
    return value


def _u32(stream: BinaryIO) -> int:
    return struct.unpack("<I", _read_exact(stream, 4))[0]


def _u64(stream: BinaryIO) -> int:
    return struct.unpack("<Q", _read_exact(stream, 8))[0]


def _string(stream: BinaryIO) -> str:
    size = _u64(stream)
    if size > _MAX_STRING_BYTES:
        raise GGUFError("The GGUF metadata contains an unsafe string length.")
    return _read_exact(stream, size).decode("utf-8", errors="replace")


def _value(stream: BinaryIO, kind: int, *, keep: bool = True, depth: int = 0):
    if depth > 2:
        raise GGUFError("The GGUF metadata nesting is unsupported.")
    if kind == 8:
        value = _string(stream)
        return value if keep else None
    if kind == 9:
        item_kind = _u32(stream)
        count = _u64(stream)
        if count > _MAX_METADATA_ITEMS:
            raise GGUFError("The GGUF metadata array is unreasonably large.")
        if not keep and item_kind in _SIZES:
            stream.seek(count * _SIZES[item_kind], 1)
            return None
        values = [_value(stream, item_kind, keep=keep, depth=depth + 1) for _ in range(count)]
        return values if keep else None
    if kind in _INT_FORMATS:
        raw = _read_exact(stream, _SIZES[kind])
        value = struct.unpack(_INT_FORMATS[kind], raw)[0]
        return value if keep else None
    if kind in _FLOAT_FORMATS:
        raw = _read_exact(stream, _SIZES[kind])
        value = struct.unpack(_FLOAT_FORMATS[kind], raw)[0]
        return value if keep else None
    raise GGUFError(f"Unknown GGUF metadata type {kind}.")


# Architecture fields needed to size the KV cache for a given context length.
_SHAPE_SUFFIXES = (
    ".context_length",
    ".block_count",
    ".embedding_length",
    ".attention.head_count",
    ".attention.head_count_kv",
    ".attention.key_length",
    ".attention.value_length",
    ".full_attention_interval",
)


def read_gguf_metadata(path: Path) -> dict[str, object]:
    wanted = {
        "general.architecture",
        "general.name",
        "general.parameter_count",
        "general.file_type",
        "general.size_label",
        "tokenizer.chat_template",
    }
    metadata: dict[str, object] = {}
    with path.open("rb") as stream:
        if _read_exact(stream, 4) != b"GGUF":
            raise GGUFError("The file does not have a GGUF signature.")
        version = _u32(stream)
        if version not in {2, 3}:
            raise GGUFError(f"GGUF version {version} is unsupported.")
        _u64(stream)  # tensor count
        count = _u64(stream)
        if count > _MAX_METADATA_ITEMS:
            raise GGUFError("The GGUF metadata table is unreasonably large.")
        for _ in range(count):
            key = _string(stream)
            kind = _u32(stream)
            keep = key in wanted or key.endswith(_SHAPE_SUFFIXES)
            value = _value(stream, kind, keep=keep)
            if keep:
                metadata[key] = value
    metadata["gguf.version"] = version
    return metadata


def _quantization(file_type: object, filename: str) -> str:
    match = re.search(r"(?:^|[-_.])(Q\d(?:_[A-Z0-9]+)*)", filename.upper())
    if match:
        return match.group(1)
    known = {2: "Q4_0", 3: "Q4_1", 7: "Q8_0", 12: "Q4_K", 15: "Q4_K_M"}
    return known.get(file_type, f"GGUF type {file_type}")


def _display_title(raw_title: str, filename: str, quantization: str) -> str:
    """Present the local GGUF format instead of an inherited source-checkpoint label."""
    title = re.sub(r"\s+AWQ\b", "", raw_title, flags=re.IGNORECASE).strip()
    if title != raw_title.strip() and quantization:
        return f"{title} (GGUF {quantization})"
    return title or Path(filename).stem


@dataclass(frozen=True)
class ModelInfo:
    name: str
    title: str
    size_bytes: int
    architecture: str | None
    parameters: int | None
    size_label: str | None
    quantization: str | None
    context_length: int | None
    has_chat_template: bool
    identity: str
    status: str
    reason: str
    estimated_memory_bytes: int

    def as_dict(self) -> dict[str, object]:
        return self.__dict__.copy()


class ModelManager:
    """Discovers validated GGUF models and selects one conservatively for this computer."""

    def __init__(self, models_dir: Path, settings: SettingsStore, total_ram_bytes: int | None = None):
        self.models_dir = models_dir
        self.settings = settings
        self.total_ram_bytes = total_ram_bytes

    @property
    def total_ram(self) -> int:
        return self.total_ram_bytes or psutil.virtual_memory().total

    def computer_key(self) -> str:
        cpu_mode = detect_cpu_profile().mode
        ram_bucket = "8" if self.total_ram < 12 * 1024**3 else "16" if self.total_ram < 24 * 1024**3 else "32+"
        coarse = f"{platform.machine().lower()}|{cpu_mode}|{ram_bucket}"
        return hashlib.sha256(coarse.encode("utf-8")).hexdigest()[:16]

    def scan(self) -> list[ModelInfo]:
        if not self.models_dir.is_dir():
            return []
        results: list[ModelInfo] = []
        for path in sorted(self.models_dir.glob("*.gguf"), key=lambda item: item.name.lower()):
            stat = path.stat()
            identity = hashlib.sha256(f"{path.name}|{stat.st_size}|{stat.st_mtime_ns}".encode()).hexdigest()
            estimate = int(stat.st_size * 1.30 + 768 * 1024**2)
            try:
                metadata = read_gguf_metadata(path)
                architecture = str(metadata.get("general.architecture") or "").strip() or None
                raw_title = str(metadata.get("general.name") or path.stem).strip()
                quantization = _quantization(metadata.get("general.file_type"), path.name)
                title = _display_title(raw_title, path.name, quantization)
                parameters = metadata.get("general.parameter_count")
                parameters = int(parameters) if isinstance(parameters, int) else None
                context = next((int(v) for k, v in metadata.items() if k.endswith(".context_length") and isinstance(v, int)), None)
                template = bool(metadata.get("tokenizer.chat_template"))
                supported = architecture in {"qwen2", "qwen3", "qwen3moe", "qwen3next", "qwen35"}
                if not architecture:
                    status, reason = "unsupported", "The model does not declare an architecture."
                elif not supported:
                    status, reason = "unsupported", f"Architecture {architecture} is unsupported by this release."
                elif not template:
                    status, reason = "unsupported", "The model does not contain a chat template."
                elif estimate > max(0, self.total_ram - 1536 * 1024**2):
                    status, reason = "too-large", "Estimated memory use is too high for this computer."
                else:
                    verified = self._verified().get(identity)
                    if verified is True:
                        status, reason = "verified", "A load and generation test succeeded on this computer."
                    else:
                        status, reason = "eligible", "Metadata validated; load and generation test still required."
                results.append(ModelInfo(
                    path.name, title, stat.st_size, architecture, parameters,
                    str(metadata.get("general.size_label")) if metadata.get("general.size_label") else None,
                    quantization, context, template,
                    identity, status, reason, estimate,
                ))
            except (OSError, GGUFError, ValueError) as exc:
                results.append(ModelInfo(
                    path.name, path.stem, stat.st_size, None, None, None, None, None, False,
                    identity, "unsupported", str(exc), estimate,
                ))
        return results

    def automatic(self, models: list[ModelInfo] | None = None) -> ModelInfo | None:
        eligible = [item for item in (models or self.scan()) if item.status in {"eligible", "verified"}]
        if not eligible:
            return None
        # 8 GB systems receive the smallest validated model. Larger systems receive the
        # strongest model that retains a conservative 1.5 GiB operating-system reserve.
        if self.total_ram < 12 * 1024**3:
            return min(eligible, key=lambda item: item.estimated_memory_bytes)
        def rank(item: ModelInfo) -> tuple[int, int]:
            family = 2 if "3.5" in item.name.lower() or "3.5" in item.title.lower() else 1
            return (item.parameters or item.size_bytes, family)
        return max(eligible, key=rank)

    def selected(self) -> ModelInfo | None:
        models = self.scan()
        by_name = {item.name: item for item in models}
        saved = self.settings.load()
        if saved.get("model_mode") == "manual":
            manual = by_name.get(str(saved.get("manual_model") or ""))
            if manual and manual.status in {"eligible", "verified"}:
                return manual
        return self.automatic(models)

    def set_manual(self, filename: str) -> ModelInfo:
        selected_path = confined_path(self.models_dir, self.models_dir / Path(filename).name)
        if selected_path.name != filename:
            raise ValueError("Invalid model filename.")
        item = next((model for model in self.scan() if model.name == filename), None)
        if item is None:
            raise FileNotFoundError("The selected model is missing.")
        if item.status not in {"eligible", "verified"}:
            raise ValueError(item.reason)
        self.settings.save({"model_mode": "manual", "manual_model": item.name})
        return item

    def restore_automatic(self) -> ModelInfo | None:
        self.settings.save({"model_mode": "automatic", "manual_model": None})
        return self.automatic()

    @property
    def compatibility_path(self) -> Path:
        return self.settings.path.parent / "model-compatibility.json"

    def _verified(self) -> dict[str, bool]:
        try:
            raw = json.loads(self.compatibility_path.read_text(encoding="utf-8"))
            computer = raw.get(self.computer_key(), {}) if isinstance(raw, dict) else {}
            return {str(key): value is True for key, value in computer.items()} if isinstance(computer, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def mark_verified(self, identity: str) -> None:
        try:
            raw = json.loads(self.compatibility_path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raw = {}
        except (OSError, json.JSONDecodeError):
            raw = {}
        computer = raw.setdefault(self.computer_key(), {})
        if not isinstance(computer, dict):
            computer = {}
            raw[self.computer_key()] = computer
        computer[identity] = True
        self.compatibility_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.compatibility_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(raw, indent=2), encoding="utf-8")
        temporary.replace(self.compatibility_path)
