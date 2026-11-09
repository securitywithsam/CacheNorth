from __future__ import annotations

import platform
import shutil
import subprocess
import ctypes
from functools import lru_cache
from pathlib import Path

import cpuinfo
import psutil

from .config import AppPaths
from .documents import DocumentIndex
from .engine import KoboldEngine, detect_cpu_profile, select_memory_profile
from .integrations import Integrations


def directory_size(path: Path) -> int:
    if not path.is_dir():
        return 0
    total = 0
    try:
        for item in path.rglob("*"):
            if item.is_file():
                try:
                    total += item.stat().st_size
                except OSError:
                    pass
    except OSError:
        pass
    return total


def storage_identity(root: Path) -> dict[str, object]:
    resolved = root.resolve()
    removable = False
    if platform.system() == "Windows" and resolved.anchor:
        try:
            removable = ctypes.windll.kernel32.GetDriveTypeW(resolved.anchor) == 2  # type: ignore[attr-defined]
        except (AttributeError, OSError):
            removable = False
    development = any((candidate / "pyproject.toml").is_file() for candidate in (resolved, *resolved.parents))
    if removable:
        label, kind = "USB Storage", "usb"
    elif development:
        label, kind = "Development Storage", "development"
    else:
        label, kind = "Local Storage", "local"
    return {"label": label, "kind": kind, "path": str(resolved), "removable": removable}


@lru_cache(maxsize=1)
def _gpu_names() -> tuple[str, ...]:
    names: list[str] = []
    if platform.system() != "Windows":
        return ()
    command = [
        "powershell.exe",
        "-NoLogo",
        "-NoProfile",
        "-NonInteractive",
        "-Command",
        "Get-CimInstance Win32_VideoController -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name",
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=8, check=False)
        physical_markers = ("nvidia", "geforce", "amd", "radeon", "intel", "arc")
        names.extend(
            line.strip() for line in result.stdout.splitlines()
            if line.strip() and any(marker in line.lower() for marker in physical_markers)
        )
    except (OSError, subprocess.TimeoutExpired):
        pass
    return tuple(dict.fromkeys(names))


def gpu_names() -> tuple[str, ...]:
    return _gpu_names()


@lru_cache(maxsize=1)
def _cpu_info() -> dict[str, object]:
    return cpuinfo.get_cpu_info()


def build_system_status(
    paths: AppPaths,
    engine: KoboldEngine,
    documents: DocumentIndex,
    integrations: Integrations,
) -> dict[str, object]:
    memory = psutil.virtual_memory()
    disk = shutil.disk_usage(paths.root)
    storage = storage_identity(paths.root)
    cpu = _cpu_info()
    cpu_profile = engine.cpu_profile
    memory_profile = select_memory_profile(memory.total)
    document_items = documents.list_documents()
    archives = integrations.zim_archives()
    maps = integrations.map_files()
    guides = integrations.guide_files()
    engine_status = engine.status()
    blockers: list[str] = []
    if engine_status.get("model") is None:
        blockers.append("AI model missing")
    try:
        engine.find_executable()
    except Exception:
        blockers.append("KoboldCpp missing")
    if disk.free < 3 * 1024**3:
        blockers.append("Less than 3 GiB free")
    category_sizes = {
        "models": directory_size(paths.models),
        "documents": directory_size(paths.documents),
        "library": directory_size(paths.library),
        "maps": directory_size(paths.maps),
        "guides": directory_size(paths.guides) + directory_size(paths.start_here),
    }
    category_sizes["app"] = max(0, directory_size(paths.product) - category_sizes["models"] - directory_size(paths.data))
    warnings: list[str] = []
    if disk.free < 1024**3:
        warnings.append("Critical: less than 1 GiB of free storage remains.")
    elif disk.free < 3 * 1024**3:
        warnings.append("Low storage: less than 3 GiB of free storage remains.")
    return {
        "engine": engine_status,
        "system": {
            "windows": platform.platform(),
            "architecture": platform.machine(),
            "cpu": cpu.get("brand_raw") or platform.processor() or "Unknown processor",
            "cpu_mode": cpu_profile.mode,
            "logical_processors": psutil.cpu_count(logical=True),
            "ram_total_bytes": memory.total,
            "ram_available_bytes": memory.available,
            "memory_profile": memory_profile.name,
            # Requested and actually running context; the RAM tier is only the automatic ceiling.
            "context_size": (getattr(engine, "context_status", {}) or {}).get("actual") or memory_profile.context_size,
            "context_requested": (getattr(engine, "context_status", {}) or {}).get("requested"),
            "context_running": (getattr(engine, "context_status", {}) or {}).get("actual"),
            "context_mode": (getattr(engine, "context_status", {}) or {}).get("mode"),
            "context_fallback": (getattr(engine, "context_status", {}) or {}).get("fallback"),
            "context_reason": (getattr(engine, "context_status", {}) or {}).get("reason"),
            "gpus": list(_gpu_names()),
        },
        "storage": {"total_bytes": disk.total, "free_bytes": disk.free, "categories": category_sizes, "warnings": warnings, **storage},
        "documents": {
            "count": len(document_items),
            "ready": sum(1 for item in document_items if item["status"] == "ready"),
            "chunks": sum(int(item["chunk_count"]) for item in document_items),
        },
        "library": {"available": integrations.kiwix_executable() is not None, "archives": len(archives)},
        "maps": {"available": integrations.maps_executable() is not None, "files": len(maps)},
        "guides": {"files": len(guides)},
        "offline_ready": not blockers,
        "blockers": blockers,
    }
