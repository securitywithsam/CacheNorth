from __future__ import annotations

import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture
def kit_root(tmp_path: Path) -> Path:
    root = tmp_path / "USB Name [Test] #1"
    product = root / "Apps" / "Offline AI"
    for directory in (
        product / "Runtime",
        product / "Models",
        product / "Dashboard",
        product / "Data",
        root / "Library",
        root / "Maps",
        root / "Kiwix",
    ):
        directory.mkdir(parents=True, exist_ok=True)
    return root
