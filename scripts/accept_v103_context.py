"""Packaged-runtime acceptance for v1.0.3 context length (development stage only, never the USB)."""
from __future__ import annotations

import argparse
import ctypes
import json
import os
import re
import sqlite3
import subprocess
import time
import urllib.request
import uuid
from ctypes import wintypes
from pathlib import Path

import psutil

OPTIONS = (2048, 4096, 8192, 16384, 32768)
MODELS = ("Qwen3-1.7B-Q4_K_M.gguf", "Qwen3-4B-Q4_K_M.gguf", "Qwen3.5-4B-Q4_K_M.gguf")


def api(base, token, path, method="GET", body=None, job=None, timeout=60):
    headers = {"X-SWS-Token": token, "Content-Type": "application/json"}
    if job:
        headers["X-SWS-Job"] = job
    data = json.dumps(body).encode() if body is not None else (b"{}" if method == "POST" else None)
    request = urllib.request.Request(base + path, data=data, method=method, headers=headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def wait_job(base, token, job_id, timeout=900):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        job = api(base, token, f"/api/jobs/{job_id}")
        if job["state"] in {"complete", "error"}:
            return job
        time.sleep(0.5)
    raise TimeoutError("job")


def wait_engine(base, token, timeout=900):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        status = api(base, token, "/api/status")
        if status["engine"]["state"] in {"running", "error"}:
            return status
        time.sleep(0.5)
    raise TimeoutError("engine")


def chat(base, token, message, conversation=None, timeout=1200):
    request = urllib.request.Request(
        base + "/api/chat",
        data=json.dumps({"message": message, "mode": "general", "conversation_id": conversation}).encode(),
        method="POST",
        headers={"X-SWS-Token": token, "Content-Type": "application/json"},
    )
    started = time.monotonic()
    first_event, first_text, parts, errors = None, None, [], []
    with urllib.request.urlopen(request, timeout=timeout) as response:
        for line in response:
            event = json.loads(line)
            if first_event is None:
                first_event = event
            if event.get("delta"):
                first_text = first_text or time.monotonic()
                parts.append(event["delta"])
            if event.get("error"):
                errors.append(event["error"])
    return {
        "first": first_event,
        "answer": "".join(parts).strip(),
        "errors": errors,
        "client_time_to_first_text_s": round((first_text or time.monotonic()) - started, 2),
        "client_total_s": round(time.monotonic() - started, 2),
    }


def apply(base, token, body):
    result = api(base, token, "/api/settings", "POST", {**body, "restart_engine": True})
    job = wait_job(base, token, result["job_id"])
    return job, wait_engine(base, token)


def kobold_private_mib(root: Path) -> int:
    total = 0
    for process in psutil.process_iter(["name", "exe"]):
        if str(root).lower() in str(process.info.get("exe") or "").lower() and "kobold" in (process.info.get("name") or "").lower():
            try:
                total += process.memory_info().private
            except psutil.Error:
                pass
    return round(total / 2**20)


def managed(root: Path):
    return [p.pid for p in psutil.process_iter(["name", "exe"]) if str(root).lower() in str(p.info.get("exe") or "").lower()
            and any(t in (p.info.get("name") or "").lower() for t in ("kobold", "securitywithsam"))]


class _Limits(ctypes.Structure):
    _fields_ = [("a", ctypes.c_longlong), ("b", ctypes.c_longlong), ("LimitFlags", wintypes.DWORD), ("c", ctypes.c_size_t), ("d", ctypes.c_size_t),
                ("e", wintypes.DWORD), ("f", ctypes.c_size_t), ("g", wintypes.DWORD), ("h", wintypes.DWORD)]


class _Extended(ctypes.Structure):
    _fields_ = [("Basic", _Limits), ("Io", ctypes.c_ulonglong * 6), ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcess", ctypes.c_size_t), ("PeakJob", ctypes.c_size_t)]


class Backend:
    def __init__(self, root: Path, memory_limit_mib: int | None = None):
        self.root = root
        runtime = root / "Apps" / "Offline AI" / "Runtime" / "SecurityWithSamOfflineAI.exe"
        self.session = root / "Apps" / "Offline AI" / "Data" / f"v103-{uuid.uuid4().hex[:8]}.json"
        flags = subprocess.CREATE_NO_WINDOW | (0x4 if memory_limit_mib else 0)  # CREATE_SUSPENDED when limited
        self.process = subprocess.Popen([str(runtime), "--headless", "--root", str(root), "--session-file", str(self.session)],
                                        cwd=runtime.parent, creationflags=flags)
        self.job = None
        if memory_limit_mib:
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel32.CreateJobObjectW.restype = wintypes.HANDLE
            self.job = kernel32.CreateJobObjectW(None, None)
            info = _Extended()
            info.Basic.LimitFlags = 0x200 | 0x2000  # JOB_MEMORY | KILL_ON_JOB_CLOSE
            info.JobMemoryLimit = memory_limit_mib * 2**20
            assert kernel32.SetInformationJobObject(wintypes.HANDLE(self.job), 9, ctypes.byref(info), ctypes.sizeof(info))
            assert kernel32.AssignProcessToJobObject(wintypes.HANDLE(self.job), wintypes.HANDLE(int(self.process._handle)))
            psutil.Process(self.process.pid).resume()
        deadline = time.monotonic() + 120
        while not self.session.is_file():
            if self.process.poll() is not None or time.monotonic() > deadline:
                raise RuntimeError("backend did not start")
            time.sleep(0.2)
        self.base, self.token = json.loads(self.session.read_text(encoding="utf-8"))["url"].split("/#token=", 1)

    def shutdown(self):
        api(self.base, self.token, "/api/shutdown", "POST", {})
        self.process.wait(timeout=60)
        deadline = time.monotonic() + 15
        while managed(self.root) and time.monotonic() < deadline:
            time.sleep(0.25)
        if self.job:
            ctypes.windll.kernel32.CloseHandle(wintypes.HANDLE(self.job))
        return {"exit_code": self.process.returncode, "session_removed": not self.session.exists(), "remaining": managed(self.root)}


def log_since(log: Path, offset: int) -> str:
    with log.open("rb") as stream:
        stream.seek(offset)
        return stream.read().decode("utf-8", "replace")


def seed_conversation(chats_db: Path, turns: int = 70) -> str:
    """Insert a long synthetic conversation (test stage only) so context trimming can be measured quickly."""
    conversation = "v103-long-" + uuid.uuid4().hex[:8]
    now = int(time.time())
    with sqlite3.connect(chats_db) as connection:
        connection.execute("INSERT INTO conversations(id, title, mode, created_at, updated_at) VALUES(?, ?, 'general', ?, ?)", (conversation, "Long context test", now, now))
        for index in range(turns):
            role = "user" if index % 2 == 0 else "assistant"
            content = f"Turn {index}. Field note about river crossings, map reading, and supply planning. " * 18
            connection.execute("INSERT INTO messages(conversation_id, role, content, sources_json, created_at) VALUES(?, ?, ?, '[]', ?)", (conversation, role, content, now))
    return conversation


def message_count(chats_db: Path, conversation: str) -> int:
    with sqlite3.connect(chats_db) as connection:
        return connection.execute("SELECT COUNT(*) FROM messages WHERE conversation_id=?", (conversation,)).fetchone()[0]


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
    mei_before = len(list(Path(os.environ["TEMP"]).glob("_MEI*")))
    r: dict[str, object] = {"root": str(root), "matrix": [], "long_conversation": []}

    backend = Backend(root)
    first = wait_engine(backend.base, backend.token)
    r["initial"] = {"context": first["engine"]["context"], "acceleration": first["engine"]["acceleration"]["actual"]}
    for backend_mode in ("cpu", "auto_vulkan"):
        apply(backend.base, backend.token, {"acceleration_mode": backend_mode, "vulkan_device": None})
        for model in MODELS:
            job_id = uuid.uuid4().hex
            api(backend.base, backend.token, "/api/models/load", "POST", {"filename": model}, job_id)
            wait_job(backend.base, backend.token, job_id)
            wait_engine(backend.base, backend.token)
            for size in OPTIONS:
                settings = api(backend.base, backend.token, "/api/settings")
                option = next(item for item in settings["context"]["options"] if item["size"] == size)
                offset = log.stat().st_size
                started = time.monotonic()
                job, status = apply(backend.base, backend.token, {"context_size": size, "allow_over_estimate": True})
                restart_s = round(time.monotonic() - started, 1)
                new_log = log_since(log, offset)
                n_ctx = re.findall(r"llama_context: n_ctx\s+=\s+(\d+)", new_log)
                device_mib = sum(float(x) for x in re.findall(r"Vulkan0 (?:model|KV|compute) buffer size =\s+([\d.]+) MiB", new_log))
                measured_private = kobold_private_mib(root)
                reply = chat(backend.base, backend.token, "Give one short sentence about maps.")
                perf = api(backend.base, backend.token, "/api/status")["engine"]["last_generation"] or {}
                engine = status["engine"]
                r["matrix"].append({
                    "backend": engine["acceleration"]["actual"], "model": model, "size": size, "job": job["state"],
                    "context": engine["context"], "log_n_ctx": int(n_ctx[-1]) if n_ctx else None,
                    "layers": engine["acceleration"].get("layers"), "restart_s": restart_s,
                    "estimate_ram_mib": option["ram_mib"], "estimate_vram_mib": option["vram_mib"], "estimate_level": option["level"],
                    "measured_kobold_private_mib": measured_private, "measured_device_buffers_mib": round(device_mib) if device_mib else None,
                    "answered": bool(reply["answer"]) and not reply["errors"],
                    "prompt_tps": perf.get("prompt_tokens_per_second"), "gen_tps": perf.get("tokens_per_second"),
                    "ttft_s": perf.get("time_to_first_token_seconds"),
                })
                print(json.dumps(r["matrix"][-1]), flush=True)

    # Long conversation: what each size actually sends, real token counts, and the time cost.
    apply(backend.base, backend.token, {"acceleration_mode": "cpu", "vulkan_device": None})
    job_id = uuid.uuid4().hex
    api(backend.base, backend.token, "/api/models/load", "POST", {"filename": "Qwen3-1.7B-Q4_K_M.gguf"}, job_id)
    wait_job(backend.base, backend.token, job_id)
    chats_db = data / "Chats" / "chats.sqlite3"
    conversation = seed_conversation(chats_db)
    seeded = message_count(chats_db, conversation)
    for backend_mode, sizes in (("cpu", OPTIONS[:4]), ("auto_vulkan", OPTIONS)):
        apply(backend.base, backend.token, {"acceleration_mode": backend_mode, "vulkan_device": None})
        for size in sizes:
            apply(backend.base, backend.token, {"context_size": size, "allow_over_estimate": True})
            offset = log.stat().st_size
            reply = chat(backend.base, backend.token, "In one sentence, what did the earliest turn you can see say?", conversation)
            limits = re.findall(r"CtxLimit:(\d+)/(\d+)", log_since(log, offset))
            perf = api(backend.base, backend.token, "/api/status")["engine"]["last_generation"] or {}
            context_info = reply["first"].get("context", {})
            r["long_conversation"].append({
                "backend": backend_mode, "size": size, "history_sent": context_info.get("history_sent"),
                "history_omitted": context_info.get("history_omitted"), "estimate_tokens": context_info.get("prompt_tokens_estimate"),
                "actual_prompt_tokens": perf.get("prompt_tokens"), "ctx_limit_line": limits[-1] if limits else None,
                "prompt_tps": perf.get("prompt_tokens_per_second"), "gen_tps": perf.get("tokens_per_second"),
                "ttft_s": perf.get("time_to_first_token_seconds"), "total_s": perf.get("seconds"),
                "answered": bool(reply["answer"]) and not reply["errors"], "errors": reply["errors"],
            })
            print(json.dumps(r["long_conversation"][-1]), flush=True)
    r["long_saved_before"], r["long_saved_after"] = seeded, message_count(chats_db, conversation)
    apply(backend.base, backend.token, {"acceleration_mode": "cpu", "vulkan_device": None, "context_size": "auto"})
    r["shutdown_1"] = backend.shutdown()

    # Real failure: a 4 GiB job memory limit lets 8K start but makes 32K fail to allocate.
    offset = log.stat().st_size
    limited = Backend(root, memory_limit_mib=4096)
    wait_engine(limited.base, limited.token)
    job, status = apply(limited.base, limited.token, {"context_size": 32768, "allow_over_estimate": True})
    fail_log = log_since(log, offset)
    r["failure_recovery"] = {"job": job["state"], "context": status["engine"]["context"], "n_ctx_attempts": re.findall(r"llama_context: n_ctx\s+=\s+(\d+)", fail_log),
                             "loads": fail_log.count("Loading Text Model:"), "answered": bool(chat(limited.base, limited.token, "Say hello.")["answer"])}
    r["failure_settings"] = api(limited.base, limited.token, "/api/settings")["context"]["failure"]
    r["shutdown_2"] = limited.shutdown()
    offset = log.stat().st_size
    again = Backend(root, memory_limit_mib=4096)
    restarted = wait_engine(again.base, again.token)
    restart_log = log_since(log, offset)
    r["restart_after_failure"] = {"context": restarted["engine"]["context"], "loads": restart_log.count("Loading Text Model:"),
                                  "n_ctx": re.findall(r"llama_context: n_ctx\s+=\s+(\d+)", restart_log)}
    r["failure_after_restart"] = api(again.base, again.token, "/api/settings")["context"]["failure"]
    r["long_saved_after_restarts"] = message_count(chats_db, conversation)
    api(again.base, again.token, "/api/settings", "POST", {"context_size": "auto"})
    r["shutdown_3"] = again.shutdown()
    r["mei_before"], r["mei_after"] = mei_before, len(list(Path(os.environ["TEMP"]).glob("_MEI*")))

    matrix = r["matrix"]
    checks = {
        "starts_cpu_automatic": r["initial"]["acceleration"] == "cpu" and r["initial"]["context"]["mode"] == "automatic",
        "all_30_option_runs_exact": len(matrix) == 30 and all(m["context"]["actual"] == m["size"] == m["context"]["requested"] and m["log_n_ctx"] == m["size"] + 256 for m in matrix),
        "all_30_answered": all(m["answered"] and m["job"] == "complete" for m in matrix),
        "gpu_runs_verified_on_gpu": all(m["backend"] == "gpu" and (m["layers"] or [0])[0] > 0 for m in matrix[15:]),
        "cpu_estimate_conservative": all(m["estimate_ram_mib"] >= m["measured_kobold_private_mib"] for m in matrix[:15]),
        "gpu_vram_estimate_conservative": all(m["estimate_vram_mib"] >= m["measured_device_buffers_mib"] for m in matrix[15:]),
        "long_history_scales_and_fits": all(item["answered"] and int(item["ctx_limit_line"][0]) <= int(item["ctx_limit_line"][1]) for item in r["long_conversation"])
            and r["long_conversation"][0]["history_omitted"] > r["long_conversation"][3]["history_omitted"],
        # Later phases chat in new conversations, so the long conversation must be exactly unchanged by them.
        "full_history_preserved": r["long_saved_after"] == r["long_saved_before"] + 2 * len(r["long_conversation"]) and r["long_saved_after_restarts"] == r["long_saved_after"],
        # The log window includes the limited backend's own startup at the automatic size before 32K is applied.
        "failure_retried_once_to_safe": r["failure_recovery"]["context"]["requested"] == 32768 and r["failure_recovery"]["context"]["actual"] < 32768
            and r["failure_recovery"]["context"]["fallback"] is True and r["failure_recovery"]["n_ctx_attempts"][1:] == ["33024", "8448"]
            and r["failure_recovery"]["answered"],
        "failure_remembered": bool(r["failure_settings"]) and bool(r["failure_after_restart"]) and r["restart_after_failure"]["loads"] == 1
            and (r["restart_after_failure"]["context"]["actual"] or 0) == 8192,
        "clean_shutdowns": all(r[k]["exit_code"] == 0 and r[k]["session_removed"] and not r[k]["remaining"] for k in ("shutdown_1", "shutdown_2", "shutdown_3")),
        "no_new_mei": r["mei_after"] <= r["mei_before"],
    }
    r["checks"], r["passed"] = checks, all(checks.values())
    args.output.write_text(json.dumps(r, indent=2), encoding="utf-8")
    print(json.dumps(checks, indent=2))
    return 0 if r["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
