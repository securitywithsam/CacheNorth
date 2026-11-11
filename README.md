<p align="center"><img src="dashboard/cache-north-logo.png" alt="CacheNorth logo" width="120"></p>

# CacheNorth

<p align="center"><strong>Your knowledge. Anywhere.</strong><br>Portable offline AI, knowledge, maps and guides — by <a href="https://github.com/securitywithsam">Security With Sam</a></p>

CacheNorth turns a Windows USB drive into a customizable offline toolkit: chat with a private local AI model, search your documents, browse Kiwix knowledge archives, open regional maps, and keep reference guides close at hand.

> **CacheNorth v1.0.3.1 — free early access.** Portable local AI, knowledge, maps and guides. See [release notes](docs/RELEASE_NOTES.md) and [third-party rights](docs/THIRD_PARTY_LICENSES.md).

## Download CacheNorth

**[Download CacheNorth v1.0.3.1 — Full Portable ZIP](https://downloads.samsonschmidt.com/CacheNorth-v1.0.3.1-Full-Portable.zip)**

- **Windows 10/11 (64-bit)**; tested on Windows 11.
- **Size:** 15,993,029,771 bytes (about 14.9 GiB).
- **SHA-256:** `4D6711127EAC4803756963359AD331CA41150385B300C02D862B48B0094EAAED`
- **Status:** Early access. The filename and checksum were provided by the maintainer; an independent hosted-download check is pending.

### Get started in three steps

1. Download the ZIP using the link above. GitHub's **Code → Download ZIP** contains developer source, not the ready-to-run app.
2. Extract the entire ZIP to a writable folder or USB drive (32 GB or more recommended). Open the extracted `CacheNorth-v1.0.3.1-Full-Portable` folder.
3. Double-click `Launch CacheNorth.exe`. Wait for the dashboard, then try **AI Chat**, **Knowledge Base**, **Maps**, or **Guides**.

Windows may warn about unsigned software. Check the source and checksum, follow your device's security policy, and do not disable security protections to launch it.

For more help, open [Getting Started](docs/GETTING_STARTED.md), [Customize Your USB](docs/CUSTOMIZE_YOUR_USB.md), or [Troubleshooting](docs/TROUBLESHOOTING.md).

### Start here

| I want to… | Open this guide |
|---|---|
| **Add my own models, Wikipedia, maps or PDFs** | **[Customize Your USB — folder map and download links](docs/CUSTOMIZE_YOUR_USB.md)** |
| See beginner setup instructions | [Getting Started](docs/GETTING_STARTED.md) |
| Download specific models, ZIM archives and maps | [Content Sources](docs/CONTENT_SOURCES.md) |
| Troubleshoot or change settings | [Troubleshooting](docs/TROUBLESHOOTING.md) · [Configuration](docs/CONFIGURATION.md) |
| Build CacheNorth myself | [Developer Build Guide](docs/BUILDING.md) |

## Where do my files go?

The drive letter changes between computers. These are the paths **inside the CacheNorth USB/folder**, wherever you extracted it.

| Content | Put files in this folder | File types |
|---|---|---|
| **AI models** | `Apps\Offline AI\Models\` | `.gguf` |
| **Offline knowledge** | `Library\` | `.zim` |
| **Offline maps** | `Maps\` | Mapsforge `.map` |
| **PDF guides** | `Guides\` | `.pdf` |
| **Documents for AI search** | `Apps\Offline AI\Data\Documents\` | `.pdf`, `.txt`, `.md` |

> **[See the complete illustrated USB folder map, exact steps, and official download links →](docs/CUSTOMIZE_YOUR_USB.md)**

You can keep optional folders empty or fill them with content relevant to you. After copying files, open CacheNorth and use **Refresh All** (or **Refresh Documents** for document search). The hosted portable package is designed to avoid developer-tool installation.

### Verify your download

In PowerShell, run:

```powershell
Get-FileHash "C:\\Path\\To\\CacheNorth-v1.0.3.1-Full-Portable.zip" -Algorithm SHA256
```

Compare it with `4D6711127EAC4803756963359AD331CA41150385B300C02D862B48B0094EAAED` or [SHA256SUMS.txt](SHA256SUMS.txt). A matching hash confirms file identity, not safety.

## Pick your offline content

**Bundled models:** Qwen3 1.7B, Qwen3 4B and Qwen3.5 4B have been checked against official published hashes. The model manager currently supports Qwen-family GGUFs only.

| Category | Good starting point | Source |
|---|---|---|
| **AI** | Qwen3 1.7B for lighter computers, or Qwen3 4B for 16 GB+ RAM | [Official Qwen GGUF models](https://huggingface.co/Qwen) |
| **Wikipedia and other knowledge** | Simple English Wikipedia, Wikivoyage, subject-specific archives | [Kiwix Library](https://library.kiwix.org/) |
| **Maps** | A state, country or region you actually need | [Mapsforge map downloads](https://download.mapsforge.org/maps/v5/) |
| **Preparedness guides** | Emergency kit, family plans, weather safety | [Ready.gov](https://www.ready.gov/) · [NWS publications](https://www.weather.gov/owlie/publication_brochures) |

Each category has different file formats and licenses. **[Follow the customization guide](docs/CUSTOMIZE_YOUR_USB.md)** for the correct folders and steps. Downloads require internet upfront; the finished toolkit is designed for offline use.

## Preview the interface

The download includes privacy-reviewed screenshots in its Quick Start and Troubleshooting PDFs; an optional repository README preview is still pending. Until then, the [Getting Started guide](docs/GETTING_STARTED.md) explains what to expect in each section. Never publish a screenshot containing personal chats, machine information, or real document names.

## What it can do

- **Private AI chat:** local GGUF models using KoboldCpp, with CPU-first startup and optional experimental Vulkan GPU acceleration.
- **Ask Documents:** query your PDFs, text and Markdown files, with source references.
- **Knowledge Base:** browse offline `.zim` archives through the optional Kiwix viewer.
- **Offline Maps:** open compatible Mapsforge `.map` files through GPXSee.
- **Guides:** browse your own PDF reference library.
- **Portable layout:** drive-letter-independent paths, refreshable libraries, customizable models and context settings.

## Computer requirements

| | Minimum / status | Better experience |
|---|---|---|
| OS | Windows 10/11, 64-bit; **Windows 11 tested** | Windows 11 64-bit |
| Memory | 8 GB target; physical 8 GB system not yet validated | 16 GB+ |
| CPU | x86-64; AVX2 strongly preferred | Recent 6-core or better |
| Storage | App ~0.4 GB plus models/content | USB 3 drive or external SSD with plenty of space |
| GPU | Optional; CPU works without a dedicated GPU | Vulkan-capable GPU for experimental acceleration |

The native window uses Microsoft Edge WebView2 Runtime; without it, CacheNorth can fall back to the default browser. Windows may warn about unsigned executables, and restricted systems can block components. Do not disable Windows security protections just to run it.

## Licensing and commercial use

Original CacheNorth source and branding remain **all rights reserved**, with limited personal noncommercial early-access use of official builds. See [LICENSE](LICENSE) and [Contributing](CONTRIBUTING.md) for source permissions. Third-party applications, models, archives, maps, and PDFs have independent licenses and permissions; review the [bundled content register](docs/CONTENT_LICENSES.md) and [redistribution matrix](docs/REDISTRIBUTION_MATRIX.md). The iFixit archive carries CC BY-NC-SA terms; future paid bundling requires a separate commercial review or permission from iFixit.

## Important notes

- **Early-access limitations:** This version passed 19 tests on one Windows 11 PC. Windows 10, low-memory systems, GPU mode and downloaded-ZIP security prompts need wider testing. Chromium/Electron source and iFixit noncommercial permissions remain under review. See [release checklist](docs/FULL_PORTABLE_RELEASE_CHECKLIST.md).
- **Privacy:** chats, added documents, and indexes are stored unencrypted on the drive. Keep your USB secure, and never share a personal data-filled copy.
- **Third-party rights:** model weights, ZIM content, map data, PDFs and optional viewers have separate licenses and attribution requirements. A download link does not imply blanket permission to redistribute everything inside.
- **Offline limitations:** model answers may be incorrect, and offline emergency/navigation material can become outdated. Verify critical information.
- **Tested hardware:** the Windows 11 desktop build was tested on an AMD Ryzen 7 7800X3D/RTX 3080 machine. An Intel laptop running Windows build 26200 successfully launched v1.0.3, loaded Qwen3.5 4B on CPU, and shut down. Broader feature testing, Windows 10, 8/16 GB devices and managed PCs remain pending.

## For developers

Want to build, review or modify CacheNorth? See the [Build from Source](docs/BUILDING.md), [Architecture](docs/ARCHITECTURE.md), [Security](SECURITY.md), and [Third-party Licenses](docs/THIRD_PARTY_LICENSES.md) guides. The source is consolidated on `main`. **Source updates do not automatically change the hosted ZIP.** See [Source vs. Hosted ZIP](docs/SOURCE_VS_HOSTED_ZIP.md) and the [v1.0.4 backlog](docs/V104_BACKLOG.md) for version boundaries and deferred fixes. The package has been tested on one PC; it still requires a new hosted ZIP integrity record and remaining redistribution review.

To report a bug, use the repository's issue template and check logs for personal information before sharing them. Security issues should be reported privately via [Security](SECURITY.md).

"CacheNorth", "Security With Sam", and their logos are brand assets and are not covered by any future code license. Third-party trademarks belong to their owners.
