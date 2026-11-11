from __future__ import annotations

import struct
from pathlib import Path

from security_with_sam.models import GGUFError, ModelInfo, ModelManager, read_gguf_metadata
from security_with_sam.settings import SettingsStore


def _text(value: str) -> bytes:
    encoded = value.encode()
    return struct.pack("<Q", len(encoded)) + encoded


def write_test_gguf(path: Path, architecture: str = "qwen3", template: str = "{{ messages }}") -> None:
    values = [
        ("general.architecture", 8, _text(architecture)),
        ("general.name", 8, _text("Portable test model")),
        ("general.size_label", 8, _text("1.7B")),
        ("general.file_type", 4, struct.pack("<I", 15)),
        (f"{architecture}.context_length", 4, struct.pack("<I", 40960)),
        ("tokenizer.chat_template", 8, _text(template)),
    ]
    body = b"".join(_text(key) + struct.pack("<I", kind) + value for key, kind, value in values)
    path.write_bytes(b"GGUF" + struct.pack("<IQQ", 3, 0, len(values)) + body)


def test_bounded_gguf_parser_reads_required_metadata(tmp_path: Path):
    model = tmp_path / "Qwen3-1.7B-Q4_K_M.gguf"
    write_test_gguf(model)
    metadata = read_gguf_metadata(model)
    assert metadata["general.architecture"] == "qwen3"
    assert metadata["qwen3.context_length"] == 40960
    assert metadata["tokenizer.chat_template"] == "{{ messages }}"


def test_gguf_extension_alone_is_rejected(tmp_path: Path):
    model = tmp_path / "fake.gguf"
    model.write_bytes(b"not a model")
    try:
        read_gguf_metadata(model)
    except GGUFError as exc:
        assert "signature" in str(exc)
    else:
        raise AssertionError("Invalid GGUF was accepted")


def test_model_scan_accepts_qwen35_and_rejects_unknown_architecture(tmp_path: Path):
    models = tmp_path / "Models"; models.mkdir()
    write_test_gguf(models / "Qwen3.5-4B-Q4_K_M.gguf", architecture="qwen35")
    write_test_gguf(models / "unknown.gguf", architecture="mystery")
    manager = ModelManager(models, SettingsStore(tmp_path / "settings.json"), total_ram_bytes=16 * 1024**3)
    found = {item.name: item for item in manager.scan()}
    assert found["Qwen3.5-4B-Q4_K_M.gguf"].status == "eligible"
    assert found["unknown.gguf"].status == "unsupported"


def test_automatic_selection_is_smallest_on_8gb_and_strongest_on_16gb(tmp_path: Path):
    def item(name: str, size: int, parameters: int) -> ModelInfo:
        return ModelInfo(name, name, size, "qwen3", parameters, None, "Q4_K_M", 40960, True, name, "eligible", "", size)
    candidates = [item("Qwen3-1.7B.gguf", 2, 1_700_000_000), item("Qwen3.5-4B.gguf", 4, 4_000_000_000)]
    settings = SettingsStore(tmp_path / "settings.json")
    assert ModelManager(tmp_path, settings, total_ram_bytes=8 * 1024**3).automatic(candidates).name == "Qwen3-1.7B.gguf"
    assert ModelManager(tmp_path, settings, total_ram_bytes=16 * 1024**3).automatic(candidates).name == "Qwen3.5-4B.gguf"


def test_missing_manual_model_falls_back_to_valid_automatic_choice(tmp_path: Path):
    models = tmp_path / "Models"; models.mkdir()
    write_test_gguf(models / "available.gguf")
    settings = SettingsStore(tmp_path / "settings.json")
    settings.save({"model_mode": "manual", "manual_model": "removed.gguf"})
    selected = ModelManager(models, settings, total_ram_bytes=16 * 1024**3).selected()
    assert selected is not None and selected.name == "available.gguf"
