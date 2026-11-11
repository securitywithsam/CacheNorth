from __future__ import annotations

import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

from security_with_sam.config import AppPaths, ensure_temporary_storage
from security_with_sam.engine import CpuProfile, KoboldEngine, detect_cpu_profile, find_free_port, select_cpu_threads, select_memory_profile
from security_with_sam.windows_job import assign_kill_on_close, close_job


def test_memory_profiles_for_8_16_and_32_gib():
    assert select_memory_profile(8 * 1024**3).context_size == 2048
    assert select_memory_profile(16 * 1024**3).context_size == 4096
    assert select_memory_profile(32 * 1024**3).context_size == 8192


def test_engine_password_cannot_be_parsed_as_an_option(kit_root: Path):
    engine = KoboldEngine(AppPaths.from_root(kit_root))
    assert engine.password.startswith("sws_")
    assert not engine.password.startswith("-")


def test_unpacked_koboldcpp_runtime_is_preferred(kit_root: Path):
    product = kit_root / "Apps" / "Offline AI"
    one_file = product / "koboldcpp-nocuda.exe"
    unpacked = product / "KoboldCpp" / "koboldcpp-launcher.exe"
    one_file.write_bytes(b"legacy")
    unpacked.parent.mkdir(parents=True)
    unpacked.write_bytes(b"unpacked")
    engine = KoboldEngine(AppPaths.from_root(kit_root))
    assert engine.find_executable() == unpacked
    assert engine.runtime_layout() == "unpacked"


def test_one_file_koboldcpp_remains_a_compatibility_fallback(kit_root: Path):
    executable = kit_root / "Apps" / "Offline AI" / "koboldcpp-nocuda.exe"
    executable.write_bytes(b"legacy")
    engine = KoboldEngine(AppPaths.from_root(kit_root))
    assert engine.find_executable() == executable
    assert engine.runtime_layout() == "one-file"


def test_model_switch_clears_prior_performance(kit_root: Path):
    model = kit_root / "Apps" / "Offline AI" / "Models" / "replacement.gguf"
    model.parent.mkdir(parents=True, exist_ok=True)
    model.write_bytes(b"GGUF")
    engine = KoboldEngine(AppPaths.from_root(kit_root))
    engine.last_generation = {"tokens_per_second": 12.0}
    engine.set_model(model.name)
    assert engine.last_generation is None


def test_avx2_cpu_mode():
    profile = detect_cpu_profile(["sse3", "avx", "avx2"])
    assert profile.flags == ("--usecpu",)
    assert profile.mode == "AVX2"


def test_avx1_compatibility_mode():
    profile = detect_cpu_profile(["sse3", "avx"])
    assert profile.flags == ("--usecpu", "--noavx2")
    assert profile.mode.startswith("AVX1")


def test_non_avx_failsafe_mode():
    profile = detect_cpu_profile(["sse3", "ssse3"])
    assert profile.flags == ("--usecpu", "--noavx2", "--failsafe")
    assert profile.mode == "x64 failsafe"


def test_cpu_thread_selection_uses_physical_cores_conservatively():
    assert select_cpu_threads(2) == 2
    assert select_cpu_threads(4) == 4
    assert select_cpu_threads(8) == 7
    assert select_cpu_threads(32) == 12


@pytest.mark.skipif(sys.platform != "win32", reason="Windows backend launch environment")
def test_windows_launch_environment_skips_broken_duplicate_cpu_probe(kit_root: Path):
    engine = KoboldEngine(AppPaths.from_root(kit_root))
    assert engine._launch_environment()["PROCESSOR_ARCHITECTURE"] == "x64"


def test_bundled_cpu_probe_selects_avx2(monkeypatch, tmp_path: Path):
    helper = tmp_path / "cache-north-cpuinfo.exe"
    helper.write_bytes(b"probe")

    class Result:
        stdout = '{"avx":1,"avx2":1}'

    monkeypatch.setattr("security_with_sam.engine.subprocess.run", lambda *args, **kwargs: Result())
    profile = detect_cpu_profile(helper_path=helper)
    assert profile.mode == "AVX2"
    assert profile.flags == ("--usecpu",)


def test_free_port_is_available_for_loopback_binding():
    port = find_free_port()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", port))


def test_vulkan_failure_falls_back_to_cpu_once(monkeypatch, kit_root: Path):
    engine = KoboldEngine(AppPaths.from_root(kit_root))
    attempts = []
    monkeypatch.setattr("security_with_sam.engine.ensure_temporary_storage", lambda: Path("."))
    monkeypatch.setattr(
        "security_with_sam.engine.detect_cpu_profile",
        lambda: CpuProfile("AVX2", ("--usecpu",), avx=True, avx2=True),
    )
    monkeypatch.setattr(engine, "_launch_once", lambda mode, timeout: attempts.append(mode) or mode == "cpu")
    engine.start(prefer_vulkan=True, timeout=0.01)
    assert attempts == ["vulkan", "cpu"]
    assert engine.backend == "cpu"


def test_cpu_baseline_has_one_start_attempt(monkeypatch, kit_root: Path):
    engine = KoboldEngine(AppPaths.from_root(kit_root))
    attempts = []
    monkeypatch.setattr("security_with_sam.engine.ensure_temporary_storage", lambda: Path("."))
    monkeypatch.setattr(
        "security_with_sam.engine.detect_cpu_profile",
        lambda: CpuProfile("AVX2", ("--usecpu",), avx=True, avx2=True),
    )
    monkeypatch.setattr(engine, "_launch_once", lambda mode, timeout: attempts.append(mode) or True)
    engine.start(prefer_vulkan=False, timeout=0.01)
    assert attempts == ["cpu"]


def test_stop_waits_for_direct_process_before_releasing_job(monkeypatch, kit_root: Path):
    events = []

    class Process:
        def poll(self):
            return None

        def terminate(self):
            events.append("terminate")

        def wait(self, timeout):
            events.append(f"wait:{timeout}")

    engine = KoboldEngine(AppPaths.from_root(kit_root))
    engine.process = Process()
    engine._job_handle = 123
    monkeypatch.setattr("security_with_sam.engine.close_job", lambda handle: events.append(f"close_job:{handle}"))
    engine.stop()
    assert events == ["terminate", "wait:8", "close_job:123"]


def test_final_cpu_failure_is_reported_without_restart_loop(monkeypatch, kit_root: Path):
    engine = KoboldEngine(AppPaths.from_root(kit_root))
    attempts = []
    monkeypatch.setattr("security_with_sam.engine.ensure_temporary_storage", lambda: Path("."))
    monkeypatch.setattr(
        "security_with_sam.engine.detect_cpu_profile",
        lambda: CpuProfile("AVX2", ("--usecpu",), avx=True, avx2=True),
    )
    monkeypatch.setattr(engine, "_launch_once", lambda mode, timeout: attempts.append(mode) or False)
    with pytest.raises(RuntimeError, match="will not retry automatically"):
        engine.start(prefer_vulkan=False, timeout=0.01)
    assert attempts == ["cpu"]
    assert engine.mode == "error"


def test_temporary_storage_failure_is_visible_in_engine_status(monkeypatch, kit_root: Path):
    engine = KoboldEngine(AppPaths.from_root(kit_root))
    monkeypatch.setattr(
        "security_with_sam.engine.ensure_temporary_storage",
        lambda: (_ for _ in ()).throw(RuntimeError("Windows temporary storage is unavailable.")),
    )
    with pytest.raises(RuntimeError, match="temporary storage is unavailable"):
        engine.start()
    assert engine.mode == "error"
    assert "temporary storage" in engine.message


def test_low_temporary_storage_has_clear_error(monkeypatch, tmp_path: Path):
    class Usage:
        total = 1024
        used = 900
        free = 124

    monkeypatch.setattr("security_with_sam.config.tempfile.gettempdir", lambda: str(tmp_path))
    monkeypatch.setattr("security_with_sam.config.shutil.disk_usage", lambda _path: Usage())
    with pytest.raises(RuntimeError, match="temporary storage has only"):
        ensure_temporary_storage(512)


@pytest.mark.skipif(sys.platform != "win32", reason="Windows job object test")
def test_windows_job_closes_owned_child():
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    handle = assign_kill_on_close(int(child._handle))  # type: ignore[attr-defined]
    if handle is None:
        child.terminate()
        child.wait(timeout=5)
        pytest.skip("Nested job assignment is unavailable in this test host")
    close_job(handle)
    deadline = time.monotonic() + 5
    while child.poll() is None and time.monotonic() < deadline:
        time.sleep(0.05)
    assert child.poll() is not None
