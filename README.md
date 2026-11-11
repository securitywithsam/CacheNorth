<p align="center"><img src="dashboard/cache-north-logo.png" alt="CacheNorth logo" width="120"></p>

# CacheNorth

<p align="center"><strong>Your knowledge. Anywhere.</strong><br>Portable offline AI, knowledge, maps and guides — by <a href="https://github.com/securitywithsam">Security With Sam</a></p>

CacheNorth turns a Windows USB drive into a customizable offline toolkit: chat with a private local AI model, search your documents, browse Kiwix knowledge archives, open regional maps, and keep reference guides close at hand.

> **Release status: v1.0.3 preview.** The full portable package has been uploaded to the download host; **release verification is still in progress**. The repository is private while security, licensing, and compatibility checks are completed. The original CacheNorth code does not yet have a public license. See [release notes](docs/RELEASE_NOTES.md) and [third-party rights](docs/THIRD_PARTY_LICENSES.md).

## Download CacheNorth

| Package | What you get | Status |
|---|---|---|
| **[Full Portable USB ZIP](https://downloads.samsonschmidt.com/CacheNorth-v1.0.3-Full-Portable.zip)** — `CacheNorth-v1.0.3-Full-Portable.zip` | Ready-to-run app and offline content; candidate archive **16.9 GiB (18,183,434,240 bytes)** | **Hosted preview — integrity, licensing and hardware verification pending** |
| **Source project** | Application code, tests, build scripts and documentation | Available on `main` (private preview); for developers |

**For private testing:** download the hosted Full Portable ZIP → extract it to a writable USB drive or a folder → open `Launch CacheNorth.exe` → customize it with your own models, knowledge, maps and PDFs.

**Important:** GitHub's **Code → Download ZIP** contains the *source project*, not the ready-to-run Full Portable USB package. Do not mistake one for the other.

### Quick setup (when the verified ZIP is released)

1. Download **Full Portable USB ZIP** from the official link above; **Code → Download ZIP** is source only.
2. Extract the ZIP, then copy its contents to a writable USB 3 drive (32 GB or larger recommended for the complete bundle). Keep the folder structure intact.
3. Double-click **`Launch CacheNorth.exe`**, wait for the local dashboard, and explore the four libraries.
4. To personalize it, copy `.gguf`, `.zim`, Mapsforge `.map`, or PDF files into the folders below and choose **Refresh All**.

**First run checklist:** Confirm AI Chat responds, open one knowledge archive, view a map and PDF, then repeat the test with Wi-Fi disconnected. Exit CacheNorth and any external viewers before ejecting.

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

You can keep optional folders empty or fill them with content relevant to you. After copying files, open CacheNorth and use **Refresh All** (or **Refresh Documents** for document search). The full portable package, once released, is intended to remove the need to install developer tools.

## Pick your offline content

| Category | Good starting point | Source |
|---|---|---|
| **AI** | Qwen3 1.7B for lighter computers, or Qwen3 4B for 16 GB+ RAM | [Official Qwen GGUF models](https://huggingface.co/Qwen) |
| **Wikipedia and other knowledge** | Simple English Wikipedia, Wikivoyage, subject-specific archives | [Kiwix Library](https://library.kiwix.org/) |
| **Maps** | A state, country or region you actually need | [Mapsforge map downloads](https://download.mapsforge.org/maps/v5/) |
| **Preparedness guides** | Emergency kit, family plans, weather safety | [Ready.gov](https://www.ready.gov/) · [NWS publications](https://www.weather.gov/owlie/publication_brochures) |

Each category has different file formats and licenses. **[Follow the customization guide](docs/CUSTOMIZE_YOUR_USB.md)** for the correct folders and steps. Downloads require internet upfront; the finished toolkit is designed for offline use.

## Preview the interface

A real, privacy-reviewed screenshot of the Windows dashboard will be added before publication. **Do not substitute a mockup for a tested application screenshot.** The [Getting Started guide](docs/GETTING_STARTED.md) describes AI Chat, Knowledge Base, Maps, and Guides in the meantime.

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

## Important notes

- **Hosted archive is not yet release-cleared:** the link above was supplied by the maintainer, but this audit has not independently confirmed its HTTP response, SHA-256, contents, third-party redistribution rights, or hardware acceptance. Complete the [Full Portable ZIP checklist](docs/FULL_PORTABLE_RELEASE_CHECKLIST.md) and the [release gate](docs/PUBLIC_RELEASE_GATE.md) before announcing a public launch.
- **Privacy:** chats, added documents, and indexes are stored unencrypted on the drive. Keep your USB secure, and never share a personal data-filled copy.
- **Third-party rights:** model weights, ZIM content, map data, PDFs and optional viewers have separate licenses and attribution requirements. A download link does not imply blanket permission to redistribute everything inside.
- **Offline limitations:** model answers may be incorrect, and offline emergency/navigation material can become outdated. Verify critical information.
- **Tested hardware:** the Windows 11 desktop build was tested on an AMD Ryzen 7 7800X3D/RTX 3080 machine. Intel laptop field logs cover earlier versions; v1.0.3 validation on that laptop, Windows 10, 8/16 GB devices, and managed PCs remains pending.

## For developers

Want to build, review or modify CacheNorth? See the [Build from Source](docs/BUILDING.md), [Architecture](docs/ARCHITECTURE.md), [Security](SECURITY.md), and [Third-party Licenses](docs/THIRD_PARTY_LICENSES.md) guides. The source is consolidated on `main`. The compiled binary and complete USB package still require separate release approval.

To report a bug, use the repository's issue template and check logs for personal information before sharing them. Security issues should be reported privately via [Security](SECURITY.md).

"CacheNorth", "Security With Sam", and their logos are brand assets and are not covered by any future code license. Third-party trademarks belong to their owners.
