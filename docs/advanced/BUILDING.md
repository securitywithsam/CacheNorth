# Building CacheNorth from source

The build produces a portable folder, `dist\CacheNorth-<version>\`, that you copy to a USB drive or any folder. It contains no AI models, archives, or maps; add those afterwards ([INSTALLATION.md](INSTALLATION.md)).

## Prerequisites

| Requirement | Notes |
|---|---|
| Windows 10 or 11, 64-bit | The application and its launcher are Windows-only. |
| PowerShell 5.1 or 7 | Included with Windows. Run scripts with `powershell -ExecutionPolicy Bypass -File ...` if script execution is restricted. |
| .NET Framework 4.8 | Included with Windows 10/11. The build uses its C# compiler (`csc.exe`) for the native launcher; no Visual Studio needed. |
| 64-bit Python 3.12 (3.13 untested) | Optional: `bootstrap.ps1` installs a project-local Python 3.12.8 if none is found. |
| Node.js 18+ | Optional; only for the dashboard JavaScript tests. |
| Internet access | Needed during setup only (see below). |
| Disk space | About 2 GB for the environment, downloads, and build output. |

## Steps

Run from the project folder (any path, spaces are fine):

```powershell
# 1. Python environment with pinned dependencies (PyPI)
powershell -ExecutionPolicy Bypass -File scripts\bootstrap.ps1
#    Use a specific interpreter:  ... bootstrap.ps1 -Python "C:\Path\To\python.exe"

# 2. Third-party runtime inputs, downloaded and SHA-256 verified (GitHub, nuget.org)
powershell -ExecutionPolicy Bypass -File scripts\fetch_third_party.ps1

# 3. Automated tests
powershell -ExecutionPolicy Bypass -File scripts\test.ps1

# 4. Build
powershell -ExecutionPolicy Bypass -File scripts\build.ps1
```

`build.ps1` options:

| Option | Purpose |
|---|---|
| `-OutputDir <folder>` | Build somewhere else (default `dist\CacheNorth-<version>`). |
| `-GpxSeeDir <folder>` | Bundle a portable GPXSee (a folder containing `GPXSee.exe`) as the map viewer. |
| `-GuidesDir <folder>` | Copy the branded `CacheNorth *.pdf` guides into "Start Here" (see below). |
| `-Force` | Replace an existing output folder inside `dist\`. Without it, the build refuses to overwrite. |

## What is downloaded, and from where

| Item | Source | Verification |
|---|---|---|
| Python packages | PyPI, exact versions in `requirements\*.txt` | Version pins; pip's TLS. Hash pinning is a planned improvement. |
| KoboldCpp 1.124.2 (`koboldcpp-nocuda.exe`) | GitHub release `LostRuins/koboldcpp` v1.124.2 | SHA-256 in `third_party\manifest.json` (matches GitHub's published digest); the unpacked folder is verified against a whole-tree hash. |
| WebView2 SDK 1.0.4314.35 | nuget.org | SHA-256 in `third_party\manifest.json` |
| Python 3.12.8 installer (only if needed) | python.org | SHA-256 in `third_party\manifest.json` |

Downloads are kept in `third_party\cache\` (ignored by Git). To build without internet, put the files listed in `third_party\manifest.json` into that folder and run `fetch_third_party.ps1 -Offline`. Files with a wrong hash are never used.

`fetch_third_party.ps1` runs the verified KoboldCpp executable once with `--unpack`. The unpacked runtime is what CacheNorth ships: it avoids the one-file version's temporary `_MEI*` extraction folders.

## PDF guides (optional)

The dashboard's **Quick Start** and **Troubleshooting** buttons open `Start Here\CacheNorth Quick Start Guide.pdf` and `CacheNorth Troubleshooting Guide.pdf`. Without them the buttons show "unavailable", and Markdown copies of the guides are placed in "Start Here" instead. To regenerate the branded PDFs:

1. `bootstrap.ps1 -WithDocs`
2. Run a build with models, start it headless, and capture screenshots with `scripts\capture_headless_screenshots.py` (requires Microsoft Edge).
3. Run `scripts\create_cache_north_guides.py`, then pass `-GuidesDir output\pdf` to `build.ps1`.

These maintainer tools expect screenshots in `output\screenshots-expansion`; adjust the paths at the top of the scripts if needed.

## Tests

| Command | What it covers | Runs in CI |
|---|---|---|
| `scripts\test.ps1` | All Python tests and coverage, dashboard keyboard tests (Node), JavaScript syntax check | Yes |
| `scripts\accept_v101_stage.py --root <build>` | Packaged app: models, switching, citations, Refresh All, shutdown | No: needs models and content |
| `scripts\accept_v102_gpu_policy.py --root <build>` | GPU selection, failure memory, CPU fallback | No: needs a GPU |
| `scripts\accept_v103_context.py --root <build>` | All context sizes, memory estimates, real allocation failure | No: needs models (and a GPU for half the matrix) |
| `scripts\accept_native_xclose_v102.py --root <build>` | Native window close and process cleanup | No: needs a desktop session |

Acceptance scripts write logs, settings, and test conversations into the build you point them at. They refuse removable drives unless you add `--allow-removable`. Run them against a copy, never against a drive holding real data.

## Common build errors

| Message | Fix |
|---|---|
| "The build environment is missing" | Run `bootstrap.ps1` first. |
| "The verified KoboldCpp runtime is missing" / "WebView2 SDK is missing" | Run `fetch_third_party.ps1`. |
| "SHA-256 mismatch" | The download is incomplete or altered. Delete the file from `third_party\cache` and run again. Never bypass this check. |
| "C# compiler was not found" | Enable .NET Framework 4.8 in Windows Features. |
| "... already exists" | Pass `-Force` or choose another `-OutputDir`. |
| PyInstaller is blocked by antivirus | Allow the project folder in your own antivirus only if you trust the source, or build on a clean development machine. |

## Reproducibility notes

- Builds are functionally reproducible from the pinned inputs, but not byte-for-byte identical: PyInstaller embeds timestamps.
- `Apps\Offline AI\BUILD-INFO.txt` records the version, build time, and third-party input hashes of each build.
- Build output (`build\`, `dist\`) and downloads (`third_party\cache\`) stay outside the source tree and are ignored by Git.
