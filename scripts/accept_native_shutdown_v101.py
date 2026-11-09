from __future__ import annotations

import argparse
import json
import subprocess
import time
import urllib.request
from pathlib import Path

import psutil


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    launcher = root / "Launch CacheNorth.exe"
    session = root / "Apps" / "Offline AI" / "Data" / "cache-north-session.json"
    session.unlink(missing_ok=True)
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 6  # SW_SHOWMINIMIZED: create the real native window without taking over the desktop.
    process = subprocess.Popen([str(launcher)], cwd=launcher.parent, startupinfo=startup)
    result: dict[str, object] = {"root": str(root), "launcher_pid": process.pid, "window_mode": "minimized"}
    try:
        deadline = time.monotonic() + 60
        while not session.is_file() and time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f"Native launcher exited before session creation: {process.returncode}")
            time.sleep(0.2)
        session_data = json.loads(session.read_text(encoding="utf-8"))
        base, token = session_data["url"].split("/#token=", 1)
        headers = {"X-SWS-Token": token}
        status = {}
        deadline = time.monotonic() + 240
        while time.monotonic() < deadline:
            with urllib.request.urlopen(urllib.request.Request(base + "/api/status", headers=headers), timeout=10) as response:
                status = json.load(response)
            if status["engine"]["state"] == "error" or (
                status["engine"]["state"] == "running" and status["engine"]["backend"] == "cpu"
            ):
                break
            time.sleep(0.5)
        if status.get("engine", {}).get("state") != "running":
            raise RuntimeError(f"Native packaged engine did not become ready: {status}")
        request = urllib.request.Request(base + "/api/shutdown", data=b"{}", method="POST", headers=headers)
        try:
            urllib.request.urlopen(request, timeout=10).close()
        except OSError:
            pass
        process.wait(timeout=30)
        deadline = time.monotonic() + 15
        remaining: list[dict[str, object]] = []
        while time.monotonic() < deadline:
            remaining = [
                {"pid": item.pid, "name": item.info.get("name")}
                for item in psutil.process_iter(["name", "exe"])
                if item.info.get("exe") and str(root).lower() in str(item.info["exe"]).lower()
            ]
            if not remaining:
                break
            time.sleep(0.25)
        result.update({
            "engine_before_shutdown": status["engine"],
            "launcher_exit_code": process.returncode,
            "session_file_removed": not session.exists(),
            "remaining_processes": remaining,
            "passed": process.returncode == 0 and not session.exists() and not remaining,
        })
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=10)
        session.unlink(missing_ok=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
