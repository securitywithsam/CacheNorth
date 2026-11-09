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


def request_json(base: str, token: str, path: str, method: str = "GET", payload: dict | None = None, job: str | None = None):
    data = json.dumps(payload or {}).encode() if method != "GET" else None
    headers = {"X-SWS-Token": token}
    if data is not None:
        headers["Content-Type"] = "application/json"
    if job:
        headers["X-SWS-Job"] = job
    request = urllib.request.Request(base + path, data=data, method=method, headers=headers)
    with urllib.request.urlopen(request, timeout=360) as response:
        content_type = response.headers.get("Content-Type", "")
        body = response.read().decode("utf-8")
    if "application/x-ndjson" in content_type:
        return [json.loads(line) for line in body.splitlines() if line]
    return json.loads(body)


def wait_engine(base: str, token: str, timeout: float = 240) -> dict:
    deadline = time.monotonic() + timeout
    status = {}
    while time.monotonic() < deadline:
        status = request_json(base, token, "/api/status")
        if status["engine"]["state"] in {"running", "error"}:
            return status
        time.sleep(0.4)
    raise TimeoutError(f"Engine readiness timeout: {status}")


def chat(base: str, token: str, message: str, mode: str = "general") -> dict:
    events = request_json(base, token, "/api/chat", "POST", {"message": message, "mode": mode})
    answer = "".join(str(event.get("delta", "")) for event in events).strip()
    errors = [event["error"] for event in events if event.get("error")]
    sources = next((event.get("sources", []) for event in events if "sources" in event), [])
    return {"answer": answer, "errors": errors, "sources": sources, "done": any(event.get("done") for event in events)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    runtime = root / "Apps" / "Offline AI" / "Runtime" / "SecurityWithSamOfflineAI.exe"
    session = root / "Apps" / "Offline AI" / "Data" / "v101-acceptance-session.json"
    session.unlink(missing_ok=True)
    process = subprocess.Popen(
        [str(runtime), "--headless", "--root", str(root), "--session-file", str(session)],
        cwd=runtime.parent,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    result: dict[str, object] = {"root": str(root), "actual_packaged_runtime": True}
    try:
        deadline = time.monotonic() + 60
        while not session.is_file() and time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f"Packaged runtime exited with {process.returncode}")
            time.sleep(0.2)
        session_data = json.loads(session.read_text(encoding="utf-8"))
        base, token = session_data["url"].split("/#token=", 1)
        initial = wait_engine(base, token)
        models = request_json(base, token, "/api/models")
        library = request_json(base, token, "/api/library")
        maps = request_json(base, token, "/api/maps")
        guides = request_json(base, token, "/api/guides")
        runs = []
        runs.append({"model": models["selected"], "chat": chat(base, token, "Explain the difference between RAM and storage in two sentences.")})
        for filename in ("Qwen3-1.7B-Q4_K_M.gguf", "Qwen3-4B-Q4_K_M.gguf", "Qwen3.5-4B-Q4_K_M.gguf"):
            job_id = uuid.uuid4().hex
            switch = request_json(base, token, "/api/models/load", "POST", {"filename": filename}, job_id)
            deadline = time.monotonic() + 240
            job = {}
            while time.monotonic() < deadline:
                job = request_json(base, token, f"/api/jobs/{switch['job_id']}")
                if job["state"] in {"complete", "error"}:
                    break
                time.sleep(0.5)
            status = wait_engine(base, token)
            runs.append({
                "model": filename,
                "switch_job": job,
                "engine": status["engine"],
                "chat": chat(base, token, "Reply with exactly: MODEL SWITCH OK"),
            })
        refresh_job = uuid.uuid4().hex
        refresh = request_json(base, token, "/api/refresh-all", "POST", {}, refresh_job)
        grounded = chat(base, token, "When does the Cedar County warming center open and what should residents bring?", "documents")
        final_status = request_json(base, token, "/api/status")
        result.update({
            "initial_engine": initial["engine"],
            "models": models,
            "archives": len(library["archives"]),
            "maps": len(maps["files"]),
            "guides": len(guides["files"]),
            "runs": runs,
            "refresh": refresh,
            "grounded": grounded,
            "final_engine": final_status["engine"],
        })
        request_json(base, token, "/api/shutdown", "POST", {})
        process.wait(timeout=30)
        deadline = time.monotonic() + 15
        remaining = []
        while time.monotonic() < deadline:
            remaining = [
                item.pid for item in psutil.process_iter(["name", "exe"])
                if item.info.get("exe") and str(root).lower() in str(item.info["exe"]).lower()
                and any(term in (item.info.get("name") or "").lower() for term in ("kobold", "securitywithsam"))
            ]
            if not remaining:
                break
            time.sleep(0.25)
        checks = {
            "avx2_optimized": initial["system"]["cpu_mode"] == "AVX2" and initial["engine"]["threads"] == 7,
            "three_models": len(models["models"]) == 3,
            "accurate_qwen3_4b_label": next(item["title"] for item in models["models"] if item["name"] == "Qwen3-4B-Q4_K_M.gguf") == "Qwen3 4B Instruct (GGUF Q4_K_M)",
            "content_counts": len(library["archives"]) == 7 and len(maps["files"]) == 4 and len(guides["files"]) == 10,
            "model_switches": all(run.get("switch_job", {"state": "complete"})["state"] == "complete" for run in runs),
            "all_responses_completed": all(run["chat"]["done"] and not run["chat"]["errors"] and run["chat"]["answer"] for run in runs),
            "performance_reported": bool(final_status["engine"].get("last_generation", {}).get("tokens_per_second")),
            "document_citation": grounded["done"] and len(grounded["sources"]) >= 1,
            "refresh_all": refresh.get("result", {}).get("models") == 3,
            "clean_shutdown": process.returncode == 0 and not remaining,
        }
        result["checks"] = checks
        result["remaining_managed_processes"] = remaining
        result["passed"] = all(checks.values())
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
