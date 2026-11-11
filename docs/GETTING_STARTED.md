# Getting started with CacheNorth

**Welcome!** CacheNorth is a portable Windows toolkit for local AI, searchable documents, offline knowledge, maps and guides.

> **Download status:** The full ready-to-run USB package, `CacheNorth-v1.0.3-Full-Portable.zip` (current candidate: **16.9 GiB**), is **coming soon**. It is undergoing release checks, and there is no public download link yet. The current GitHub project is a source preview.

## Which path should I follow?

| What describes you? | Follow this |
|---|---|
| **I want a ready-made offline USB** | Wait for the **Full Portable ZIP** link on the [main page](../README.md#download-cachenorth), then follow the steps below |
| **I have CacheNorth already and want to customize it** | [Customize Your USB — visual folder map and links](CUSTOMIZE_YOUR_USB.md) |
| **I want to find AI models, Wikipedia, maps or PDF guides** | [Content Sources](CONTENT_SOURCES.md) |
| **I want to build the Windows app from source today** | [Build from Source](BUILDING.md), then [Installation](INSTALLATION.md) |
| **Something isn't working** | [Troubleshooting](TROUBLESHOOTING.md) |

## The easy USB setup (once Full ZIP is released)

1. Download the verified **Full Portable ZIP** from [Download CacheNorth](../README.md#download-cachenorth). Do **not** use GitHub's green **Code → Download ZIP** button; that is source code.
2. Extract it to a writable USB drive or folder. Keep the contents together and leave the existing paths unchanged.
3. Open the extracted folder and double-click `Launch CacheNorth.exe`.
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
