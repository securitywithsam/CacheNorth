<p align="center"><img src="dashboard/cache-north-logo.png" alt="CacheNorth logo" width="120"></p>

# CacheNorth

**Your knowledge. Anywhere.** · By [Security With Sam](https://github.com/securitywithsam)

> **Source preview:** v1.0.3 is still undergoing release checks. There is no official downloadable Windows package or preassembled USB image yet. Start with [Getting Started](docs/GETTING_STARTED.md).

CacheNorth is a portable, offline-first Windows application that runs a private AI assistant on your own computer, answers questions from your own documents with source citations, and opens offline reference libraries and maps. It runs from a USB drive or any folder, needs no account or cloud service, and keeps your conversations on your drive.

> **Status:** v1.0.3. Developed and tested on Windows 11. See [Tested hardware](#tested-hardware) before relying on it elsewhere.
> **License:** not yet chosen. Until a license is published, all rights are reserved by Security With Sam. See [docs/LICENSE_RECOMMENDATION.md](docs/LICENSE_RECOMMENDATION.md).

## Choose your path

| Goal | Guide |
|---|---|
| **Get started as a beginner** | [Getting Started](docs/GETTING_STARTED.md) |
| **Build the Windows app** | [Build from Source](docs/BUILDING.md) |
| **Set up a USB and AI model** | [Installation](docs/INSTALLATION.md) |
| **Find models, Wikipedia, maps and guides** | [Content Sources](docs/CONTENT_SOURCES.md) |
| **Change settings or troubleshoot** | [Configuration](docs/CONFIGURATION.md) · [Troubleshooting](docs/TROUBLESHOOTING.md) |

## What it does

- **Private AI chat** with local GGUF models (Qwen3 1.7B, Qwen3 4B, Qwen3.5 4B tested) through [KoboldCpp](https://github.com/LostRuins/koboldcpp). Nothing is sent to the internet.
- **Ask Documents:** add PDF, TXT, or Markdown files and get answers with source cards showing the file, page, and passage used.
- **Knowledge Library:** opens Kiwix `.zim` archives (Wikipedia, medical, repair, and more) in Kiwix JS.
- **Offline Maps:** opens Mapsforge `.map` files in GPXSee.
- **Guides:** lists PDF guides you copy to the drive.
- **Hardware-aware:** CPU by default with AVX2/AVX/fallback detection. Optional Vulkan GPU acceleration (NVIDIA, AMD, Intel) is chosen per computer and falls back to CPU automatically.
- **Configurable context length** (Automatic, 2K–32K tokens) with memory estimates for each option.
- **Portable:** works from any drive letter or folder, including paths with spaces, and closes cleanly so the drive can be removed.

## Requirements

| | Minimum | Recommended |
|---|---|---|
| Windows | Windows 10 or 11, 64-bit (only Windows 11 has been tested) | Windows 11 64-bit |
| Processor | 64-bit x86 CPU (AVX2 strongly recommended) | Recent 6+ core CPU with AVX2 |
| Memory | 8 GB (Qwen3 1.7B, 2K context; untested on physical 8 GB machines) | 16 GB or more |
| Storage | ~0.4 GB for the app + 1.3–2.8 GB per model | 32 GB+ USB 3 drive or SSD |
| Graphics | Not required | Optional Vulkan-capable GPU |
| Other | Microsoft Edge WebView2 Runtime (included with Windows 11) for the built-in window; otherwise your browser is used | |

## Quick start (users)

**There is no ready-to-run release yet.** The currently available project is source code; building requires a Windows development computer. See [Getting Started](docs/GETTING_STARTED.md) first.

1. Build CacheNorth (below) or obtain a build from Security With Sam.
2. Copy the build folder to a USB drive or any folder.
3. Add at least one GGUF model to `Apps\Offline AI\Models` ([docs/INSTALLATION.md](docs/INSTALLATION.md#3-add-an-ai-model)).
4. Double-click **`Launch CacheNorth.exe`**.

Full instructions: **[docs/INSTALLATION.md](docs/INSTALLATION.md)**.

## Build from source (developers)

```powershell
git clone https://github.com/securitywithsam/CacheNorth.git
cd CacheNorth
powershell -ExecutionPolicy Bypass -File scripts\bootstrap.ps1          # Python environment (internet)
powershell -ExecutionPolicy Bypass -File scripts\fetch_third_party.ps1  # KoboldCpp + WebView2, hash-verified (internet)
powershell -ExecutionPolicy Bypass -File scripts\test.ps1               # automated tests
powershell -ExecutionPolicy Bypass -File scripts\build.ps1              # creates dist\CacheNorth-1.0.3
```

Details, prerequisites, and options: **[docs/BUILDING.md](docs/BUILDING.md)**.

## Documentation

| Document | Contents |
|---|---|
| [GETTING_STARTED.md](docs/GETTING_STARTED.md) | Choose the correct setup path and see what is included |
| [CONTENT_SOURCES.md](docs/CONTENT_SOURCES.md) | Verified source links for AI models, Kiwix, maps and optional guides |
| [INSTALLATION.md](docs/INSTALLATION.md) | Set up a portable drive, add models, documents, archives, maps, and guides |
| [BUILDING.md](docs/BUILDING.md) | Build the Windows application from source; tests |
| [CONFIGURATION.md](docs/CONFIGURATION.md) | Settings, GPU acceleration, context length, data locations, customization |
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common problems and fixes |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | How the pieces fit together |
| [THIRD_PARTY_LICENSES.md](docs/THIRD_PARTY_LICENSES.md) | Third-party components, licenses, and redistribution notes |
| [RELEASE_NOTES.md](docs/RELEASE_NOTES.md) | Version history |
| [SECURITY.md](SECURITY.md) | Security model and how to report vulnerabilities |

## What needs the internet

Only setup. Building needs PyPI, GitHub (KoboldCpp), and nuget.org (WebView2). Getting models, archives, maps, and viewers needs their download sites. **Running CacheNorth needs no internet.** Some third-party components may contact their own services when a connection exists (for example, the WebView2 runtime and Kiwix JS's update check). See [SECURITY.md](SECURITY.md).

## Tested hardware

Physically tested on Windows 11 with:

- an AMD Ryzen 7 7800X3D desktop (32 GB, NVIDIA RTX 3080 and AMD integrated Vulkan);
- an Intel Core laptop (Comet Lake class) with Intel UHD Graphics. Field logs cover v1.0.1–v1.0.2; owner testing of v1.0.3 on it is pending.

Windows 10, physical 8 GB and 16 GB machines, older AVX-only or non-AVX processors, and managed corporate PCs have **not** been tested.

## Reporting bugs

Open an issue using the **Bug report** template. Include your Windows version, CPU, RAM, CacheNorth version, the exact error, and the last lines of `Apps\Offline AI\Data\Logs\koboldcpp.log`. Check logs for personal content before posting. Report security issues privately as described in [SECURITY.md](SECURITY.md).

## Before sharing or distributing

The source repository excludes model weights, ZIM archives, maps, third-party viewers and user data. Download these components separately, follow their individual licenses, and do not assume packaged distributions are cleared. [License details](docs/THIRD_PARTY_LICENSES.md).

## Branding

"CacheNorth", "Security With Sam", and their logos identify this project and are not covered by any open-source license that may be chosen for the code. Third-party names and trademarks belong to their owners.
