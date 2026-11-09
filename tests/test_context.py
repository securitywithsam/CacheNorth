from __future__ import annotations

import json
import struct
from pathlib import Path

import pytest

from security_with_sam import context
from security_with_sam.config import AppPaths
from security_with_sam.context import (
    MINIMUM,
    OPTIONS,
    ModelShape,
    automatic_context,
    estimate,
    fit_level,
    load_choice,
    model_shape,
    options_report,
    plan,
    record_outcome,
)
from security_with_sam.engine import CpuProfile, KoboldEngine, MemoryProfile
from security_with_sam.prompting import PromptTooLong, build_messages, estimate_tokens
from security_with_sam.settings import SettingsStore

MEASURED = json.loads((Path(__file__).parent / "fixtures" / "context_memory_measured_v103.json").read_text(encoding="utf-8"))
MIB = 1024**2

# Architecture metadata exactly as stored in the three bundled GGUF files.
REAL_SHAPES = {
    "Qwen3-1.7B-Q4_K_M.gguf": ("qwen3", 1282439264, {"block_count": 28, "attention.head_count": 16, "attention.head_count_kv": 8, "attention.key_length": 128, "attention.value_length": 128, "embedding_length": 2048, "context_length": 40960}),
    "Qwen3-4B-Q4_K_M.gguf": ("qwen3", 2497280256, {"block_count": 36, "attention.head_count": 32, "attention.head_count_kv": 8, "attention.key_length": 128, "attention.value_length": 128, "embedding_length": 2560, "context_length": 40960}),
    "Qwen3.5-4B-Q4_K_M.gguf": ("qwen35", 2740937888, {"block_count": 32, "attention.head_count": 16, "attention.head_count_kv": 4, "attention.key_length": 256, "attention.value_length": 256, "embedding_length": 2560, "context_length": 262144, "full_attention_interval": 4}),
}


def _text(value: str) -> bytes:
    encoded = value.encode()
    return struct.pack("<Q", len(encoded)) + encoded


def write_shape_gguf(path: Path, arch: str, fields: dict[str, int]) -> None:
    values = [("general.architecture", 8, _text(arch)), ("tokenizer.chat_template", 8, _text("{{ messages }}"))]
    values += [(f"{arch}.{key}", 4, struct.pack("<I", value)) for key, value in fields.items()]
    body = b"".join(_text(key) + struct.pack("<I", kind) + value for key, kind, value in values)
    path.write_bytes(b"GGUF" + struct.pack("<IQQ", 3, 0, len(values)) + body)


def real_shape(tmp_path: Path, name: str) -> ModelShape:
    arch, size, fields = REAL_SHAPES[name]
    path = tmp_path / name
    write_shape_gguf(path, arch, fields)
    parsed = model_shape(path)
    return ModelShape(name, size, parsed.max_context, parsed.kv_bytes_per_token, parsed.hybrid)


@pytest.mark.parametrize("row", MEASURED, ids=lambda r: f"{r['backend']}-{r['model'][:10]}-{r['context']}")
def test_kv_estimate_matches_koboldcpp_log_exactly(tmp_path: Path, row):
    shape = real_shape(tmp_path, row["model"])
    assert row["n_ctx"] == row["context"] + context.KV_EXTRA_CELLS
    assert estimate(shape, row["context"], "gpu" if row["backend"] == "vulkan" else "cpu")["kv_mib"] == round(row["kv_mib"])


@pytest.mark.parametrize("row", [r for r in MEASURED if r["backend"] == "cpu"], ids=lambda r: f"{r['model'][:10]}-{r['context']}")
def test_cpu_memory_estimate_is_conservative_but_close(tmp_path: Path, row):
    need = estimate(real_shape(tmp_path, row["model"]), row["context"], "cpu")["ram_mib"]
    assert row["private_mib"] <= need <= row["private_mib"] + 300


@pytest.mark.parametrize("row", [r for r in MEASURED if r["backend"] == "vulkan"], ids=lambda r: f"{r['model'][:10]}-{r['context']}")
def test_gpu_estimates_cover_measured_device_and_resident_memory(tmp_path: Path, row):
    need = estimate(real_shape(tmp_path, row["model"]), row["context"], "gpu")
    assert need["vram_mib"] >= row["model_mib"] + row["kv_mib"] + row["compute_mib"]
    assert need["ram_mib"] >= row["rss_mib"]


def test_model_maximum_comes_from_metadata(tmp_path: Path):
    assert real_shape(tmp_path, "Qwen3-4B-Q4_K_M.gguf").max_context == 40960
    assert real_shape(tmp_path, "Qwen3.5-4B-Q4_K_M.gguf").max_context == 262144
    small = ModelShape("small.gguf", 10 * MIB, 8192, 4096, False)
    report = options_report(small, "cpu", 64000, None, 8192)
    assert [row["supported"] for row in report] == [True, True, True, False, False]


def test_fit_levels():
    assert fit_level(800, 1000) == "fits"
    assert fit_level(900, 1000) == "tight"
    assert fit_level(1100, 1000) == "exceeds"
    assert fit_level(None, 1000) == "unknown"


def test_automatic_keeps_ram_tier_and_shrinks_when_memory_is_short(tmp_path: Path):
    shape = real_shape(tmp_path, "Qwen3-4B-Q4_K_M.gguf")
    assert automatic_context(shape, "cpu", 20000, None, total_ram_bytes=32 * 1024**3) == 8192
    assert automatic_context(shape, "cpu", 20000, None, total_ram_bytes=16 * 1024**3) == 4096
    assert automatic_context(shape, "cpu", 20000, None, total_ram_bytes=8 * 1024**3) == 2048
    assert automatic_context(shape, "cpu", 4300, None, total_ram_bytes=32 * 1024**3) < 8192
    assert automatic_context(shape, "gpu", 20000, 3500, total_ram_bytes=32 * 1024**3) < 8192


def test_manual_choice_is_per_computer_and_failure_is_remembered(tmp_path: Path, monkeypatch):
    model = tmp_path / "Qwen3-1.7B-Q4_K_M.gguf"
    write_shape_gguf(model, "qwen3", REAL_SHAPES[model.name][2])
    store = SettingsStore(tmp_path / "settings.json")
    store.update_profile("desktop", {"context_size": 16384})
    monkeypatch.setattr(context, "available_memory_mib", lambda pid=None: 20000)
    desktop = plan(model, store, "desktop", "cpu", None, total_ram_bytes=32 * 1024**3)
    laptop = plan(model, store, "laptop", "cpu", None, total_ram_bytes=32 * 1024**3)
    assert (desktop.mode, desktop.requested.context_size, desktop.safe.context_size) == ("manual", 16384, 8192)
    assert (laptop.mode, laptop.requested.context_size) == ("automatic", 8192)
    assert laptop.safe.context_size == MINIMUM
    record_outcome(store, "desktop", desktop, 8192, "did not start")
    assert load_choice(store, "desktop")["context_failure"]["size"] == 16384
    paused = plan(model, store, "desktop", "cpu", None, total_ram_bytes=32 * 1024**3)
    assert paused.requested.context_size == 8192 and "could not start" in paused.note
    record_outcome(store, "desktop", desktop, 16384, None)
    assert load_choice(store, "desktop")["context_failure"] is None


def test_paused_start_keeps_the_remembered_failure(tmp_path: Path, monkeypatch):
    model = tmp_path / "Qwen3-1.7B-Q4_K_M.gguf"
    write_shape_gguf(model, "qwen3", REAL_SHAPES[model.name][2])
    store = SettingsStore(tmp_path / "settings.json")
    store.update_profile("pc", {"context_size": 32768, "context_failure": {"size": 32768, "message": "x"}})
    monkeypatch.setattr(context, "available_memory_mib", lambda pid=None: 20000)
    paused = plan(model, store, "pc", "cpu", None, total_ram_bytes=32 * 1024**3)
    assert paused.paused and paused.requested.context_size == 8192
    record_outcome(store, "pc", paused, 8192, None)  # The substituted size started fine...
    assert load_choice(store, "pc")["context_failure"]["size"] == 32768  # ...but 32K is still remembered as failing.
    assert plan(model, store, "pc", "cpu", None, total_ram_bytes=32 * 1024**3).paused


def test_settings_stores_for_one_file_share_a_lock_and_never_lose_updates(tmp_path: Path):
    import threading

    path = tmp_path / "settings.json"
    first, second = SettingsStore(path), SettingsStore(tmp_path / "." / "settings.json")
    assert first._lock is second._lock
    threads = [threading.Thread(target=store.update_profile, args=("pc", {f"key{index}": index})) for index, store in enumerate([first, second] * 20)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    profile = first.load()["computer_profiles"]["pc"]
    assert all(profile[f"key{index}"] == index for index in range(40))


def test_status_is_not_running_until_start_has_recorded_the_context(kit_root: Path, monkeypatch):
    engine = KoboldEngine(AppPaths.from_root(kit_root))

    class Alive:
        def poll(self):
            return None

    engine.process, engine.mode = Alive(), "starting"
    monkeypatch.setattr(engine, "_ready", lambda: True)
    monkeypatch.setattr(engine, "find_executable", lambda: Path("koboldcpp-launcher.exe"))
    assert engine.status()["state"] == "starting"
    engine.mode = "running"
    assert engine.status()["state"] == "running"


def _engine(monkeypatch, kit_root: Path, fail_above: int, vulkan_kind_log: str = ""):
    engine = KoboldEngine(AppPaths.from_root(kit_root))
    engine.cpu_profile = CpuProfile("AVX2", ("--usecpu",), avx=True, avx2=True)
    attempts: list[tuple[str, int]] = []
    monkeypatch.setattr("security_with_sam.engine.ensure_temporary_storage", lambda: Path("."))

    def launch(mode, timeout):
        size = engine.running_profile().context_size
        attempts.append((mode, size))
        engine.paths.logs.mkdir(parents=True, exist_ok=True)
        log = engine.paths.logs / "koboldcpp.log"
        engine._log_offset = log.stat().st_size if log.is_file() else 0
        with log.open("a", encoding="utf-8") as stream:
            if mode == "vulkan" and vulkan_kind_log:
                stream.write(vulkan_kind_log)  # Fails while loading the backend library, before any model load.
            else:
                stream.write("Loading Text Model: test.gguf\n")
                if size > fail_above:
                    stream.write("ggml_backend_cpu_buffer_type_alloc_buffer: failed to allocate buffer\n")
                elif mode == "vulkan":
                    stream.write("load_tensors: offloaded 29/29 layers to GPU\n")
        ok = size <= fail_above and not (mode == "vulkan" and vulkan_kind_log)
        engine._launch_outcome = "ready" if ok else "exited"
        return ok

    monkeypatch.setattr(engine, "_launch_once", launch)
    monkeypatch.setattr(engine, "stop", lambda: None)
    return engine, attempts


def test_cpu_context_failure_retries_once_with_safe_size(monkeypatch, kit_root: Path):
    engine, attempts = _engine(monkeypatch, kit_root, fail_above=8192)
    engine.memory_profile = MemoryProfile("manual", 32768, 1024)
    engine.start(fallback_profile=MemoryProfile("safe-fallback", 8192, 1024))
    assert attempts == [("cpu", 32768), ("cpu", 8192)]
    assert engine.context_status["requested"] == 32768 and engine.context_status["actual"] == 8192
    assert engine.context_status["fallback"] is True and "retried once" in engine.context_status["reason"]


def test_context_retry_is_bounded_and_reports_failure(monkeypatch, kit_root: Path):
    engine, attempts = _engine(monkeypatch, kit_root, fail_above=1024)
    engine.memory_profile = MemoryProfile("manual", 32768, 1024)
    with pytest.raises(Exception):
        engine.start(fallback_profile=MemoryProfile("safe-fallback", 8192, 1024))
    assert attempts == [("cpu", 32768), ("cpu", 8192)]
    assert engine.context_status["actual"] is None


def test_gpu_context_failure_retries_on_gpu_with_smaller_context(monkeypatch, kit_root: Path):
    engine, attempts = _engine(monkeypatch, kit_root, fail_above=8192)
    engine.memory_profile = MemoryProfile("manual", 16384, 1024)
    engine.start(prefer_vulkan=True, fallback_profile=MemoryProfile("safe-fallback", 8192, 1024))
    assert attempts == [("vulkan", 16384), ("vulkan", 8192)]
    assert engine.acceleration["actual"] == "gpu" and engine.context_status["actual"] == 8192


def test_windows_security_block_does_not_trigger_context_retry_on_gpu(monkeypatch, kit_root: Path):
    blocked = "OSError: [WinError 4551] An Application Control policy has blocked this file\n"
    engine, attempts = _engine(monkeypatch, kit_root, fail_above=65536, vulkan_kind_log=blocked)
    engine.memory_profile = MemoryProfile("manual", 16384, 1024)
    engine.start(prefer_vulkan=True, fallback_profile=MemoryProfile("safe-fallback", 8192, 1024))
    assert attempts == [("vulkan", 16384), ("cpu", 16384)]
    assert engine.acceleration["failure_kind"] == "blocked_by_windows"
    assert engine.context_status["actual"] == 16384 and engine.context_status["fallback"] is False


def test_gpu_library_load_failure_does_not_trigger_context_retry(monkeypatch, kit_root: Path):
    broken = "OSError: [WinError 193] %1 is not a valid Win32 application\n"
    engine, attempts = _engine(monkeypatch, kit_root, fail_above=65536, vulkan_kind_log=broken)
    engine.memory_profile = MemoryProfile("automatic", 8192, 1024)
    engine.start(prefer_vulkan=True, fallback_profile=MemoryProfile("safe-fallback", 2048, 384))
    assert attempts == [("vulkan", 8192), ("cpu", 8192)]
    assert engine.context_status["fallback"] is False


def test_every_context_option_produces_a_launch_argument(kit_root: Path):
    engine = KoboldEngine(AppPaths.from_root(kit_root))
    model = kit_root / "Apps" / "Offline AI" / "Models" / "test.gguf"
    model.write_bytes(b"GGUF")
    (kit_root / "Apps" / "Offline AI" / "koboldcpp-nocuda.exe").write_bytes(b"exe")
    for size in OPTIONS:
        engine.memory_profile = context.profile_for(size, "manual")
        command = engine._command("cpu")
        assert command[command.index("--contextsize") + 1] == str(size)


# Prompt fitting --------------------------------------------------------------------------------

def turns(count: int, words: int = 120) -> list[dict[str, str]]:
    return [{"role": "user" if index % 2 == 0 else "assistant", "content": f"message {index} " + "word " * words} for index in range(count)]


def test_long_history_is_trimmed_newest_first_and_question_is_kept():
    history = turns(40)
    built = build_messages(system_prompt="System.", history=history, question="What now?", context_size=2048, max_output_tokens=384)
    sent = built["messages"]
    assert sent[0]["role"] == "system" and sent[-1] == {"role": "user", "content": "What now?"}
    assert sent[1]["role"] == "user"
    assert built["history_omitted"] > 0 and built["history_sent"] + built["history_omitted"] == 40
    assert sent[-2]["content"] == history[-1]["content"]
    assert sum(estimate_tokens(m["content"]) + 8 for m in sent) <= 2048 - 384


def test_larger_context_sends_more_history():
    history = turns(40)
    sizes = [build_messages(system_prompt="S", history=history, question="Q", context_size=size, max_output_tokens=context.max_output_for(size))["history_sent"] for size in OPTIONS]
    assert sizes == sorted(sizes) and sizes[-1] == 40 and sizes[0] < sizes[-1]


def test_question_larger_than_context_is_rejected_not_truncated():
    with pytest.raises(PromptTooLong):
        build_messages(system_prompt="S", history=[], question="x" * 6000, context_size=2048, max_output_tokens=384)


def test_passages_are_limited_and_only_included_ones_are_returned():
    passages = [{"filename": f"doc{i}.pdf", "page_number": i, "passage": "evidence " * 250} for i in range(4)]
    built = build_messages(system_prompt="Docs.", history=[], question="Q?", context_size=2048, max_output_tokens=384, passages=passages)
    included = built["passages"]
    assert 1 <= len(included) < 4 and included == passages[: len(included)]
    system = built["messages"][0]["content"]
    assert system.count("\nSOURCE ") == len(included) and "UNTRUSTED SOURCE PASSAGES BEGIN" in system
    assert [m["role"] for m in built["messages"]].count("system") == 1
    roomy = build_messages(system_prompt="Docs.", history=[], question="Q?", context_size=16384, max_output_tokens=1024, passages=passages)
    assert len(roomy["passages"]) == 4


def test_exact_token_counter_is_used_when_available():
    calls = []
    built = build_messages(system_prompt="S", history=turns(4, 5), question="Q", context_size=4096, max_output_tokens=768, count_tokens=lambda text: calls.append(text) or 3)
    assert calls and built["history_sent"] == 4
