from __future__ import annotations

import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


PRODUCT_DIR = Path("Apps") / "Offline AI"


def _executable_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def resolve_root(explicit_root: str | os.PathLike[str] | None = None) -> Path:
    """Resolve the USB/release root without a fixed drive letter or username."""
    if explicit_root:
        return Path(explicit_root).expanduser().resolve()
    env_root = os.environ.get("SWS_OFFLINE_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()

    start = _executable_dir()
    candidates = (start, *start.parents)
    for candidate in candidates:
        if (candidate / PRODUCT_DIR).is_dir():
            return candidate

    # Development default: repository-local simulated release root.
    return (Path(__file__).resolve().parents[2] / "build" / "dev-root").resolve()


@dataclass(frozen=True)
class AppPaths:
    root: Path
    product: Path
    runtime: Path
    dashboard: Path
    models: Path
    data: Path
    documents: Path
    index: Path
    chats: Path
    logs: Path
    library: Path
    maps: Path
    kiwix: Path
    guides: Path
    start_here: Path

    @classmethod
    def from_root(cls, root: Path) -> "AppPaths":
        product = root / PRODUCT_DIR
        data = product / "Data"
        return cls(
            root=root,
            product=product,
            runtime=product / "Runtime",
            dashboard=product / "Dashboard",
            models=product / "Models",
            data=data,
            documents=data / "Documents",
            index=data / "Index",
            chats=data / "Chats",
            logs=data / "Logs",
            library=root / "Library",
            maps=root / "Maps",
            kiwix=root / "Kiwix",
            guides=root / "Guides",
            start_here=root / "Start Here",
        )

    def ensure_writable_data(self) -> None:
        probe = self.data / ".write-test"
        try:
            for directory in (self.data, self.documents, self.index, self.chats, self.logs):
                directory.mkdir(parents=True, exist_ok=True)
            probe.write_bytes(b"ok")
        except OSError as exc:
            raise RuntimeError(
                "The CacheNorth data folder is read-only or unavailable. "
                "Copy the kit to writable media or remove write protection before using AI chat or document search."
            ) from exc
        finally:
            try:
                probe.unlink(missing_ok=True)
            except OSError:
                pass


def discover_paths(explicit_root: str | os.PathLike[str] | None = None) -> AppPaths:
    return AppPaths.from_root(resolve_root(explicit_root))


def ensure_temporary_storage(minimum_free_bytes: int = 512 * 1024 * 1024) -> Path:
    temp = Path(tempfile.gettempdir()).resolve()
    probe = temp / f"cache-north-{os.getpid()}.tmp"
    try:
        probe.write_bytes(b"temporary storage test")
        free = shutil.disk_usage(temp).free
        if free < minimum_free_bytes:
            raise RuntimeError(
                f"Windows temporary storage has only {free / (1024**2):.0f} MiB free. "
                f"At least {minimum_free_bytes / (1024**2):.0f} MiB is required to start the AI engine safely."
            )
    except OSError as exc:
        raise RuntimeError(
            "Windows temporary storage is unavailable or read-only. The AI engine needs writable temporary storage."
        ) from exc
    finally:
        try:
            probe.unlink(missing_ok=True)
        except OSError:
            pass
    return temp
