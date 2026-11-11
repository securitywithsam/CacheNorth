> **v1.0.3.1 uploaded-artifact metadata (owner reported):** [CacheNorth-v1.0.3.1-Full-Portable.zip](https://downloads.samsonschmidt.com/CacheNorth-v1.0.3.1-Full-Portable.zip) — **15,993,029,771 bytes** (15.99 GB decimal; ~14.90 GiB), SHA-256 `4D6711127EAC4803756963359AD331CA41150385B300C02D862B48B0094EAAED`. The URL follows the existing Cloudflare R2 custom-domain naming pattern, but **the new download has not yet been independently fetched or verified**. Verify the hosted copy before announcing it. The old v1.0.3 ZIP remains a separate historical artifact.

# Getting started with CacheNorth

**Welcome!** CacheNorth is a portable Windows toolkit for local AI, searchable documents, offline knowledge, maps and guides.

 > **Download status:** The [v1.0.3.1 cleaned ZIP](https://downloads.samsonschmidt.com/CacheNorth-v1.0.3.1-Full-Portable.zip) is the intended current package (owner-reported local size and SHA-256 above). The link and hosted bytes need independent verification; rights and cross-PC checks remain open.

## Which path should I follow?

| What describes you? | Follow this |
|---|---|
| **I want a ready-made offline USB** | Use the **hosted Full Portable ZIP** link on the [main page](../README.md#download-cachenorth), noting that licensing, privacy, and hardware acceptance checks remain open, then follow the steps below |
| **I have CacheNorth already and want to customize it** | [Customize Your USB — visual folder map and links](CUSTOMIZE_YOUR_USB.md) |
| **I want to find AI models, Wikipedia, maps or PDF guides** | [Content Sources](CONTENT_SOURCES.md) |
| **I want to build the Windows app from source today** | [Build from Source](BUILDING.md), then [Installation](INSTALLATION.md) |
| **Something isn't working** | [Troubleshooting](TROUBLESHOOTING.md) |

## The easy USB setup (hosted preview)

1. Download the **Full Portable ZIP** with a matching hosted-copy SHA-256 from [Download CacheNorth](../README.md#download-cachenorth). Do **not** use GitHub's green **Code → Download ZIP** button; that is source code.
2. Extract it to a writable USB drive or folder. **Open the extracted `CacheNorth-v1.0.3.1-Full-Portable` folder** and keep its contents together.
3. Inside that folder, double-click `Launch CacheNorth.exe`.
4. Explore **AI Chat**, **Knowledge Base**, **Maps**, and **Guides**. CacheNorth is designed to work offline after its resources have been downloaded.
5. Want to add your own files? Open [Customize Your USB](CUSTOMIZE_YOUR_USB.md), copy files into the indicated folders, and choose **Refresh All**.

**You choose the content.** Keep just a small AI model and a few guides, or add regional maps and larger knowledge libraries. You don't need to fill every folder.

## Quick USB folder cheat sheet

| Add | Folder on the USB |
|---|---|
| AI model (.gguf) | `Apps\Offline AI\Models\` |
| Knowledge archive (.zim) | `Library\` |
| Mapsforge map (.map) | `Maps\` |
| Reading PDF | `Guides\` |
| PDF/TXT/MD you want AI to search | `Apps\Offline AI\Data\Documents\` |

For the full folder map, model size suggestions, specific download links, and Kiwix/GPXSee viewer setup, see **[Customize Your USB](CUSTOMIZE_YOUR_USB.md)**.

## If you want to build now

This v1.0.3 source preview requires a Windows development machine. See [Build from Source](BUILDING.md) for prerequisites, verified third-party dependency downloads, automated tests and build commands. Then use [Installation](INSTALLATION.md) to copy the generated build onto your USB.

The source repository does not include AI weights, ZIM archives, maps, personal documents or a ready-to-run executable package.

## Safety and compatibility

- Windows 11 is tested; Windows 10 and several lower-memory/managed configurations still need validation.
- The app is currently unsigned; Windows may warn about or block components. Do not weaken Windows security to install it.
- Chats, documents, indexes and settings can contain private information and are stored unencrypted on the USB. Never publicly upload a personal drive copy.
- Download from the original project/provider pages and verify file licenses, sizes and integrity where available. Rights vary for ZIMs, maps and PDFs.
- Local AI can make mistakes and offline knowledge can become outdated. Verify critical medical, emergency and navigation information.

**Next:** [Customize Your USB](CUSTOMIZE_YOUR_USB.md) · [Content Sources](CONTENT_SOURCES.md) · [Troubleshooting](TROUBLESHOOTING.md)
