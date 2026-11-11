from __future__ import annotations

from pathlib import Path

import pytest

from security_with_sam.config import AppPaths
from security_with_sam.integrations import Integrations


def test_kiwix_archive_launch_is_confined(monkeypatch, kit_root: Path):
    executable = kit_root / "Kiwix" / "kiwix-js-pwa-win32-ia32" / "Kiwix JS Electron.exe"
    executable.parent.mkdir(parents=True, exist_ok=True)
    executable.write_bytes(b"test")
    archive = kit_root / "Library" / "ready.zim"
    archive.write_bytes(b"zim")
    launches = []
    integration = Integrations(AppPaths.from_root(kit_root))
    monkeypatch.setattr(integration, "_start", lambda exe, arguments=None, environment=None: launches.append((exe, arguments)))
    integration.launch_kiwix("ready.zim")
    assert launches == [(executable, [str(archive.resolve())])]
    with pytest.raises(FileNotFoundError):
        integration.launch_kiwix("missing.zim")


def test_map_launch_rejects_missing_file(monkeypatch, kit_root: Path):
    executable = kit_root / "Apps" / "GPXSee" / "GPXSee.exe"
    executable.parent.mkdir(parents=True, exist_ok=True)
    executable.write_bytes(b"test")
    integration = Integrations(AppPaths.from_root(kit_root))
    monkeypatch.setattr(integration, "_start", lambda *args, **kwargs: None)
    with pytest.raises(FileNotFoundError):
        integration.launch_maps("missing.map")


def test_all_map_files_are_discovered_with_readable_titles(kit_root: Path):
    for name in ("iowa.map", "michigan.map", "minnesota.map", "wisconsin.map"):
        (kit_root / "Maps" / name).write_bytes(b"mapsforge")
    files = Integrations(AppPaths.from_root(kit_root)).map_files()
    assert [item["name"] for item in files] == ["iowa.map", "michigan.map", "minnesota.map", "wisconsin.map"]
    assert [item["title"] for item in files] == ["Iowa", "Michigan", "Minnesota", "Wisconsin"]


def test_known_archive_names_receive_readable_titles(kit_root: Path):
    (kit_root / "Library" / "wikipedia_en-simple_all_maxi_2026-09.zim").write_bytes(b"zim")
    files = Integrations(AppPaths.from_root(kit_root)).zim_archives()
    assert files[0]["title"] == "Simple English Wikipedia"
    assert files[0]["category"] == "Reference"
    assert files[0]["date"] == "2026-09"


def test_guides_are_discovered_with_friendly_titles_and_confined_open(monkeypatch, kit_root: Path):
    guides = kit_root / "Guides"; guides.mkdir()
    (guides / "emergency_disinfection_of_drinking_water_sept2017.pdf").write_bytes(b"pdf")
    integration = Integrations(AppPaths.from_root(kit_root))
    found = integration.guide_files()
    assert found[0]["title"] == "Emergency Disinfection of Drinking Water (2017)"
    opened = []
    monkeypatch.setattr("security_with_sam.integrations.open_local_file", lambda path: opened.append(path))
    integration.open_guide("guides", found[0]["name"])
    assert opened == [(guides / found[0]["name"]).resolve()]
    with pytest.raises(FileNotFoundError):
        integration.open_guide("guides", "..\\outside.pdf")


@pytest.mark.parametrize("relative_name", [
    "Kiwix-JS-Electron-3.9.3-E.exe",
    "Kiwix-JS-Electron.exe",
    "Kiwix-JS-Electron-3.9.3-E/Kiwix JS Electron.exe",
])
def test_current_kiwix_portable_layouts_are_detected(kit_root: Path, relative_name: str):
    executable = kit_root / "Kiwix" / relative_name
    executable.parent.mkdir(parents=True, exist_ok=True)
    executable.write_bytes(b"test")
    assert Integrations(AppPaths.from_root(kit_root)).kiwix_executable() == executable


def test_kiwix_ignores_unknown_executable(kit_root: Path):
    executable = kit_root / "Kiwix" / "unrelated.exe"
    executable.parent.mkdir(parents=True, exist_ok=True)
    executable.write_bytes(b"test")
    assert Integrations(AppPaths.from_root(kit_root)).kiwix_executable() is None
