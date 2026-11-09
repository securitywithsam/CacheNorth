from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
import urllib.request
import uuid
from pathlib import Path

import psutil


def api(base: str, token: str, path: str, method: str = "GET", payload: dict | None = None):
    data = json.dumps(payload or {}).encode() if method != "GET" else None
    headers = {"X-SWS-Token": token}
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(base + path, data=data, method=method, headers=headers)
    with urllib.request.urlopen(request, timeout=120) as response:
        body = response.read().decode("utf-8")
        if "application/x-ndjson" in response.headers.get("Content-Type", ""):
            return [json.loads(line) for line in body.splitlines() if line]
        return json.loads(body)


def launch(root: Path, session: Path):
    runtime = root / "Apps" / "Offline AI" / "Runtime" / "SecurityWithSamOfflineAI.exe"
    session.unlink(missing_ok=True)
    process = subprocess.Popen(
        [str(runtime), "--headless", "--root", str(root), "--session-file", str(session)],
        cwd=runtime.parent,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    deadline = time.monotonic() + 60
    while not session.is_file() and time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Runtime exited early: {process.returncode}")
        time.sleep(0.1)
    details = json.loads(session.read_text(encoding="utf-8"))
    base, token = details["url"].split("/#token=", 1)
    deadline = time.monotonic() + 240
    while time.monotonic() < deadline:
        status = api(base, token, "/api/status")
        if status["engine"]["state"] == "running":
            return process, base, token
        if status["engine"]["state"] == "error":
            raise RuntimeError(status["engine"]["message"])
        time.sleep(0.25)
    raise TimeoutError("Engine did not become ready")


def stop(process: subprocess.Popen, base: str, token: str, session: Path) -> tuple[list[int], bool]:
    api(base, token, "/api/shutdown", "POST", {})
    process.wait(timeout=30)
    deadline = time.monotonic() + 15
    remaining: list[int] = []
    while time.monotonic() < deadline:
        remaining = [
            item.pid for item in psutil.process_iter(["exe"])
            if item.info.get("exe") and str(session.parents[3]).lower() in str(item.info["exe"]).lower()
        ]
        if not remaining and not session.exists():
            break
        time.sleep(0.25)
    return remaining, not session.exists()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    session = root / "Apps" / "Offline AI" / "Data" / "conversation-persistence-session.json"
    marker = f"PERSIST-{uuid.uuid4().hex}"
    result: dict[str, object] = {"marker": marker}
    process = None
    try:
        process, base, token = launch(root, session)
        events = api(base, token, "/api/chat", "POST", {"message": f"Reply with exactly: {marker}", "mode": "general"})
        conversation_id = next(event["conversation_id"] for event in events if event.get("conversation_id"))
        first_cleanup = stop(process, base, token, session)
        process, base, token = launch(root, session)
        chats = api(base, token, "/api/chats")
        messages = api(base, token, f"/api/chats/{conversation_id}")
        second_cleanup = stop(process, base, token, session)
        checks = {
            "conversation_listed_after_restart": any(item.get("id") == conversation_id for item in chats),
            "user_message_persisted": any(marker in item.get("content", "") for item in messages if item.get("role") == "user"),
            "assistant_message_persisted": any(marker in item.get("content", "") for item in messages if item.get("role") == "assistant"),
            "first_cleanup": first_cleanup == ([], True),
            "second_cleanup": second_cleanup == ([], True),
        }
        result.update({"conversation_id": conversation_id, "messages": len(messages), "checks": checks, "passed": all(checks.values())})
    finally:
        if process is not None and process.poll() is None:
            process.kill()
            process.wait(timeout=10)
        session.unlink(missing_ok=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
