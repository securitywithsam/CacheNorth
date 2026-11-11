<p align="center"><img src="dashboard/cache-north-logo.png" alt="CacheNorth logo" width="120"></p>

# CacheNorth

<p align="center"><strong>Your knowledge. Anywhere.</strong><br>Portable offline AI, knowledge, maps and guides — by <a href="https://github.com/securitywithsam">Security With Sam</a></p>

CacheNorth turns a Windows USB drive into a customizable offline toolkit: chat with a private local AI model, search your documents, browse Kiwix knowledge archives, open regional maps, and keep reference guides close at hand.

> **Release status: v1.0.3.1 package preparation.** A cleaned portable build has passed the maintainer's 19 functional tests; further hardware and redistribution checks remain. The existing v1.0.3 URL below is the **original archived package**, not the cleaned build. See [v1.0.3.1 package notes](docs/V1031_RELEASE_CANDIDATE.md). Original CacheNorth code retains its limited proprietary early-access license; third-party components retain their own licenses.

## Download CacheNorth

**New cleaned v1.0.3.1 download: pending upload and checksum.** Please wait for the verified link before treating it as the current package. The existing link below points to the original v1.0.3 archive.

| Package | What you get | Status |
|---|---|---|
| **[Original v1.0.3 ZIP (historical)](https://downloads.samsonschmidt.com/CacheNorth-v1.0.3-Full-Portable.zip)** — `CacheNorth-v1.0.3-Full-Portable.zip` | Ready-to-run app and offline content; candidate archive **approximately 16.9 GiB** (exact file length not independently recorded; prior byte count was reported as *size on disk*) | **Original v1.0.3 only; superseded by locally cleaned candidate (new ZIP pending)** |
| **Source project** | Application code, tests, build scripts and documentation | Available on `main` (private preview); for developers |

**For the original v1.0.3 archive only:** download the hosted Full Portable ZIP → extract it to a writable USB drive or a folder → open the extracted `CacheNorth-v1.0.3-Full-Portable` folder → open `Launch CacheNorth.exe` → customize it with your own models, knowledge, maps and PDFs.

**Important:** GitHub's **Code → Download ZIP** contains the *source project*, not the ready-to-run Full Portable USB package. Do not mistake one for the other.

### Quick setup — original package (new archive pending)

1. Download **Full Portable USB ZIP** from the official link above; **Code → Download ZIP** is source only.
2. Extract the ZIP to a writable USB 3 drive (32 GB or larger recommended for the complete bundle) or a normal folder. **Open the resulting `CacheNorth-v1.0.3-Full-Portable` folder**; keep its contents together.
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

You can keep optional folders empty or fill them with content relevant to you. After copying files, open CacheNorth and use **Refresh All** (or **Refresh Documents** for document search). The hosted portable package is designed to avoid developer-tool installation.

### Verify your download

The original local ZIP and a separate copy downloaded from `downloads.samsonschmidt.com` produced the same SHA-256:

```text
486824A6BE4B441417BAB6A4AF000FD5312A83602C99F03B7F9D754750791F17
```

On Windows PowerShell, check your copy with `Get-FileHash "C:\Path\To\CacheNorth-v1.0.3-Full-Portable.zip" -Algorithm SHA256`. Match it against [SHA256SUMS.txt](SHA256SUMS.txt). **This verifies delivery integrity, not the package's security or third-party redistribution permissions.**

## Pick your offline content

**Bundled cleaned package:** Qwen3 1.7B, Qwen3 4B and Qwen3.5 4B have been checked against official published hashes. The model manager currently supports Qwen-family GGUFs only.

| Category | Good starting point | Source |
|---|---|---|
| **AI** | Qwen3 1.7B for lighter computers, or Qwen3 4B for 16 GB+ RAM | [Official Qwen GGUF models](https://huggingface.co/Qwen) |
| **Wikipedia and other knowledge** | Simple English Wikipedia, Wikivoyage, subject-specific archives | [Kiwix Library](https://library.kiwix.org/) |
| **Maps** | A state, country or region you actually need | [Mapsforge map downloads](https://download.mapsforge.org/maps/v5/) |
| **Preparedness guides** | Emergency kit, family plans, weather safety | [Ready.gov](https://www.ready.gov/) · [NWS publications](https://www.weather.gov/owlie/publication_brochures) |

Each category has different file formats and licenses. **[Follow the customization guide](docs/CUSTOMIZE_YOUR_USB.md)** for the correct folders and steps. Downloads require internet upfront; the finished toolkit is designed for offline use.

## Preview the interface

The cleaned package includes privacy-reviewed screenshots in its Quick Start and Troubleshooting PDFs; an optional repository README preview is still pending. Until then, the [Getting Started guide](docs/GETTING_STARTED.md) explains what to expect in each section. Never publish a screenshot containing personal chats, machine information, or real document names.

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

- **Early-access limitations:** the maintainer compared the local ZIP and a newly downloaded copy and found matching SHA-256 values. The **original v1.0.3 historical archive** contained generated runtime data; the cleaned v1.0.3.1 candidate removed it. Remaining Chromium/Electron source and iFixit content-rights questions still need resolution before broad distribution. Complete the [Full Portable ZIP checklist](docs/FULL_PORTABLE_RELEASE_CHECKLIST.md) and the [release gate](docs/PUBLIC_RELEASE_GATE.md) before announcing a public launch.
- **Privacy:** chats, added documents, and indexes are stored unencrypted on the drive. Keep your USB secure, and never share a personal data-filled copy.
- **Third-party rights:** model weights, ZIM content, map data, PDFs and optional viewers have separate licenses and attribution requirements. A download link does not imply blanket permission to redistribute everything inside.
- **Offline limitations:** model answers may be incorrect, and offline emergency/navigation material can become outdated. Verify critical information.
- **Tested hardware:** the Windows 11 desktop build was tested on an AMD Ryzen 7 7800X3D/RTX 3080 machine. An Intel laptop running Windows build 26200 successfully launched v1.0.3, loaded Qwen3.5 4B on CPU, and shut down. Broader feature testing, Windows 10, 8/16 GB devices and managed PCs remain pending.

## For developers

Want to build, review or modify CacheNorth? See the [Build from Source](docs/BUILDING.md), [Architecture](docs/ARCHITECTURE.md), [Security](SECURITY.md), and [Third-party Licenses](docs/THIRD_PARTY_LICENSES.md) guides. The source is consolidated on `main`. **Source updates do not change the hosted v1.0.3 ZIP.** See [Source vs. Hosted ZIP](docs/SOURCE_VS_HOSTED_ZIP.md) and the [v1.0.4 backlog](docs/V104_BACKLOG.md) for version boundaries and deferred fixes. The cleaned package has been tested on one PC; it still requires a new hosted ZIP integrity record and remaining redistribution review.

To report a bug, use the repository's issue template and check logs for personal information before sharing them. Security issues should be reported privately via [Security](SECURITY.md).

"CacheNorth", "Security With Sam", and their logos are brand assets and are not covered by any future code license. Third-party trademarks belong to their owners.
