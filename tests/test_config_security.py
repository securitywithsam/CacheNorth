from __future__ import annotations

from pathlib import Path

import pytest

from security_with_sam.config import AppPaths, resolve_root
from security_with_sam.security import allowed_local_host, confined_path, safe_filename


def test_explicit_root_supports_spaces_and_special_characters(kit_root: Path):
    assert resolve_root(kit_root) == kit_root.resolve()
    paths = AppPaths.from_root(kit_root)
    paths.ensure_writable_data()
    assert paths.documents.is_dir()


def test_read_only_or_invalid_data_path_has_clear_error(kit_root: Path):
    data = kit_root / "Apps" / "Offline AI" / "Data"
    data.rmdir()
    data.write_text("blocks directory creation", encoding="utf-8")
    with pytest.raises(RuntimeError, match="read-only or unavailable"):
        AppPaths.from_root(kit_root).ensure_writable_data()


@pytest.mark.parametrize("name", ["report.pdf", "notes.txt", "guide.md", "A file (final) [1].PDF"])
def test_safe_filename_accepts_supported_files(name: str):
    assert safe_filename(name).lower().endswith((".pdf", ".txt", ".md"))


@pytest.mark.parametrize("name", ["program.exe", "archive.zim", "image.png", ""])
def test_safe_filename_rejects_unsupported_files(name: str):
    with pytest.raises(ValueError):
        safe_filename(name)


def test_safe_filename_removes_path_traversal():
    assert safe_filename("../../private/report.pdf") == "report.pdf"


def test_confined_path_rejects_escape(tmp_path: Path):
    base = tmp_path / "base"
    base.mkdir()
    with pytest.raises(ValueError, match="outside"):
        confined_path(base, tmp_path / "outside.txt")


@pytest.mark.parametrize("host", ["127.0.0.1:5000", "localhost:8080", "[::1]:9000"])
def test_loopback_hosts_allowed(host: str):
    assert allowed_local_host(host)


@pytest.mark.parametrize("host", ["192.168.1.5:5000", "example.com", "0.0.0.0:5000", None])
def test_non_loopback_hosts_rejected(host: str | None):
    assert not allowed_local_host(host)
