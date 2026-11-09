from pathlib import Path

from security_with_sam.system_status import storage_identity


def test_development_storage_is_labeled_without_claiming_usb(tmp_path: Path):
    project = tmp_path / "CacheNorth Dev"
    root = project / "build" / "integration-root"
    root.mkdir(parents=True)
    (project / "pyproject.toml").write_text("[project]\nname='cache-north'\n", encoding="utf-8")
    identity = storage_identity(root)
    assert identity["label"] == "Development Storage"
    assert identity["kind"] == "development"


def test_non_project_fixed_storage_is_not_mislabeled_usb(tmp_path: Path):
    root = tmp_path / "portable-copy"
    root.mkdir()
    identity = storage_identity(root)
    assert not (identity["label"] == "USB Storage" and identity["removable"] is False)
