from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from .config import AppPaths
from .security import confined_path


class Integrations:
    def __init__(self, paths: AppPaths):
        self.paths = paths

    def zim_archives(self) -> list[dict[str, object]]:
        if not self.paths.library.is_dir():
            return []
        return [
            {
                "name": path.name,
                "title": self._archive_title(path),
                "size_bytes": path.stat().st_size,
                "category": self._archive_category(path),
                "date": self._archive_date(path),
            }
            for path in sorted(self.paths.library.glob("*.zim"), key=lambda item: item.name.lower())
        ]

    def map_files(self) -> list[dict[str, object]]:
        if not self.paths.maps.is_dir():
            return []
        allowed = {".map", ".mbtiles", ".pmtiles", ".img", ".kmz", ".tif", ".tiff"}
        return [
            {"name": path.name, "title": path.stem.replace("_", " ").replace("-", " ").title(), "size_bytes": path.stat().st_size}
            for path in sorted(self.paths.maps.iterdir(), key=lambda item: item.name.lower())
            if path.is_file() and path.suffix.lower() in allowed
        ]

    @staticmethod
    def _archive_title(path: Path) -> str:
        stem = path.stem.lower()
        known = {
            "ifixit": "iFixit Repair Guides",
            "medlineplus": "MedlinePlus",
            "ready.gov": "Ready.gov Emergency Preparedness",
            "wikipedia_en-simple": "Simple English Wikipedia",
            "wiktionary_en-simple": "Simple English Wiktionary",
            "based.cooking": "Based Cooking",
            "cloudflare": "Cloudflare Learning Center",
        }
        for marker, title in known.items():
            if marker in stem:
                return title
        return path.stem.replace("_", " ").replace("-", " ").title()

    @staticmethod
    def _archive_category(path: Path) -> str:
        stem = path.stem.lower()
        categories = {
            "ifixit": "Repair",
            "medlineplus": "Health",
            "ready.gov": "Emergency",
            "wikipedia": "Reference",
            "wiktionary": "Reference",
            "based.cooking": "Cooking",
            "cloudflare": "Technology",
        }
        return next((category for marker, category in categories.items() if marker in stem), "Other")

    @staticmethod
    def _archive_date(path: Path) -> str | None:
        match = re.search(r"(20\d{2})[-_](\d{2})(?:[-_](\d{2}))?", path.stem)
        if not match:
            return None
        return "-".join(part for part in match.groups() if part)

    def guide_files(self) -> list[dict[str, object]]:
        results: list[dict[str, object]] = []
        seen: set[str] = set()
        for folder, category in ((self.paths.guides, "Guide"), (self.paths.start_here, "CacheNorth Help")):
            if not folder.is_dir():
                continue
            for path in sorted(folder.glob("*.pdf"), key=lambda item: item.name.lower()):
                key = path.name.casefold()
                if key in seen:
                    continue
                seen.add(key)
                results.append({
                    "name": path.name,
                    "title": self._guide_title(path),
                    "size_bytes": path.stat().st_size,
                    "category": category,
                    "location": "guides" if folder == self.paths.guides else "start_here",
                })
        return results

    @staticmethod
    def _guide_title(path: Path) -> str:
        stem = path.stem.lower()
        known = {
            "emergency_disinfection": "Emergency Disinfection of Drinking Water (2017)",
            "emergency-supply-kit": "Ready.gov Emergency Supply Kit Checklist",
            "emergency supply kit": "Ready.gov Emergency Supply Kit Checklist",
            "bwca": "USFS BWCAW Trip Planning Guide 2023",
        }
        for marker, title in known.items():
            if marker in stem:
                return title
        return path.stem.replace("_", " ").replace("-", " ").strip().title()

    def open_guide(self, location: str, filename: str) -> None:
        folder = self.paths.guides if location == "guides" else self.paths.start_here if location == "start_here" else None
        if folder is None:
            raise ValueError("Unknown guide location.")
        selected = confined_path(folder, folder / Path(filename).name)
        if selected.name != filename or not selected.is_file() or selected.suffix.lower() != ".pdf":
            raise FileNotFoundError("The selected guide is missing.")
        open_local_file(selected)

    def open_folder(self, name: str) -> None:
        folders = {
            "models": self.paths.models,
            "documents": self.paths.documents,
            "library": self.paths.library,
            "maps": self.paths.maps,
            "guides": self.paths.guides,
        }
        folder = folders.get(name)
        if folder is None:
            raise ValueError("Unknown folder.")
        if not folder.is_dir():
            raise FileNotFoundError(f"The {name} folder is unavailable.")
        open_local_file(folder)

    def kiwix_executable(self) -> Path | None:
        # Accept both the legacy v1.0.3 bundled layout and current portable Kiwix JS
        # Electron releases. Restrict discovery to recognized executable names inside
        # the kit's own Kiwix folder; never execute an arbitrary downloaded .exe.
        candidates = (
            self.paths.kiwix / "kiwix-js-pwa-win32-ia32" / "Kiwix JS Electron.exe",
            self.paths.kiwix / "kiwix-desktop.exe",
            self.paths.kiwix / "Kiwix-JS-Electron.exe",
            self.paths.kiwix / "Kiwix JS Electron.exe",
        )
        for candidate in candidates:
            if candidate.is_file():
                return candidate
        if self.paths.kiwix.is_dir():
            for pattern in ("Kiwix-JS-Electron-*.exe", "Kiwix-JS-Electron-*-E.exe"):
                for candidate in sorted(self.paths.kiwix.glob(pattern)):
                    if candidate.is_file():
                        return candidate
            for folder in sorted(self.paths.kiwix.iterdir()):
                if folder.is_dir() and folder.name.lower().startswith(("kiwix-js-electron", "kiwix-js-pwa")):
                    for filename in ("Kiwix JS Electron.exe", "Kiwix-JS-Electron.exe"):
                        candidate = folder / filename
                        if candidate.is_file():
                            return candidate
        return None

    def maps_executable(self) -> Path | None:
        candidates = (
            self.paths.root / "Apps" / "GPXSee" / "GPXSee.exe",
            self.paths.root / "Apps" / "GPXSee" / "gpxsee.exe",
        )
        return next((path for path in candidates if path.is_file()), None)

    @staticmethod
    def _start(executable: Path, arguments: list[str] | None = None, environment: dict[str, str] | None = None) -> None:
        subprocess.Popen(
            [str(executable), *(arguments or [])],
            cwd=executable.parent,
            env=environment,
            close_fds=True,
        )

    def launch_kiwix(self, filename: str | None = None) -> None:
        executable = self.kiwix_executable()
        if executable is None:
            raise FileNotFoundError("Kiwix is missing from the USB.")
        arguments: list[str] = []
        if filename:
            selected = confined_path(self.paths.library, self.paths.library / Path(filename).name)
            if not selected.is_file() or selected.suffix.lower() != ".zim":
                raise FileNotFoundError("The selected knowledge archive is missing.")
            arguments.append(str(selected))
        self._start(executable, arguments)

    def launch_maps(self, filename: str | None = None) -> None:
        executable = self.maps_executable()
        if executable is None:
            raise FileNotFoundError("The portable GPXSee viewer is missing from Apps\\GPXSee.")
        arguments: list[str] = []
        if filename:
            selected = confined_path(self.paths.maps, self.paths.maps / Path(filename).name)
            if not selected.is_file():
                raise FileNotFoundError("The selected map file is missing.")
            arguments.append(str(selected))
        environment = os.environ.copy()
        portable_appdata = self.paths.data / "GPXSee" / "AppData"
        portable_local = self.paths.data / "GPXSee" / "LocalAppData"
        portable_appdata.mkdir(parents=True, exist_ok=True)
        portable_local.mkdir(parents=True, exist_ok=True)
        environment["APPDATA"] = str(portable_appdata)
        environment["LOCALAPPDATA"] = str(portable_local)
        self._start(executable, arguments, environment)


def open_local_file(path: Path) -> None:
    if os.name != "nt":
        raise OSError("Opening files is supported on Windows builds.")
    os.startfile(str(path))  # type: ignore[attr-defined]
