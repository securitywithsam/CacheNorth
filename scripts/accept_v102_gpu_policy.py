"""Packaged-runtime acceptance for v1.0.2 CPU-first GPU policy (development stage only, never the USB).

Simulates the field failure by temporarily replacing the stage's Vulkan route DLL with a truncated copy,
which fails at the same KoboldCpp call (ctypes.CDLL(route_path)) as the Smart App Control block.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import time
import urllib.request
import uuid
from pathlib import Path

import psutil

VULKAN_LOAD = "Initializing dynamic library: koboldcpp_vulkan"


def api(base, token, path, method="GET", body=None, job=None, timeout=30):
    headers = {"X-SWS-Token": token, "Content-Type": "application/json"}
    if job:
        headers["X-SWS-Job"] = job
    data = json.dumps(body).encode() if body is not None else (b"{}" if method == "POST" else None)
    request = urllib.request.Request(base + path, data=data, method=method, headers=headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def wait_engine(base, token, timeout=300):
    deadline = time.monotonic() + timeout
    status = {}
    while time.monotonic() < deadline:
        status = api(base, token, "/api/status")
        if status["engine"]["state"] in {"running", "error"}:
            return status
        time.sleep(0.5)
    raise TimeoutError(f"engine did not settle: {status.get('engine')}")


def wait_job(base, token, job_id, timeout=400):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        job = api(base, token, f"/api/jobs/{job_id}")
        if job["state"] in {"complete", "error"}:
            return job
        time.sleep(0.5)
    raise TimeoutError("job did not finish")


def chat(base, token, message="Name three primary colors."):
    request = urllib.request.Request(
        base + "/api/chat",
        data=json.dumps({"message": message, "mode": "general"}).encode(),
        method="POST",
        headers={"X-SWS-Token": token, "Content-Type": "application/json"},
    )
    answer, errors = [], []
    with urllib.request.urlopen(request, timeout=300) as response:
        for line in response:
            event = json.loads(line)
            answer.append(event.get("delta", ""))
            if event.get("error"):
                errors.append(event["error"])
    return {"answer": "".join(answer).strip(), "errors": errors}


def apply_mode(base, token, mode, device=None):
    started = time.monotonic()
    result = api(base, token, "/api/settings", "POST", {"acceleration_mode": mode, "vulkan_device": device, "restart_engine": True})
    job = wait_job(base, token, result["job_id"])
    status = wait_engine(base, token)
    return {"job": job, "engine": status["engine"], "seconds": round(time.monotonic() - started, 1)}


def vulkan_loads(log: Path, offset: int) -> int:
    with log.open("rb") as stream:
        stream.seek(offset)
        return stream.read().decode("utf-8", "replace").count(VULKAN_LOAD)


def managed(root: Path):
    return [
        p.pid for p in psutil.process_iter(["name", "exe"])
        if p.info.get("exe") and str(root).lower() in str(p.info["exe"]).lower()
        and any(t in (p.info.get("name") or "").lower() for t in ("kobold", "securitywithsam"))
    ]


class Backend:
    def __init__(self, root: Path):
        self.root = root
        runtime = root / "Apps" / "Offline AI" / "Runtime" / "SecurityWithSamOfflineAI.exe"
        self.session = root / "Apps" / "Offline AI" / "Data" / f"v102-gpu-{uuid.uuid4().hex[:8]}.json"
        self.process = subprocess.Popen(
            [str(runtime), "--headless", "--root", str(root), "--session-file", str(self.session)],
            cwd=runtime.parent,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        deadline = time.monotonic() + 90
        while not self.session.is_file():
            if self.process.poll() is not None or time.monotonic() > deadline:
                raise RuntimeError("backend did not publish a session")
            time.sleep(0.2)
        self.base, self.token = json.loads(self.session.read_text(encoding="utf-8"))["url"].split("/#token=", 1)

    def shutdown(self):
        api(self.base, self.token, "/api/shutdown", "POST", {})
        self.process.wait(timeout=60)
        deadline = time.monotonic() + 15
        while managed(self.root) and time.monotonic() < deadline:
            time.sleep(0.25)
        return {"exit_code": self.process.returncode, "session_removed": not self.session.exists(), "remaining": managed(self.root)}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-removable", action="store_true", help="Allow running against a removable drive.")
    args = parser.parse_args()
    root = args.root.resolve()
    # These tests write logs, settings, and test chats under the root; keep them off portable drives
    # (where real user data lives) unless explicitly allowed.
    if not args.allow_removable and os.name == "nt" and __import__("ctypes").windll.kernel32.GetDriveTypeW(root.anchor) == 2:
        raise SystemExit(f"{root.anchor} is a removable drive. Run against a development copy, or pass --allow-removable.")
    data = root / "Apps" / "Offline AI" / "Data"
    log = data / "Logs" / "koboldcpp.log"
    route = root / "Apps" / "Offline AI" / "KoboldCpp" / "backend_routes" / "koboldcpp_vulkan" / "koboldcpp_backend.dll"
    original_hash = sha256(route)
    backup = route.with_name(route.name + ".v102-acceptance-original")
    mei_before = len(list(Path(os.environ["TEMP"]).glob("_MEI*")))
    r: dict[str, object] = {"root": str(root), "route_dll_sha256": original_hash}

    backend = Backend(root)
    try:
        start = wait_engine(backend.base, backend.token)
        r["s1_initial"] = start["engine"]["acceleration"]
        gpu = apply_mode(backend.base, backend.token, "auto_vulkan")
        r["s2_auto_gpu"] = {**gpu, "chat": chat(backend.base, backend.token), "perf": api(backend.base, backend.token, "/api/status")["engine"]["last_generation"]}
        settings = api(backend.base, backend.token, "/api/settings")
        r["s2_settings"] = {k: settings.get(k) for k in ("acceleration_mode", "vulkan_verified", "vulkan_devices", "vulkan_failure", "smart_app_control")}
        devices = settings.get("vulkan_devices") or []
        other = next((d for d in devices if "nvidia" not in d["name"].lower()), None)
        if other:
            manual = apply_mode(backend.base, backend.token, "manual_vulkan", other["index"])
            r["s3_manual_other_device"] = {**manual, "requested": other, "chat": chat(backend.base, backend.token)}
        # Simulated library-load failure at the same KoboldCpp call that Windows blocked in the field.
        # The running GPU engine holds the route DLL open, so return to CPU before replacing it.
        r["s3b_cpu_before_simulation"] = apply_mode(backend.base, backend.token, "cpu")
        shutil.copy2(route, backup)
        route.write_bytes(backup.read_bytes()[:120000])
        offset = log.stat().st_size
        failed = apply_mode(backend.base, backend.token, "auto_vulkan")
        r["s4_simulated_failure"] = {**failed, "vulkan_loads": vulkan_loads(log, offset), "chat": chat(backend.base, backend.token)}
        r["s4_settings_failure"] = api(backend.base, backend.token, "/api/settings").get("vulkan_failure")
        r["s4_shutdown"] = backend.shutdown()

        offset = log.stat().st_size
        backend = Backend(root)
        restarted = wait_engine(backend.base, backend.token)
        r["s5_restart_after_failure"] = {"engine": restarted["engine"], "vulkan_loads": vulkan_loads(log, offset)}
        job = uuid.uuid4().hex
        api(backend.base, backend.token, "/api/models/load", "POST", {"filename": "Qwen3-1.7B-Q4_K_M.gguf"}, job)
        switch_job = wait_job(backend.base, backend.token, job)
        switched = wait_engine(backend.base, backend.token)
        r["s6_model_switch_after_failure"] = {"job": switch_job, "engine": switched["engine"], "vulkan_loads": vulkan_loads(log, offset), "chat": chat(backend.base, backend.token)}

        offset = log.stat().st_size
        retry = apply_mode(backend.base, backend.token, "auto_vulkan")
        r["s7_explicit_retry_still_broken"] = {**retry, "vulkan_loads": vulkan_loads(log, offset)}

        shutil.copy2(backup, route)
        backup.unlink()
        recovered = apply_mode(backend.base, backend.token, "auto_vulkan")
        r["s8_restored_dll_gpu"] = {**recovered, "settings_failure": api(backend.base, backend.token, "/api/settings").get("vulkan_failure")}
        cpu = apply_mode(backend.base, backend.token, "cpu")
        r["s9_back_to_cpu"] = cpu
        r["s9_shutdown"] = backend.shutdown()
    finally:
        # Kill first: a live engine holds the route DLL open and would block the restore.
        if backend.process.poll() is None:
            backend.process.kill()
            backend.process.wait(timeout=30)
        deadline = time.monotonic() + 15
        while managed(root) and time.monotonic() < deadline:
            time.sleep(0.25)
        if backup.exists():
            shutil.copy2(backup, route)
            backup.unlink()
    r["route_dll_restored"] = sha256(route) == original_hash
    r["mei_before"], r["mei_after"] = mei_before, len(list(Path(os.environ["TEMP"]).glob("_MEI*")))

    def acc(key):
        return r[key]["engine"]["acceleration"]

    checks = {
        "legacy_shared_setting_starts_cpu": r["s1_initial"]["selected"] == "cpu",
        "auto_gpu_verified_on_gpu": acc("s2_auto_gpu")["actual"] == "gpu" and (acc("s2_auto_gpu")["layers"] or [0])[0] > 0,
        "auto_gpu_generation": bool(r["s2_auto_gpu"]["chat"]["answer"]) and not r["s2_auto_gpu"]["chat"]["errors"],
        "gpu_verified_recorded": r["s2_settings"]["vulkan_verified"] is True and bool(r["s2_settings"]["vulkan_devices"]),
        "manual_device_honored": "s3_manual_other_device" not in r or (acc("s3_manual_other_device")["actual"] == "gpu" and acc("s3_manual_other_device")["device"] in r["s3_manual_other_device"]["requested"]["name"]),
        "failure_falls_back_to_cpu": acc("s4_simulated_failure")["actual"] == "cpu" and acc("s4_simulated_failure")["fallback"] is True,
        "failure_single_attempt": r["s4_simulated_failure"]["vulkan_loads"] == 1,
        "failure_cpu_generation": bool(r["s4_simulated_failure"]["chat"]["answer"]) and not r["s4_simulated_failure"]["chat"]["errors"],
        "failure_remembered": bool(r["s4_settings_failure"]),
        "restart_does_not_retry_gpu": r["s5_restart_after_failure"]["vulkan_loads"] == 0 and r["s5_restart_after_failure"]["engine"]["acceleration"]["actual"] == "cpu" and "paused" in (r["s5_restart_after_failure"]["engine"]["acceleration"]["reason"] or ""),
        "model_switch_does_not_retry_gpu": r["s6_model_switch_after_failure"]["vulkan_loads"] == 0 and r["s6_model_switch_after_failure"]["job"]["state"] == "complete" and bool(r["s6_model_switch_after_failure"]["chat"]["answer"]),
        "explicit_retry_tries_once": r["s7_explicit_retry_still_broken"]["vulkan_loads"] == 1 and acc("s7_explicit_retry_still_broken")["actual"] == "cpu",
        "recovers_after_restore": acc("s8_restored_dll_gpu")["actual"] == "gpu" and r["s8_restored_dll_gpu"]["settings_failure"] is None,
        "back_to_cpu": acc("s9_back_to_cpu")["actual"] == "cpu",
        "clean_shutdowns": all(r[k]["exit_code"] == 0 and r[k]["session_removed"] and not r[k]["remaining"] for k in ("s4_shutdown", "s9_shutdown")),
        "no_new_mei": r["mei_after"] <= r["mei_before"],
        "route_dll_restored": r["route_dll_restored"],
    }
    r["checks"], r["passed"] = checks, all(checks.values())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(r, indent=2), encoding="utf-8")
    print(json.dumps(checks, indent=2))
    return 0 if r["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
