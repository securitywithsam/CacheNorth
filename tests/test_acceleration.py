from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from security_with_sam import acceleration
from security_with_sam.acceleration import (
    classify_failure,
    library_load_stalled,
    load_profile,
    parse_vulkan_run,
    plan_start,
    start_engine,
)
from security_with_sam.config import AppPaths
from security_with_sam.engine import CpuProfile, KoboldEngine, quiet_child_error_dialogs
from security_with_sam.settings import SettingsStore

# Verbatim excerpts from the field laptop's koboldcpp.log (2026-11-04).
BLOCKED_LOG = """Initializing dynamic library: koboldcpp_vulkan.dll
Traceback (most recent call last):
  File "koboldcpp.py", line 1045, in init_library
    common_backend_handle = ctypes.CDLL(route_path)
OSError: [WinError 4551] An Application Control policy has blocked this file
[16052] Failed to execute script 'koboldcpp' due to unhandled exception!
"""
STALLED_LOG = """Detected Available RAM: 23277 MB
Initializing dynamic library: koboldcpp_vulkan.dll
"""
VULKAN_OK_LOG = """ggml_vulkan: Found 1 Vulkan devices:
ggml_vulkan: 0 = Intel(R) UHD Graphics (Intel Corporation) | uma: 1 | fp16: 1 | bf16: 0
llama_prepare_model_devices: using device Vulkan0 (Intel(R) UHD Graphics) (unknown id) - 15407 MiB free
load_tensors: offloaded 29/29 layers to GPU
"""
CPU_ONLY_LOG = "load_tensors: offloaded 0/37 layers to GPU\n"
AVX2 = CpuProfile("AVX2", ("--usecpu",), avx=True, avx2=True)


def test_real_laptop_policy_block_is_classified_as_windows_security():
    kind, message = classify_failure(BLOCKED_LOG)
    assert kind == "blocked_by_windows"
    assert "not a hardware fault" in message and "does not bypass" in message


def test_library_load_stall_is_detected_and_classified():
    assert library_load_stalled(STALLED_LOG)
    assert not library_load_stalled(VULKAN_OK_LOG)
    assert classify_failure(STALLED_LOG, stalled=True)[0] == "library_load_stalled"


def test_missing_driver_and_timeout_are_distinguished():
    assert classify_failure("OSError: [WinError 126] The specified module could not be found")[0] == "no_vulkan_device"
    assert classify_failure("Loading Text Model", timed_out=True)[0] == "timeout"


def test_vulkan_run_reports_device_and_verified_offload():
    details = parse_vulkan_run(VULKAN_OK_LOG)
    assert details["devices"] == [{"index": 0, "name": "Intel(R) UHD Graphics (Intel Corporation)"}]
    assert details["device"] == "Intel(R) UHD Graphics"
    assert details["layers"] == [29, 29]
    assert parse_vulkan_run(CPU_ONLY_LOG)["layers"] == [0, 37]


def test_legacy_shared_gpu_setting_does_not_enable_gpu_on_any_computer(tmp_path: Path):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"prefer_vulkan": True, "acceleration_mode": "auto_vulkan"}), encoding="utf-8")
    assert load_profile(SettingsStore(path), "laptop")["acceleration_mode"] == "cpu"


def test_gpu_choice_is_saved_per_computer_and_neutralizes_legacy_keys(tmp_path: Path):
    store = SettingsStore(tmp_path / "settings.json")
    store.save({"acceleration_mode": "auto_vulkan"})
    store.update_profile("desktop", {"acceleration_mode": "manual_vulkan", "vulkan_device": 1})
    assert load_profile(store, "desktop")["acceleration_mode"] == "manual_vulkan"
    assert load_profile(store, "desktop")["vulkan_device"] == 1
    assert load_profile(store, "laptop")["acceleration_mode"] == "cpu"
    raw = json.loads((tmp_path / "settings.json").read_text(encoding="utf-8"))
    assert raw["acceleration_mode"] == "cpu" and raw["prefer_vulkan"] is False


def test_plan_start_respects_failure_memory_and_smart_app_control():
    profile = {"acceleration_mode": "auto_vulkan", "vulkan_device": None, "vulkan_failure": None, "vulkan_verified": False}
    assert plan_start({**profile, "acceleration_mode": "cpu"}, "off", False)[0] is False
    assert plan_start(profile, "off", False)[0] is True
    skipped = plan_start(profile, "on", False)
    assert skipped[0] is False and "Smart App Control" in skipped[2]
    assert plan_start({**profile, "vulkan_verified": True}, "on", False)[0] is True
    assert plan_start(profile, "on", True)[0] is True
    failed = {**profile, "vulkan_failure": {"kind": "blocked_by_windows", "message": "Blocked."}}
    assert plan_start(failed, "off", False)[0] is False
    assert plan_start(failed, "off", True)[0] is True
    manual = {**profile, "acceleration_mode": "manual_vulkan", "vulkan_device": 2}
    assert plan_start(manual, "on", False) == (True, 2, None)


class FakeEngine:
    def __init__(self, outcome: str):
        self.outcome = outcome
        self.attempts: list[bool] = []
        self.vulkan_device = None
        self.acceleration: dict[str, object] = {}

    def start(self, prefer_vulkan=False, timeout=180.0, selected_mode=None, note=None, **_context):
        self.attempts.append(prefer_vulkan)
        if prefer_vulkan and self.outcome == "blocked":
            self.acceleration = {"actual": "cpu", "fallback": True, "failure_kind": "blocked_by_windows", "reason": "Blocked.", "devices": []}
        elif prefer_vulkan:
            self.acceleration = {"actual": "gpu", "failure_kind": None, "devices": [{"index": 0, "name": "GPU"}]}
        else:
            self.acceleration = {"actual": "cpu", "failure_kind": None, "reason": note}


def test_blocked_gpu_is_attempted_once_then_cpu_until_user_retries(tmp_path: Path):
    store = SettingsStore(tmp_path / "settings.json")
    store.update_profile("laptop", {"acceleration_mode": "auto_vulkan"})
    engine = FakeEngine("blocked")
    start_engine(engine, store, machine="laptop", smart_app_control="off")
    start_engine(engine, store, machine="laptop", smart_app_control="off")
    start_engine(engine, store, machine="laptop", smart_app_control="off")
    assert engine.attempts == [True, False, False]
    assert load_profile(store, "laptop")["vulkan_failure"]["kind"] == "blocked_by_windows"
    assert "paused" in engine.acceleration["reason"]
    start_engine(engine, store, machine="laptop", smart_app_control="off", explicit=True)
    assert engine.attempts[-1] is True


def test_successful_gpu_start_records_devices_and_clears_failure(tmp_path: Path):
    store = SettingsStore(tmp_path / "settings.json")
    store.update_profile("desktop", {"acceleration_mode": "auto_vulkan", "vulkan_failure": {"kind": "timeout", "message": "x"}})
    start_engine(FakeEngine("ok"), store, machine="desktop", smart_app_control="off", explicit=True)
    profile = load_profile(store, "desktop")
    assert profile["vulkan_failure"] is None and profile["vulkan_verified"] is True
    assert profile["vulkan_devices"] == [{"index": 0, "name": "GPU"}]


def _engine_with_log(monkeypatch, kit_root: Path, vulkan_log: str, vulkan_ready: bool) -> tuple[KoboldEngine, list[str]]:
    engine = KoboldEngine(AppPaths.from_root(kit_root))
    engine.cpu_profile = AVX2
    attempts: list[str] = []
    monkeypatch.setattr("security_with_sam.engine.ensure_temporary_storage", lambda: Path("."))

    def launch(mode, timeout):
        attempts.append(mode)
        engine.paths.logs.mkdir(parents=True, exist_ok=True)
        log = engine.paths.logs / "koboldcpp.log"
        engine._log_offset = log.stat().st_size if log.is_file() else 0
        with log.open("a", encoding="utf-8") as stream:
            stream.write(vulkan_log if mode == "vulkan" else CPU_ONLY_LOG)
        engine._launch_outcome = "ready" if (mode == "cpu" or vulkan_ready) else "exited"
        return engine._launch_outcome == "ready"

    monkeypatch.setattr(engine, "_launch_once", launch)
    monkeypatch.setattr(engine, "stop", lambda: None)
    return engine, attempts


def test_engine_reports_windows_block_and_runs_cpu(monkeypatch, kit_root: Path):
    engine, attempts = _engine_with_log(monkeypatch, kit_root, BLOCKED_LOG, vulkan_ready=False)
    engine.start(prefer_vulkan=True, timeout=0.01)
    assert attempts == ["vulkan", "cpu"]
    assert engine.backend == "cpu"
    assert engine.acceleration["actual"] == "cpu"
    assert engine.acceleration["fallback"] is True
    assert engine.acceleration["failure_kind"] == "blocked_by_windows"


def test_engine_never_reports_gpu_when_no_layers_are_offloaded(monkeypatch, kit_root: Path):
    engine, _attempts = _engine_with_log(monkeypatch, kit_root, CPU_ONLY_LOG, vulkan_ready=True)
    engine.start(prefer_vulkan=True, timeout=0.01)
    assert engine.acceleration["actual"] == "cpu"
    assert "offloaded no model layers" in engine.acceleration["reason"]


def test_engine_reports_verified_gpu(monkeypatch, kit_root: Path):
    engine, _attempts = _engine_with_log(monkeypatch, kit_root, VULKAN_OK_LOG, vulkan_ready=True)
    engine.start(prefer_vulkan=True, timeout=0.01)
    assert engine.acceleration["actual"] == "gpu"
    assert engine.acceleration["device"] == "Intel(R) UHD Graphics"
    assert engine.acceleration["layers"] == [29, 29]


@pytest.mark.skipif(sys.platform != "win32", reason="Windows job object and process launch")
def test_real_process_stuck_loading_gpu_library_is_abandoned_and_cleaned_up(monkeypatch, kit_root: Path, tmp_path: Path):
    script = tmp_path / "fake_kobold.py"
    script.write_text(
        "import sys, time\nprint('Initializing dynamic library: koboldcpp_vulkan.dll', flush=True)\ntime.sleep(120)\n",
        encoding="utf-8",
    )
    engine = KoboldEngine(AppPaths.from_root(kit_root))
    engine.cpu_profile = AVX2
    monkeypatch.setattr("security_with_sam.engine.LIBRARY_LOAD_STALL_SECONDS", 1.0)
    monkeypatch.setattr(engine, "_command", lambda mode: [sys.executable, "-I", str(script)])
    monkeypatch.setattr(engine, "find_executable", lambda: Path(sys.executable))
    assert engine._launch_once("vulkan", timeout=30) is False
    assert engine._launch_outcome == "stalled"
    process = engine.process
    engine.stop()
    assert process.poll() is not None


@pytest.mark.skipif(sys.platform != "win32", reason="Windows error mode")
def test_child_processes_inherit_quiet_error_mode_and_parent_mode_is_restored():
    import ctypes

    probe = "import ctypes; print(ctypes.windll.kernel32.GetErrorMode())"
    before = ctypes.windll.kernel32.GetErrorMode()
    with quiet_child_error_dialogs():
        inherited = int(subprocess.run([sys.executable, "-I", "-c", probe], capture_output=True, text=True, check=True).stdout)
    assert inherited & 0x0001 and inherited & 0x0002 and inherited & 0x8000
    assert ctypes.windll.kernel32.GetErrorMode() == before


def test_machine_id_is_stable_and_not_the_raw_guid():
    first = acceleration.machine_id()
    assert first == acceleration.machine_id()
    assert len(first) == 16 and all(c in "0123456789abcdef" for c in first)
