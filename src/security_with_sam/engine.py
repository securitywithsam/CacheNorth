from __future__ import annotations

import contextlib
import ctypes
import json
import os
import secrets
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

import cpuinfo
import psutil

from .acceleration import classify_failure, library_load_stalled, parse_vulkan_run
from .config import AppPaths, ensure_temporary_storage
from .security import confined_path
from .windows_job import assign_kill_on_close, close_job

# SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX | SEM_NOOPENFILEERRORBOX
_QUIET_ERROR_MODE = 0x0001 | 0x0002 | 0x8000
_error_mode_lock = threading.Lock()
# Seconds the backend-library load line may remain KoboldCpp's newest output before the attempt is abandoned.
LIBRARY_LOAD_STALL_SECONDS = 60.0


@contextlib.contextmanager
def quiet_child_error_dialogs():
    """Children inherit the error mode, so a DLL that Windows refuses to load returns an error
    instead of a modal loader dialog that would stall startup. Security policy still applies."""
    if os.name != "nt":
        yield
        return
    kernel32 = ctypes.windll.kernel32
    with _error_mode_lock:
        previous = kernel32.GetErrorMode()
        kernel32.SetErrorMode(previous | _QUIET_ERROR_MODE)
        try:
            yield
        finally:
            kernel32.SetErrorMode(previous)


def reached_model_load(log_text: str) -> bool:
    """KoboldCpp logs this after its backend library loaded; later failures can be memory-related."""
    return "Loading Text Model:" in log_text


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@dataclass(frozen=True)
class MemoryProfile:
    name: str
    context_size: int
    max_output_tokens: int


def select_memory_profile(total_ram_bytes: int | None = None) -> MemoryProfile:
    total = total_ram_bytes if total_ram_bytes is not None else psutil.virtual_memory().total
    gib = total / (1024**3)
    if gib < 10:
        return MemoryProfile("low-memory", 2048, 384)
    if gib < 24:
        return MemoryProfile("recommended", 4096, 768)
    return MemoryProfile("high-memory", 8192, 1024)


@dataclass(frozen=True)
class CpuProfile:
    mode: str
    flags: tuple[str, ...]
    avx: bool
    avx2: bool


def select_cpu_threads(physical_cores: int | None = None) -> int:
    """Choose a conservative physical-core count and leave one large CPU free for Windows."""
    physical = physical_cores or psutil.cpu_count(logical=False) or psutil.cpu_count(logical=True) or 1
    return max(1, min(12, physical - 1 if physical > 4 else physical))


def _probe_cpu_flags(helper_path: Path | None) -> set[str]:
    if helper_path is None or not helper_path.is_file():
        return set()
    try:
        startup_info = subprocess.STARTUPINFO() if os.name == "nt" else None
        if startup_info:
            startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        result = subprocess.run(
            [str(helper_path)],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
            startupinfo=startup_info,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        payload = json.loads(result.stdout.strip())
        return {name for name in ("avx", "avx2") if int(payload.get(name, 0)) == 1}
    except (OSError, subprocess.SubprocessError, ValueError, json.JSONDecodeError, AttributeError):
        return set()


def _default_cpu_probe_path() -> Path | None:
    executable_dir = Path(sys.executable).resolve().parent
    for candidate in (
        executable_dir / "cache-north-cpuinfo.exe",
        executable_dir.parent / "cache-north-cpuinfo.exe",
    ):
        if candidate.is_file():
            return candidate
    return None


def detect_cpu_profile(flags: Iterable[str] | None = None, helper_path: Path | None = None) -> CpuProfile:
    if flags is None:
        detected = _probe_cpu_flags(helper_path or _default_cpu_probe_path())
        if not detected:
            detected = {value.lower() for value in cpuinfo.get_cpu_info().get("flags", [])}
    else:
        detected = {value.lower() for value in flags}
    avx2 = "avx2" in detected
    avx = "avx" in detected
    if avx2:
        return CpuProfile("AVX2", ("--usecpu",), avx=True, avx2=True)
    if avx:
        return CpuProfile("AVX1 compatibility", ("--usecpu", "--noavx2"), avx=True, avx2=False)
    return CpuProfile("x64 failsafe", ("--usecpu", "--noavx2", "--failsafe"), avx=False, avx2=False)


class EngineError(RuntimeError):
    pass


class KoboldEngine:
    """Own one KoboldCpp process and allow at most one Vulkan-to-CPU fallback."""

    def __init__(
        self,
        paths: AppPaths,
        status_callback: Callable[[str, str], None] | None = None,
        memory_profile: MemoryProfile | None = None,
        vulkan_device: int | None = None,
        cpu_threads: int | None = None,
    ):
        self.paths = paths
        self.status_callback = status_callback or (lambda _state, _message: None)
        self.memory_profile = memory_profile
        self.vulkan_device = vulkan_device
        self.cpu_threads = cpu_threads or select_cpu_threads()
        self.process: subprocess.Popen[str] | None = None
        self.port: int | None = None
        # Prefix prevents a URL-safe token beginning with '-' from being parsed as a CLI option.
        self.password = f"sws_{secrets.token_urlsafe(24)}"
        self.mode = "stopped"
        self.backend = "stopped"
        self.message = "AI engine is stopped."
        self._lock = threading.RLock()
        self._log_handle = None
        self._job_handle: int | None = None
        self.selected_model: Path | None = None
        self._generation_lock = threading.Lock()
        self.last_generation: dict[str, object] | None = None
        self.cpu_profile = detect_cpu_profile(helper_path=self._cpu_probe_path())
        self.acceleration: dict[str, object] = {"selected": "cpu", "actual": "stopped"}
        self.context_status: dict[str, object] = {"mode": None, "requested": None, "actual": None, "fallback": False, "reason": None}
        self._log_offset = 0
        self._launch_outcome = ""

    def _cpu_probe_path(self) -> Path | None:
        for candidate in (
            self.paths.product / "cache-north-cpuinfo.exe",
            self.paths.runtime / "cache-north-cpuinfo.exe",
        ):
            if candidate.is_file():
                return candidate
        return None

    def _set_status(self, state: str, message: str) -> None:
        self.mode = state
        self.message = message
        self.status_callback(state, message)

    def find_executable(self) -> Path:
        candidates = (
            self.paths.product / "KoboldCpp" / "koboldcpp-launcher.exe",
            self.paths.runtime / "KoboldCpp" / "koboldcpp-launcher.exe",
            self.paths.product / "koboldcpp-nocuda.exe",
            self.paths.runtime / "koboldcpp-nocuda.exe",
            self.paths.product / "koboldcpp.exe",
        )
        for candidate in candidates:
            if candidate.is_file():
                return candidate
        raise EngineError(
            "KoboldCpp is missing. Expected the unpacked Apps\\Offline AI\\KoboldCpp runtime "
            "or koboldcpp-nocuda.exe in Apps\\Offline AI."
        )

    def runtime_layout(self) -> str:
        executable = self.find_executable()
        return "unpacked" if executable.name.casefold() == "koboldcpp-launcher.exe" else "one-file"

    def find_model(self) -> Path:
        if self.selected_model is not None and self.selected_model.is_file():
            return self.selected_model
        models = sorted(self.paths.models.glob("*.gguf")) if self.paths.models.is_dir() else []
        if models:
            return models[0]
        raise EngineError("No GGUF model was found in Apps\\Offline AI\\Models.")

    def set_model(self, filename: str) -> Path:
        candidate = confined_path(self.paths.models, self.paths.models / Path(filename).name)
        if candidate.name != filename or candidate.suffix.lower() != ".gguf" or not candidate.is_file():
            raise EngineError("The selected GGUF model is missing or invalid.")
        if self.process and self.process.poll() is None:
            raise EngineError("Stop the current AI engine before changing models.")
        self.selected_model = candidate
        self.last_generation = None
        return candidate

    def _command(self, acceleration: str) -> list[str]:
        executable = self.find_executable()
        model = self.find_model()
        memory = self.memory_profile or select_memory_profile()
        cpu = self.cpu_profile
        flags: list[str]
        if acceleration == "vulkan" and cpu.avx2:
            flags = ["--usevulkan", *([str(self.vulkan_device)] if self.vulkan_device is not None else [])]
        elif acceleration == "vulkan" and cpu.avx:
            flags = [
                "--usevulkan",
                *([str(self.vulkan_device)] if self.vulkan_device is not None else []),
                "--noavx2",
            ]
        else:
            flags = list(cpu.flags)
        return [
            str(executable),
            "--model",
            str(model),
            "--contextsize",
            str(memory.context_size),
            "--host",
            "127.0.0.1",
            "--port",
            str(self.port),
            "--password",
            self.password,
            "--jinja",
            "--jinjathink",
            "false",
            "--quiet",
            "--threads",
            str(self.cpu_threads),
            "--blasthreads",
            str(self.cpu_threads),
            *flags,
        ]

    def _launch_environment(self) -> dict[str, str]:
        """Prevent KoboldCpp's bundled detector from overriding our explicit, tested CPU flags.

        KoboldCpp 1.124.2 can misread its helper result when launched as a one-file
        application and silently force failsafe mode. CacheNorth already detects AVX/AVX2
        in-process, then passes the matching explicit backend flag. Reporting a neutral x64
        architecture to the bundled Python layer skips only that duplicate detector.
        """
        environment = os.environ.copy()
        if os.name == "nt":
            environment["PROCESSOR_ARCHITECTURE"] = "x64"
        return environment

    def _ready(self) -> bool:
        if self.port is None:
            return False
        request = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/api/extra/version",
            headers={"Authorization": f"Bearer {self.password}"},
        )
        try:
            with urllib.request.urlopen(request, timeout=1.5) as response:
                return response.status == 200
        except (OSError, urllib.error.URLError):
            return False

    def _log_since_launch(self, limit: int = 512 * 1024) -> str:
        path = self.paths.logs / "koboldcpp.log"
        try:
            if self._log_handle:
                self._log_handle.flush()
            with path.open("rb") as stream:
                stream.seek(max(self._log_offset, path.stat().st_size - limit))
                return stream.read().decode("utf-8", errors="replace")
        except OSError:
            return ""

    def _launch_once(self, acceleration: str, timeout: float) -> bool:
        self.port = find_free_port()
        command = self._command(acceleration)
        self.paths.logs.mkdir(parents=True, exist_ok=True)
        log_path = self.paths.logs / "koboldcpp.log"
        self._log_offset = log_path.stat().st_size if log_path.is_file() else 0
        self._log_handle = log_path.open("a", encoding="utf-8")
        startup_info = subprocess.STARTUPINFO() if os.name == "nt" else None
        if startup_info:
            startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        with quiet_child_error_dialogs():
            self.process = subprocess.Popen(
                command,
                # The unpacked launcher resolves its Python runtime and native DLLs beside itself.
                # The one-file fallback remains compatible with the historical product-directory cwd.
                cwd=self.find_executable().parent,
                stdout=self._log_handle,
                stderr=subprocess.STDOUT,
                text=True,
                startupinfo=startup_info,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                env=self._launch_environment(),
            )
        if os.name == "nt":
            self._job_handle = assign_kill_on_close(int(self.process._handle))  # type: ignore[attr-defined]
        started = time.monotonic()
        deadline = started + timeout
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                self._launch_outcome = "exited"
                return False
            if self._ready():
                self._launch_outcome = "ready"
                return True
            if (
                acceleration == "vulkan"
                and time.monotonic() - started >= LIBRARY_LOAD_STALL_SECONDS
                and library_load_stalled(self._log_since_launch())
            ):
                self._launch_outcome = "stalled"
                return False
            time.sleep(0.25)
        self._launch_outcome = "timeout"
        return False

    def start(
        self,
        prefer_vulkan: bool = False,
        timeout: float = 180.0,
        selected_mode: str | None = None,
        note: str | None = None,
        fallback_profile: MemoryProfile | None = None,
        context_note: str | None = None,
    ) -> None:
        with self._lock:
            if self.process and self.process.poll() is None:
                return
            requested = self.memory_profile or select_memory_profile()
            self.context_status = {
                "mode": requested.name,
                "requested": requested.context_size,
                "actual": None,
                "fallback": False,
                "reason": context_note,
            }
            retry_profile = (
                fallback_profile
                if fallback_profile and fallback_profile.context_size < requested.context_size
                else None
            )
            self.acceleration = {
                "selected": selected_mode or ("auto_vulkan" if prefer_vulkan else "cpu"),
                "actual": "starting",
                "device": None,
                "layers": None,
                "devices": [],
                "fallback": False,
                "failure_kind": None,
                "reason": note,
            }
            try:
                ensure_temporary_storage()
            except Exception as exc:
                self._set_status("error", str(exc))
                raise EngineError(str(exc)) from exc
            memory = requested
            cpu = self.cpu_profile

            def use_smaller_context(where: str) -> None:
                nonlocal memory, retry_profile
                reason = (
                    f"The {memory.context_size:,}-token context did not start {where}. "
                    f"CacheNorth retried once with a {retry_profile.context_size:,}-token context."
                )
                memory, retry_profile = retry_profile, None
                self.memory_profile = memory
                self.context_status.update(fallback=True, reason=reason)

            def ready(message: str) -> None:
                self.context_status["actual"] = memory.context_size
                self._set_status("running", message)

            attempt_vulkan = prefer_vulkan and cpu.avx
            if prefer_vulkan and not cpu.avx:
                self.acceleration["reason"] = "GPU acceleration in this release needs a CPU with AVX. CPU mode is active."
            if attempt_vulkan:
                self._set_status("starting", "Trying optional GPU acceleration (Vulkan). CPU mode is used automatically if it fails...")
                while True:
                    launched = self._launch_once("vulkan", timeout)
                    log_text = self._log_since_launch()
                    details = parse_vulkan_run(log_text)
                    self.acceleration["devices"] = details["devices"] or self.acceleration["devices"]
                    if launched:
                        layers = details["layers"]
                        on_gpu = bool(layers and layers[0] > 0)
                        self.backend = "vulkan"
                        self.acceleration.update(
                            actual="gpu" if on_gpu else "cpu",
                            device=details["device"],
                            layers=layers,
                            device_free_mib=details.get("free_mib"),
                        )
                        if on_gpu:
                            ready(f"AI engine is ready on the GPU: {details['device'] or 'Vulkan device'} ({layers[0]}/{layers[1]} layers, {memory.context_size:,}-token context).")
                        else:
                            self.acceleration["reason"] = "The Vulkan backend started but offloaded no model layers, so inference runs on the CPU."
                            ready(f"AI engine is ready, running on the CPU ({memory.context_size:,}-token context).")
                        return
                    kind, reason = classify_failure(
                        log_text,
                        stalled=self._launch_outcome == "stalled",
                        timed_out=self._launch_outcome == "timeout",
                    )
                    self.stop()
                    # Only a failure after model loading began can be a context-memory problem. Library
                    # blocks, missing drivers, and stalled loads would just repeat (with any Windows prompt).
                    if retry_profile and reached_model_load(log_text) and kind not in {"blocked_by_windows", "no_vulkan_device", "library_load_stalled"}:
                        use_smaller_context("on the GPU")
                        continue
                    break
                self.acceleration.update(fallback=True, failure_kind=kind, reason=reason)
                self._set_status("starting", "GPU acceleration did not start. Starting CPU mode once...")
            else:
                self._set_status("starting", f"Starting CPU mode ({cpu.mode}, {memory.context_size:,}-token context)...")
            while True:
                if self._launch_once("cpu", timeout):
                    self.backend = "cpu"
                    self.acceleration["actual"] = "cpu"
                    suffix = " GPU was unavailable; see Settings for the reason." if self.acceleration["fallback"] else ""
                    ready(f"AI engine is ready in CPU mode ({memory.context_size:,}-token context).{suffix}")
                    return
                cpu_log = self._log_since_launch()
                self.stop()
                if retry_profile and reached_model_load(cpu_log):
                    use_smaller_context("in CPU mode")
                    self._set_status("starting", f"Retrying once with a {memory.context_size:,}-token context...")
                    continue
                break
            self.context_status["actual"] = None
            message = (
                "The AI engine could not start in CPU mode. Check available RAM, temporary storage, CPU support, "
                "and Apps\\Offline AI\\Data\\Logs\\koboldcpp.log. This application will not retry automatically."
            )
            self._set_status("error", message)
            raise EngineError(message)

    def status(self) -> dict[str, object]:
        # "running" only once start() has finished recording what is running, not merely when HTTP answers.
        running = bool(self.mode == "running" and self.process and self.process.poll() is None and self._ready())
        return {
            "state": "running" if running else self.mode,
            "message": self.message,
            "mode": self.mode,
            "backend": self.backend,
            "port": self.port if running else None,
            "model": self.find_model().name if self.paths.models.exists() and any(self.paths.models.glob("*.gguf")) else None,
            "threads": self.cpu_threads,
            "runtime_layout": self.runtime_layout(),
            "last_generation": self.last_generation,
            "acceleration": self.acceleration,
            "context": self.context_status,
        }

    def running_profile(self) -> MemoryProfile:
        """The context and output limits of the engine that is actually running (after any fallback)."""
        return self.memory_profile or select_memory_profile()

    def count_tokens(self, text: str) -> int | None:
        """Exact token count from the loaded model's tokenizer, or None if the engine cannot answer."""
        if not self.port:
            return None
        request = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/api/extra/tokencount",
            data=json.dumps({"prompt": text}).encode("utf-8"),
            method="POST",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.password}"},
        )
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                value = json.load(response).get("value")
            return int(value) if isinstance(value, int) else None
        except (OSError, urllib.error.URLError, json.JSONDecodeError, ValueError):
            return None

    def stop_generation(self) -> None:
        if not self.port:
            return
        request = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/api/extra/abort",
            data=b"{}",
            method="POST",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.password}"},
        )
        try:
            urllib.request.urlopen(request, timeout=2).close()
        except OSError:
            pass

    def _performance(self) -> dict[str, object]:
        if not self.port:
            return {}
        request = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/api/extra/perf",
            headers={"Authorization": f"Bearer {self.password}"},
        )
        try:
            with urllib.request.urlopen(request, timeout=3) as response:
                payload = json.load(response)
            return payload if isinstance(payload, dict) else {}
        except (OSError, urllib.error.URLError, json.JSONDecodeError):
            return {}

    def stream_chat(self, messages: list[dict[str, str]], max_tokens: int | None = None):
        if not self.port or not self._ready():
            raise EngineError("The AI engine is still starting or has stopped.")
        request_messages = [dict(message) for message in messages]
        payload = json.dumps(
            {
                "model": "local-model",
                "messages": request_messages,
                "stream": True,
                "max_tokens": max_tokens or (self.memory_profile or select_memory_profile()).max_output_tokens,
                "temperature": 0.35,
                "top_p": 0.9,
                "top_k": 20,
                "presence_penalty": 0.2,
                "chat_template_kwargs": {"enable_thinking": False},
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/v1/chat/completions",
            data=payload,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.password}",
            },
        )
        if not self._generation_lock.acquire(blocking=False):
            raise EngineError("Another AI response is already being generated. Stop it or wait for it to finish.")
        started = time.perf_counter()
        first_token: float | None = None
        characters = 0
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                for raw_line in response:
                    line = raw_line.decode("utf-8", errors="replace").strip()
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].lstrip()
                    if data == "[DONE]":
                        break
                    event = json.loads(data)
                    delta = event.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content") or ""
                    if content:
                        if first_token is None:
                            first_token = time.perf_counter()
                        characters += len(content)
                        yield content
            elapsed = time.perf_counter() - started
            if characters == 0:
                raise EngineError("The local model completed without returning visible text. Try again or load another model.")
            performance = self._performance()
            self.last_generation = {
                "seconds": round(elapsed, 3),
                "time_to_first_token_seconds": round((first_token or time.perf_counter()) - started, 3),
                "characters": characters,
                "prompt_tokens": performance.get("last_input_count"),
                "generated_tokens": performance.get("last_token_count"),
                "prompt_tokens_per_second": performance.get("last_process_speed"),
                "tokens_per_second": performance.get("last_eval_speed"),
                "completed": True,
            }
        except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
            self.last_generation = {"seconds": round(time.perf_counter() - started, 3), "completed": False, "error": str(exc)}
            raise EngineError(f"Local AI generation failed or timed out: {exc}") from exc
        finally:
            self._generation_lock.release()

    def stop(self) -> None:
        with self._lock:
            process = self.process
            self.process = None
            job_handle = self._job_handle
            self._job_handle = None
            try:
                if process and process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=8)
                    except subprocess.TimeoutExpired:
                        # Keep the kill-on-close job as the final bounded safeguard
                        # for the complete managed process tree.
                        if job_handle:
                            close_job(job_handle)
                            job_handle = None
                        else:
                            process.kill()
                        process.wait(timeout=3)
            finally:
                if job_handle:
                    close_job(job_handle)
            if self._log_handle:
                self._log_handle.close()
                self._log_handle = None
            self._set_status("stopped", "AI engine is stopped.")
            self.backend = "stopped"
            self.acceleration = {**self.acceleration, "actual": "stopped"}
