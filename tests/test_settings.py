from pathlib import Path

from security_with_sam.settings import SettingsStore


def test_settings_default_to_cpu(tmp_path: Path):
    store = SettingsStore(tmp_path / "settings.json")
    settings = store.load()
    assert settings["prefer_vulkan"] is False
    assert settings["acceleration_mode"] == "cpu"
    assert settings["vulkan_device"] is None
    assert settings["model_mode"] == "automatic"


def test_settings_save_vulkan_atomically(tmp_path: Path):
    path = tmp_path / "settings.json"
    store = SettingsStore(path)
    assert store.save({"prefer_vulkan": True})["prefer_vulkan"] is True
    assert store.load()["prefer_vulkan"] is True
    assert not path.with_suffix(".tmp").exists()


def test_manual_vulkan_device_is_saved_portably(tmp_path: Path):
    store = SettingsStore(tmp_path / "settings.json")
    saved = store.save({"acceleration_mode": "manual_vulkan", "vulkan_device": 1})
    assert saved["prefer_vulkan"] is True
    assert saved["vulkan_device"] == 1
