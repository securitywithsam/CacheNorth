"""Measure real KoboldCpp memory per model and context size (development stage only, never the USB).

For each model x context x backend: launch the unpacked KoboldCpp, wait until ready, read the
allocation lines KoboldCpp logs and the process memory, run one short generation, then stop it.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

import psutil

PATTERNS = {
    "n_ctx": r"llama_context: n_ctx\s+=\s+(\d+)",
    "kv_mib": r"llama_kv_cache:\s+(?:CPU|Vulkan0) KV buffer size =\s+([\d.]+) MiB",
    "rs_mib": r"llama_memory_recurrent:\s+\S+ RS buffer size =\s+([\d.]+) MiB",
    "compute_mib": r"sched_reserve:\s+(?:CPU|Vulkan0) compute buffer size =\s+([\d.]+) MiB",
    "model_mib": r"load_tensors:\s+(?:CPU|Vulkan0) model buffer size =\s+([\d.]+) MiB",
    "offloaded": r"offloaded (\d+/\d+) layers to GPU",
}


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def tree_bytes(process: psutil.Process) -> tuple[int, int]:
    rss = private = 0
    for item in [process, *process.children(recursive=True)]:
        try:
            info = item.memory_info()
            rss += info.rss
            private += getattr(info, "private", 0)
        except psutil.Error:
            pass
    return rss, private


def generate(port: int) -> dict[str, object]:
    body = json.dumps({"prompt": "Write two sentences about rivers.", "max_length": 48, "temperature": 0.3}).encode()
    request = urllib.request.Request(f"http://127.0.0.1:{port}/api/v1/generate", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=300) as response:
        json.load(response)
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/extra/perf", timeout=10) as response:
        perf = json.load(response)
    return {"prompt_tps": perf.get("last_process_speed"), "gen_tps": perf.get("last_eval_speed")}


def run(kobold: Path, model: Path, context: int, backend: str, logs: Path) -> dict[str, object]:
    port = free_port()
    flags = ["--usevulkan", "0"] if backend == "vulkan" else ["--usecpu"]
    log_path = logs / f"{model.stem}-{context}-{backend}.log"
    command = [str(kobold), "--model", str(model), "--contextsize", str(context), "--host", "127.0.0.1",
               "--port", str(port), "--threads", "7", "--blasthreads", "7", "--quiet", "--jinja", *flags]
    environment = {**os.environ, "PROCESSOR_ARCHITECTURE": "x64"}
    started = time.monotonic()
    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(command, cwd=kobold.parent, stdout=log, stderr=subprocess.STDOUT,
                                   env=environment, creationflags=subprocess.CREATE_NO_WINDOW)
    result: dict[str, object] = {"model": model.name, "context": context, "backend": backend}
    try:
        ready = False
        while time.monotonic() - started < 300 and process.poll() is None:
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/api/extra/version", timeout=1).close()
                ready = True
                break
            except OSError:
                time.sleep(0.25)
        result["ready"] = ready
        result["load_seconds"] = round(time.monotonic() - started, 2)
        if ready:
            rss, private = tree_bytes(psutil.Process(process.pid))
            result["rss_mib"], result["private_mib"] = round(rss / 2**20), round(private / 2**20)
            result.update(generate(port))
    finally:
        parent = psutil.Process(process.pid)
        for item in [*parent.children(recursive=True), parent]:
            try:
                item.kill()
            except psutil.Error:
                pass
        process.wait(timeout=30)
    text = log_path.read_text(encoding="utf-8", errors="replace")
    for key, pattern in PATTERNS.items():
        found = re.findall(pattern, text)
        result[key] = (found[-1] if key == "offloaded" else float(found[-1])) if found else None
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-removable", action="store_true", help="Allow running against a removable drive.")
    parser.add_argument("--contexts", default="2048,4096,8192,16384,32768")
    parser.add_argument("--backends", default="cpu")
    args = parser.parse_args()
    root = args.root.resolve()
    # These tests write logs, settings, and test chats under the root; keep them off portable drives
    # (where real user data lives) unless explicitly allowed.
    if not args.allow_removable and os.name == "nt" and __import__("ctypes").windll.kernel32.GetDriveTypeW(root.anchor) == 2:
        raise SystemExit(f"{root.anchor} is a removable drive. Run against a development copy, or pass --allow-removable.")
    kobold = root / "Apps" / "Offline AI" / "KoboldCpp" / "koboldcpp-launcher.exe"
    models = sorted((root / "Apps" / "Offline AI" / "Models").glob("*.gguf"))
    logs = args.output.parent / "context-memory-logs"
    logs.mkdir(parents=True, exist_ok=True)
    results = []
    for backend in args.backends.split(","):
        for model in models:
            for context in (int(value) for value in args.contexts.split(",")):
                item = run(kobold, model, context, backend, logs)
                results.append(item)
                print(json.dumps(item), flush=True)
    args.output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
