from __future__ import annotations

import argparse
import json
import os
import subprocess
import threading
import time
import urllib.request
from pathlib import Path

import psutil


def api(base: str, token: str, path: str, method: str = "GET", payload: dict | None = None):
    data = json.dumps(payload or {}).encode() if method != "GET" else None
    headers = {"X-SWS-Token": token}
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(base + path, data=data, method=method, headers=headers)
    with urllib.request.urlopen(request, timeout=360) as response:
        body = response.read().decode("utf-8")
    return json.loads(body) if body else {}


def temp_state() -> dict[str, object]:
    temp = Path(os.environ["TEMP"])
    entries = []
    for directory in temp.glob("_MEI*"):
        if directory.is_dir() and (directory / "kcpp_adapters").exists():
            files = [item for item in directory.rglob("*") if item.is_file()]
            entries.append({"path": str(directory), "bytes": sum(item.stat().st_size for item in files)})
    return {"paths": sorted(item["path"] for item in entries), "bytes": sum(int(item["bytes"]) for item in entries)}


def start_runtime(root: Path, session_name: str, environment: dict[str, str] | None = None):
    executable = root / "Apps" / "Offline AI" / "Runtime" / "SecurityWithSamOfflineAI.exe"
    session = root / "Apps" / "Offline AI" / "Data" / session_name
    session.unlink(missing_ok=True)
    process = subprocess.Popen(
        [str(executable), "--headless", "--root", str(root), "--session-file", str(session)],
        cwd=executable.parent,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        env=environment,
    )
    deadline = time.monotonic() + 60
    while not session.is_file() and time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Runtime exited with {process.returncode}")
        time.sleep(0.2)
    payload = json.loads(session.read_text(encoding="utf-8"))
    base, token = payload["url"].split("/#token=", 1)
    deadline = time.monotonic() + 240
    status = {}
    while time.monotonic() < deadline:
        status = api(base, token, "/api/status")
        if status["engine"]["state"] in {"running", "error"}:
            break
        time.sleep(0.25)
    if status.get("engine", {}).get("state") != "running":
        raise RuntimeError(f"Engine failed: {status}")
    return process, session, base, token, status


def remaining(root: Path) -> list[int]:
    root_text = str(root).casefold()
    return [
        item.pid for item in psutil.process_iter(["name", "exe", "cmdline"])
        if root_text in (str(item.info.get("exe") or "") + " " + " ".join(item.info.get("cmdline") or [])).casefold()
        and any(name in (item.info.get("name") or "").casefold() for name in ("kobold", "securitywithsam"))
    ]


def wait_cleanup(root: Path, session: Path, timeout: float = 20) -> tuple[list[int], bool]:
    deadline = time.monotonic() + timeout
    active = remaining(root)
    while (active or session.exists()) and time.monotonic() < deadline:
        time.sleep(0.25)
        active = remaining(root)
    return active, not session.exists()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    baseline = temp_state()
    result: dict[str, object] = {"baseline_temp": baseline}

    process = None
    session = None
    kobold_dir = root / "Apps" / "Offline AI" / "KoboldCpp"
    vulkan_files = sorted(kobold_dir.glob("koboldcpp_vulkan*.dll"))
    disabled_files = [(path, path.with_suffix(path.suffix + ".failure-test-disabled")) for path in vulkan_files]
    try:
        failure_environment = os.environ.copy()
        failure_environment["VK_ICD_FILENAMES"] = str(root / "missing-vulkan-driver-manifest.json")
        failure_environment["VK_DRIVER_FILES"] = str(root / "missing-vulkan-driver-manifest.json")
        process, session, base, token, initial = start_runtime(root, "failure-recovery-session.json", failure_environment)
        # Leave invalid files at the exact DLL names so Windows cannot continue its DLL
        # search and load another Vulkan variant from elsewhere on the development host.
        for original, disabled in disabled_files:
            original.replace(disabled)
            original.write_bytes(b"CacheNorth intentional Vulkan load failure test")
        response = api(base, token, "/api/settings", "POST", {"acceleration_mode": "auto_vulkan", "vulkan_device": None, "restart_engine": True})
        deadline = time.monotonic() + 240
        job = {}
        while time.monotonic() < deadline:
            job = api(base, token, f"/api/jobs/{response['job_id']}")
            if job["state"] in {"complete", "error"}:
                break
            time.sleep(0.25)
        recovered = api(base, token, "/api/status")
        for original, disabled in disabled_files:
            original.unlink(missing_ok=True)
            disabled.replace(original)
        api(base, token, "/api/shutdown", "POST", {})
        process.wait(timeout=30)
        active, session_removed = wait_cleanup(root, session)
        result["failure_recovery"] = {
            "initial": initial["engine"], "job": job, "recovered": recovered["engine"],
            "exit_code": process.returncode, "remaining": active, "session_removed": session_removed,
        }
    finally:
        for original, disabled in disabled_files:
            if disabled.exists():
                original.unlink(missing_ok=True)
                disabled.replace(original)
        if process is not None and process.poll() is None:
            process.kill(); process.wait(timeout=10)
        if session is not None:
            session.unlink(missing_ok=True)
    result["temp_after_failure_recovery"] = temp_state()

    process = None
    session = None
    stream_started = threading.Event()
    stream_finished = threading.Event()
    stream_result: dict[str, object] = {}
    try:
        process, session, base, token, initial = start_runtime(root, "active-generation-session.json")
        cpu_restart = api(base, token, "/api/settings", "POST", {"acceleration_mode": "cpu", "vulkan_device": None, "restart_engine": True})
        deadline = time.monotonic() + 240
        while time.monotonic() < deadline:
            job = api(base, token, f"/api/jobs/{cpu_restart['job_id']}")
            if job["state"] in {"complete", "error"}:
                break
            time.sleep(0.25)
        initial = api(base, token, "/api/status")
        def generate() -> None:
            request = urllib.request.Request(
                base + "/api/chat",
                data=json.dumps({"message": "Write a detailed 1,000-word emergency preparedness guide.", "mode": "general"}).encode(),
                method="POST",
                headers={"X-SWS-Token": token, "Content-Type": "application/json"},
            )
            try:
                with urllib.request.urlopen(request, timeout=360) as response:
                    for line in response:
                        if line.strip():
                            stream_started.set()
                stream_result["ended"] = True
            except Exception as exc:
                stream_result["error"] = f"{type(exc).__name__}: {exc}"
            finally:
                stream_finished.set()
        thread = threading.Thread(target=generate, daemon=True)
        thread.start()
        if not stream_started.wait(60):
            raise TimeoutError("Generation did not begin")
        shutdown_started = time.perf_counter()
        try:
            api(base, token, "/api/shutdown", "POST", {})
        except OSError:
            pass
        process.wait(timeout=30)
        thread.join(timeout=10)
        active, session_removed = wait_cleanup(root, session)
        result["active_generation_shutdown"] = {
            "initial": initial["engine"], "stream": stream_result,
            "shutdown_seconds": round(time.perf_counter() - shutdown_started, 3),
            "exit_code": process.returncode, "remaining": active, "session_removed": session_removed,
        }
    finally:
        if process is not None and process.poll() is None:
            process.kill(); process.wait(timeout=10)
        if session is not None:
            session.unlink(missing_ok=True)
    result["temp_after_active_shutdown"] = temp_state()
    checks = {
        "failure_recovered_to_cpu": result["failure_recovery"]["recovered"]["backend"] == "cpu",
        "failure_cleanup": not result["failure_recovery"]["remaining"] and result["failure_recovery"]["session_removed"],
        "active_shutdown_cleanup": not result["active_generation_shutdown"]["remaining"] and result["active_generation_shutdown"]["session_removed"],
        "no_new_temp_after_failure": result["temp_after_failure_recovery"] == baseline,
        "no_new_temp_after_active_shutdown": result["temp_after_active_shutdown"] == baseline,
    }
    result["checks"] = checks
    result["passed"] = all(checks.values())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
