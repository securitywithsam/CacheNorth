"""Per-computer GPU acceleration policy for CacheNorth.

CPU is the default on every computer. GPU (Vulkan) preferences, failures, and verified
devices are stored per computer, because the USB settings file travels between machines.
A failed GPU attempt is remembered so Windows security prompts are not triggered again
until the user explicitly retries. Nothing here changes Windows security settings.
"""
from __future__ import annotations

import hashlib
import os
import platform
import re
import time
from functools import lru_cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .engine import KoboldEngine
    from .settings import SettingsStore

MODES = ("cpu", "auto_vulkan", "manual_vulkan")
_POLICY_MARKERS = ("winerror 4551", "application control policy has blocked", "0xc0e90002")
_MISSING_DRIVER_MARKERS = ("vulkan-1.dll", "winerror 126", "found 0 vulkan devices", "no vulkan devices", "vk_error_incompatible_driver", "vk_error_initialization_failed")
_DEVICE_LINE = re.compile(r"ggml_vulkan: (\d+) = ([^|\r\n]+?)\s*(?:\||$)", re.MULTILINE)
_USING_DEVICE = re.compile(r"using device Vulkan(\d+) \((.+?)\)(?: \(|\s*-|\s*$)", re.MULTILINE)
_OFFLOADED = re.compile(r"offloaded (\d+)/(\d+) layers to GPU")
_FREE_VRAM = re.compile(r"using device Vulkan\d+ .*? - (\d+) MiB free")


@lru_cache(maxsize=1)
def machine_id() -> str:
    """A privacy-preserving identifier for this Windows installation (hash of MachineGuid)."""
    raw = None
    if os.name == "nt":
        try:
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Cryptography",
                0,
                winreg.KEY_READ | winreg.KEY_WOW64_64KEY,
            ) as key:
                raw = str(winreg.QueryValueEx(key, "MachineGuid")[0])
        except OSError:
            raw = None
    raw = raw or platform.node() or "unknown-computer"
    return hashlib.sha256(f"cachenorth|{raw}".encode("utf-8")).hexdigest()[:16]


def smart_app_control_state() -> str:
    """Read (never change) Windows Smart App Control: 'on', 'evaluation', 'off', or 'unknown'."""
    if os.name != "nt":
        return "unknown"
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\CI\Policy") as key:
            value = winreg.QueryValueEx(key, "VerifiedAndReputablePolicyState")[0]
    except OSError:
        return "unknown"
    return {0: "off", 1: "on", 2: "evaluation"}.get(value, "unknown")


def library_load_stalled(log_text: str) -> bool:
    """True when KoboldCpp's newest output is still the backend-library load line."""
    lines = [line.strip() for line in log_text.splitlines() if line.strip()]
    return bool(lines) and lines[-1].startswith("Initializing dynamic library")


def classify_failure(log_text: str, *, stalled: bool = False, timed_out: bool = False) -> tuple[str, str]:
    text = log_text.lower()
    if any(marker in text for marker in _POLICY_MARKERS):
        return (
            "blocked_by_windows",
            "Windows security blocked an unsigned KoboldCpp GPU component (Smart App Control or an App Control "
            "policy). This is a Windows security decision, not a hardware fault. CacheNorth does not bypass it "
            "and is using CPU mode.",
        )
    if stalled:
        return (
            "library_load_stalled",
            "The GPU component did not finish loading. Windows may have shown a security or error message. "
            "CacheNorth stopped the attempt and is using CPU mode.",
        )
    if any(marker in text for marker in _MISSING_DRIVER_MARKERS):
        return (
            "no_vulkan_device",
            "No usable Vulkan graphics device or driver was found. CacheNorth is using CPU mode.",
        )
    if timed_out:
        return "timeout", "GPU startup did not finish in time. CacheNorth is using CPU mode."
    return (
        "failed",
        "GPU startup failed. CacheNorth is using CPU mode. Details are in Apps\\Offline AI\\Data\\Logs\\koboldcpp.log.",
    )


def parse_vulkan_run(log_text: str) -> dict[str, object]:
    devices = [{"index": int(index), "name": name.strip()} for index, name in _DEVICE_LINE.findall(log_text)]
    devices = list({item["index"]: item for item in devices}.values())
    using = _USING_DEVICE.findall(log_text)
    offloaded = _OFFLOADED.findall(log_text)
    free = _FREE_VRAM.findall(log_text)
    return {
        "devices": devices,
        "device": using[-1][1].strip() if using else None,
        "layers": [int(offloaded[-1][0]), int(offloaded[-1][1])] if offloaded else None,
        "free_mib": int(free[-1]) if free else None,
    }


def load_profile(settings: "SettingsStore", machine: str | None = None) -> dict[str, object]:
    machine = machine or machine_id()
    raw = settings.load().get("computer_profiles", {}).get(machine)
    raw = raw if isinstance(raw, dict) else {}
    mode = raw.get("acceleration_mode")
    device = raw.get("vulkan_device")
    failure = raw.get("vulkan_failure")
    devices = raw.get("vulkan_devices")
    free = raw.get("vulkan_free_mib")
    return {
        "vulkan_free_mib": free if isinstance(free, int) and free > 0 else None,
        "acceleration_mode": mode if mode in MODES else "cpu",
        "vulkan_device": device if isinstance(device, int) and device >= 0 else None,
        "vulkan_failure": failure if isinstance(failure, dict) else None,
        "vulkan_verified": raw.get("vulkan_verified") is True,
        "vulkan_devices": devices if isinstance(devices, list) else [],
    }


def plan_start(profile: dict[str, object], smart_app_control: str, explicit: bool) -> tuple[bool, int | None, str | None]:
    """Return (attempt_vulkan, vulkan_device, reason_cpu_was_chosen)."""
    mode = profile["acceleration_mode"]
    if mode == "cpu":
        return False, None, None
    failure = profile.get("vulkan_failure")
    if failure and not explicit:
        return False, None, (
            "GPU acceleration is paused on this computer after a previous failure: "
            f"{failure.get('message', 'unknown reason')} Choose Apply and restart AI in Settings to try once more."
        )
    if mode == "auto_vulkan" and smart_app_control == "on" and not profile.get("vulkan_verified") and not explicit:
        return False, None, (
            "Automatic GPU was skipped because Windows Smart App Control is on and may block CacheNorth's "
            "unsigned GPU component. CPU mode is active. Choose Manual GPU and apply it to try once."
        )
    return True, profile["vulkan_device"] if mode == "manual_vulkan" else None, None


def start_engine(
    engine: "KoboldEngine",
    settings: "SettingsStore",
    *,
    explicit: bool = False,
    machine: str | None = None,
    smart_app_control: str | None = None,
) -> None:
    """Start the engine with this computer's acceleration and context choices and remember the outcome.

    `explicit` means the user just applied a GPU mode, so a paused GPU may be tried again.
    """
    from . import context as context_planning  # Imported lazily: context imports engine, which imports this module.

    machine = machine or machine_id()
    profile = load_profile(settings, machine)
    sac = smart_app_control or smart_app_control_state()
    attempt_vulkan, device, reason = plan_start(profile, sac, explicit)
    engine.vulkan_device = device
    context_plan = None
    try:
        context_plan = context_planning.plan(
            engine.find_model(),
            settings,
            machine,
            "gpu" if attempt_vulkan else "cpu",
            profile.get("vulkan_free_mib"),
        )
        engine.memory_profile = context_plan.requested
    except Exception:  # Unreadable model metadata must not prevent the RAM-tier default from starting.
        engine.memory_profile = None
    try:
        engine.start(
            prefer_vulkan=attempt_vulkan,
            selected_mode=str(profile["acceleration_mode"]),
            note=reason,
            fallback_profile=context_plan.safe if context_plan else None,
            context_note=context_plan.note if context_plan else None,
        )
    finally:
        status = getattr(engine, "context_status", None) or {}
        if context_plan:
            context_planning.record_outcome(settings, machine, context_plan, status.get("actual"), status.get("reason"))
        if attempt_vulkan:
            result = engine.acceleration
            if result.get("actual") == "gpu" and result.get("device_free_mib"):
                settings.update_profile(machine, {"vulkan_free_mib": result["device_free_mib"]})
            if result.get("failure_kind"):
                settings.update_profile(machine, {
                    "vulkan_failure": {
                        "kind": result["failure_kind"],
                        "message": result.get("reason"),
                        "at": int(time.time()),
                    },
                    "vulkan_devices": result.get("devices") or profile["vulkan_devices"],
                })
            elif result.get("actual") == "gpu":
                settings.update_profile(machine, {
                    "vulkan_failure": None,
                    "vulkan_verified": True,
                    "vulkan_devices": result.get("devices") or profile["vulkan_devices"],
                })
