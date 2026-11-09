from __future__ import annotations

import json
import threading
from pathlib import Path


DEFAULT_SETTINGS: dict[str, object] = {
    "prefer_vulkan": False,
    "acceleration_mode": "cpu",
    "vulkan_device": None,
    "model_mode": "automatic",
    "manual_model": None,
    "computer_profiles": {},
}


_PATH_LOCKS: dict[str, threading.RLock] = {}
_PATH_LOCKS_GUARD = threading.Lock()


class SettingsStore:
    def __init__(self, path: Path):
        self.path = path
        # The controller and the web app each create a store for the same file; sharing one lock per
        # file keeps their read-modify-write updates from overwriting each other.
        with _PATH_LOCKS_GUARD:
            self._lock = _PATH_LOCKS.setdefault(str(Path(path).resolve()).casefold(), threading.RLock())

    def load(self) -> dict[str, object]:
        with self._lock:
            if not self.path.is_file():
                return dict(DEFAULT_SETTINGS)
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return dict(DEFAULT_SETTINGS)
            mode = raw.get("model_mode", "automatic")
            profiles = raw.get("computer_profiles", {})
            legacy_vulkan = bool(raw.get("prefer_vulkan", False))
            acceleration = raw.get("acceleration_mode", "auto_vulkan" if legacy_vulkan else "cpu")
            return {
                "prefer_vulkan": acceleration in {"auto_vulkan", "manual_vulkan"},
                "acceleration_mode": acceleration if acceleration in {"cpu", "auto_vulkan", "manual_vulkan"} else "cpu",
                "vulkan_device": raw.get("vulkan_device") if isinstance(raw.get("vulkan_device"), int) and raw.get("vulkan_device") >= 0 else None,
                "model_mode": mode if mode in {"automatic", "manual"} else "automatic",
                "manual_model": raw.get("manual_model") if isinstance(raw.get("manual_model"), str) else None,
                "computer_profiles": profiles if isinstance(profiles, dict) else {},
            }

    def save(self, values: dict[str, object]) -> dict[str, object]:
        with self._lock:  # Hold the lock across load and write so concurrent saves cannot lose updates.
            return self._save(values)

    def _save(self, values: dict[str, object]) -> dict[str, object]:
        current = self.load()
        merged = {**current, **values}
        mode = merged.get("model_mode", "automatic")
        profiles = merged.get("computer_profiles", {})
        acceleration = values.get("acceleration_mode") if "acceleration_mode" in values else None
        if acceleration is None and "prefer_vulkan" in values:
            acceleration = "auto_vulkan" if bool(values["prefer_vulkan"]) else "cpu"
        if acceleration is None:
            acceleration = merged.get("acceleration_mode")
        if acceleration not in {"cpu", "auto_vulkan", "manual_vulkan"}:
            acceleration = "auto_vulkan" if bool(merged.get("prefer_vulkan", False)) else "cpu"
        device = merged.get("vulkan_device")
        settings: dict[str, object] = {
            "prefer_vulkan": acceleration in {"auto_vulkan", "manual_vulkan"},
            "acceleration_mode": acceleration,
            "vulkan_device": device if isinstance(device, int) and device >= 0 else None,
            "model_mode": mode if mode in {"automatic", "manual"} else "automatic",
            "manual_model": merged.get("manual_model") if isinstance(merged.get("manual_model"), str) else None,
            "computer_profiles": profiles if isinstance(profiles, dict) else {},
        }
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_suffix(".tmp")
            temporary.write_text(json.dumps(settings, indent=2), encoding="utf-8")
            temporary.replace(self.path)
        return settings

    def update_profile(self, machine: str, changes: dict[str, object]) -> dict[str, object]:
        """Merge changes into one computer's profile. GPU choices never apply to other computers."""
        with self._lock:
            profiles = dict(self.load().get("computer_profiles", {}))
            profile = dict(profiles.get(machine) or {})
            profile.update(changes)
            profiles[machine] = profile
            # The shared top-level acceleration keys are legacy (v1.0.1) and are neutralized to CPU so that
            # neither this release nor a rollback applies one computer's GPU choice to another computer.
            self.save({"computer_profiles": profiles, "acceleration_mode": "cpu", "vulkan_device": None})
            return profile
