"""Copy the license files of every bundled Python runtime package (and Python itself) into one folder."""
from __future__ import annotations

import argparse
import importlib.metadata
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DISTRIBUTIONS = (
    "Flask",
    "Werkzeug",
    "Jinja2",
    "MarkupSafe",
    "itsdangerous",
    "click",
    "colorama",
    "blinker",
    "pypdf",
    "psutil",
    "py-cpuinfo",
    "waitress",
    "cryptography",
    "cffi",
    "pycparser",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "build" / "runtime-licenses")
    output = parser.parse_args().output.resolve()
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"{output} is not empty; choose an empty or new folder.")
    output.mkdir(parents=True, exist_ok=True)
    python_license = Path(sys.base_prefix) / "LICENSE.txt"
    if not python_license.is_file():
        raise SystemExit(f"Python's LICENSE.txt was not found at {python_license}.")
    version = ".".join(str(part) for part in sys.version_info[:3])
    shutil.copy2(python_license, output / f"Python-{version}-LICENSE.txt")
    for name in RUNTIME_DISTRIBUTIONS:
        distribution = importlib.metadata.distribution(name)
        destination = output / f"{distribution.metadata['Name']}-{distribution.version}"
        destination.mkdir()
        license_files = [
            path for path in (distribution.files or ())
            if path.name.lower().startswith(("license", "copying", "notice"))
        ]
        if not license_files:
            raise RuntimeError(f"No packaged license file found for {name} {distribution.version}")
        for relative in license_files:
            source = Path(distribution.locate_file(relative))
            if source.is_file():
                target = destination / source.name
                if target.exists():
                    target = destination / f"{source.parent.name}-{source.name}"
                shutil.copy2(source, target)
    print(f"Collected runtime license files in {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
