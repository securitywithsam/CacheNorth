"""Per-computer context-length planning with memory estimates checked against KoboldCpp 1.124.2.

Estimates come from GGUF metadata, not model names. KV cache bytes per token are
KV layers x KV heads x (key + value dims) x 2 bytes (f16), and KoboldCpp reserves the
requested context plus 256 cells. Both were verified to the MiB against KoboldCpp's own
`llama_kv_cache` log lines for all three bundled models
(output/v103/context-memory-measured.json). Other buffers are conservative allowances
fitted to the measured process commit charge.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

import psutil

from .engine import MemoryProfile, select_memory_profile
from .models import read_gguf_metadata

if TYPE_CHECKING:
    from .settings import SettingsStore

OPTIONS = (2048, 4096, 8192, 16384, 32768)
MINIMUM = OPTIONS[0]
KV_EXTRA_CELLS = 256
MIB = 1024**2
# Measured commit charge above model file + KV cache (compute buffers, runtime): Qwen3 dense
# 467-538 MiB, Qwen3.5 hybrid 1,170-1,204 MiB, growing about 1 MiB per 1,024 context tokens.
CPU_OVERHEAD_MIB = {"dense": 560, "hybrid": 1240}
# With every layer on the GPU, measured resident host memory was 371-547 MiB (Qwen3) and
# 758-790 MiB (Qwen3.5). Windows commit charge is higher because of driver mappings.
GPU_HOST_MIB = {"dense": 700, "hybrid": 1000}
# Measured Vulkan compute buffers: 315-349 MiB (Qwen3), 507-537 MiB (Qwen3.5).
GPU_DEVICE_OVERHEAD_MIB = {"dense": 360, "hybrid": 560}
COMFORT = 0.85


def max_output_for(context: int) -> int:
    return 384 if context <= 2048 else 768 if context <= 4096 else 1024


def profile_for(context: int, name: str) -> MemoryProfile:
    return MemoryProfile(name, context, max_output_for(context))


@dataclass(frozen=True)
class ModelShape:
    filename: str
    file_bytes: int
    max_context: int | None
    kv_bytes_per_token: int | None
    hybrid: bool


@lru_cache(maxsize=16)
def _shape(path: str, size: int, _mtime_ns: int) -> ModelShape:
    metadata = read_gguf_metadata(Path(path))
    arch = str(metadata.get("general.architecture") or "")

    def field(name: str) -> int | None:
        value = metadata.get(f"{arch}.{name}")
        return int(value) if isinstance(value, int) else None

    blocks, heads, heads_kv, embedding = field("block_count"), field("attention.head_count"), field("attention.head_count_kv"), field("embedding_length")
    key = field("attention.key_length") or (embedding // heads if embedding and heads else None)
    value = field("attention.value_length") or key
    interval = field("full_attention_interval")
    kv_layers = (blocks // interval if interval else blocks) if blocks else None
    per_token = kv_layers * (heads_kv or heads) * (key + value) * 2 if kv_layers and (heads_kv or heads) and key and value else None
    return ModelShape(Path(path).name, size, field("context_length"), per_token, bool(interval))


def model_shape(path: Path) -> ModelShape:
    stat = path.stat()
    return _shape(str(path), stat.st_size, stat.st_mtime_ns)


def estimate(shape: ModelShape, context: int, backend: str) -> dict[str, int | None]:
    """Estimated MiB of system RAM and graphics memory for one context size."""
    kind = "hybrid" if shape.hybrid else "dense"
    if shape.kv_bytes_per_token is None:
        return {"kv_mib": None, "ram_mib": None, "vram_mib": None}
    kv = shape.kv_bytes_per_token * (context + KV_EXTRA_CELLS) / MIB
    growth = context / 1024
    file_mib = shape.file_bytes / MIB
    if backend == "gpu":
        return {
            "kv_mib": round(kv),
            "ram_mib": round(GPU_HOST_MIB[kind] + growth),
            "vram_mib": round(file_mib + kv + GPU_DEVICE_OVERHEAD_MIB[kind] + growth),
        }
    return {"kv_mib": round(kv), "ram_mib": round(file_mib + kv + CPU_OVERHEAD_MIB[kind] + growth), "vram_mib": 0}


def available_memory_mib(engine_pid: int | None = None) -> int:
    """Available RAM plus what the running engine would release when it restarts."""
    available = psutil.virtual_memory().available
    if engine_pid:
        try:
            process = psutil.Process(engine_pid)
            for item in [process, *process.children(recursive=True)]:
                available += getattr(item.memory_info(), "private", 0) or item.memory_info().rss
        except psutil.Error:
            pass
    return round(available / MIB)


def fit_level(needed: int | None, available: int | None) -> str:
    if needed is None or available is None:
        return "unknown"
    if needed <= available * COMFORT:
        return "fits"
    return "tight" if needed <= available else "exceeds"


def automatic_context(shape: ModelShape, backend: str, ram_mib: int, vram_mib: int | None, total_ram_bytes: int | None = None) -> int:
    """Largest option up to the RAM tier (2K/4K/8K, unchanged from v1.0.x) that comfortably fits."""
    cap = select_memory_profile(total_ram_bytes).context_size
    if shape.max_context:
        cap = min(cap, shape.max_context)
    for size in sorted((option for option in OPTIONS if option <= cap), reverse=True):
        need = estimate(shape, size, backend)
        memory_ok = fit_level(need["ram_mib"], ram_mib) == "fits"
        device_ok = backend != "gpu" or vram_mib is None or fit_level(need["vram_mib"], vram_mib) == "fits"
        if memory_ok and device_ok:
            return size
    return MINIMUM


def load_choice(settings: "SettingsStore", machine: str) -> dict[str, object]:
    raw = settings.load().get("computer_profiles", {}).get(machine)
    raw = raw if isinstance(raw, dict) else {}
    size = raw.get("context_size")
    failure = raw.get("context_failure")
    return {
        "context_size": size if size in OPTIONS else "auto",
        "context_failure": failure if isinstance(failure, dict) else None,
    }


def options_report(shape: ModelShape, backend: str, ram_mib: int, vram_mib: int | None, automatic: int) -> list[dict[str, object]]:
    rows = []
    for size in OPTIONS:
        need = estimate(shape, size, backend)
        supported = shape.max_context is None or size <= shape.max_context
        level = fit_level(need["ram_mib"], ram_mib)
        if backend == "gpu":
            device = fit_level(need["vram_mib"], vram_mib) if vram_mib is not None else "unknown"
            order = ["fits", "unknown", "tight", "exceeds"]
            level = max(level, device, key=order.index)
        rows.append({"size": size, **need, "level": level, "supported": supported, "automatic": size == automatic})
    return rows


@dataclass(frozen=True)
class ContextPlan:
    requested: MemoryProfile
    safe: MemoryProfile | None
    mode: str
    note: str | None
    report: dict[str, object]
    chosen: int | None = None  # The manual size the user picked (before any pause substitution).
    paused: bool = False


def plan(
    model: Path,
    settings: "SettingsStore",
    machine: str,
    backend: str,
    vram_mib: int | None,
    engine_pid: int | None = None,
    explicit: bool = False,
    total_ram_bytes: int | None = None,
) -> ContextPlan:
    shape = model_shape(model)
    ram = available_memory_mib(engine_pid)
    automatic = automatic_context(shape, backend, ram, vram_mib, total_ram_bytes)
    choice = load_choice(settings, machine)
    note = None
    chosen, paused = None, False
    if choice["context_size"] == "auto":
        size, mode = automatic, "automatic"
    else:
        size, mode = int(choice["context_size"]), "manual"
        if shape.max_context and size > shape.max_context:
            size, note = shape.max_context, f"{shape.filename} supports at most {shape.max_context:,} tokens; using that."
        chosen = size
        failure = choice["context_failure"]
        if failure and failure.get("size") == size and not explicit:
            paused = True
            note = (
                f"The {size:,}-token context could not start on this computer earlier, so the safe {automatic:,}-token "
                "context is used. Apply the context setting again to retry."
            )
            size = automatic
    safe_size = automatic if size > automatic else (MINIMUM if size > MINIMUM else None)
    report = {
        "mode": mode,
        "requested_size": size,
        "automatic_size": automatic,
        "model": shape.filename,
        "model_max": shape.max_context,
        "available_ram_mib": ram,
        "available_vram_mib": vram_mib,
        "backend_for_estimate": backend,
    }
    return ContextPlan(
        profile_for(size, mode), profile_for(safe_size, "safe-fallback") if safe_size else None, mode, note, report,
        chosen, paused,
    )


def record_outcome(settings: "SettingsStore", machine: str, plan_: ContextPlan, actual: int | None, reason: str | None) -> None:
    """Remember a manual context that failed so later starts do not repeat the failure.

    A paused start ran at a substituted safe size, so it says nothing about the chosen size and
    must not clear the remembered failure (otherwise every other start would retry and fail).
    """
    if plan_.mode != "manual" or plan_.paused or plan_.chosen is None:
        return
    if actual is not None and actual < plan_.chosen:
        settings.update_profile(machine, {"context_failure": {"size": plan_.chosen, "message": reason, "at": int(time.time())}})
    elif actual == plan_.chosen:
        settings.update_profile(machine, {"context_failure": None})
