# Installing CacheNorth on a portable drive

This guide assumes you already have a CacheNorth build folder (see [BUILDING.md](BUILDING.md)). Nothing here depends on a particular drive letter: the examples use `E:\`, but CacheNorth finds its files relative to wherever `Launch CacheNorth.exe` is.

## 1. Choose a drive

- Use a USB 3 flash drive or external SSD with at least 16 GB free (32 GB+ if you add large archives). Internal folders work too.
- exFAT or NTFS both work. The drive must be writable: CacheNorth saves conversations, settings, logs, and its document index on the drive.
- Conversations and documents are stored **unencrypted**. If the drive could be lost, use BitLocker To Go or another encrypted drive.

## 2. Copy the build

Copy the whole build folder's contents to the drive root (or any folder). You should see:

```
E:\
├── Launch CacheNorth.exe          ← start here
├── Microsoft.Web.WebView2.*.dll, WebView2Loader.dll
├── Apps\Offline AI\               ← the application (Runtime, Dashboard, KoboldCpp, Models, Data, Documentation)
├── Library\                       ← Kiwix .zim archives
├── Maps\                          ← Mapsforge .map files
├── Guides\                        ← your PDF guides
└── Start Here\                    ← help documents
```

Keep this layout. Moving folders apart breaks the relative paths.

## 3. Add an AI model

CacheNorth does not include model weights. Download at least one GGUF model and copy it into `Apps\Offline AI\Models`. These were tested with v1.0.3:

| Model | File (Q4_K_M) | Size | Good for | Source |
|---|---|---|---|---|
| Qwen3 1.7B | `Qwen3-1.7B-Q4_K_M.gguf` | 1.3 GB | 8 GB computers, older CPUs, fastest | https://huggingface.co/Qwen/Qwen3-1.7B-GGUF |
| Qwen3 4B | `Qwen3-4B-Q4_K_M.gguf` | 2.5 GB | 16 GB computers, better answers | https://huggingface.co/Qwen/Qwen3-4B-GGUF |
| Qwen3.5 4B | `Qwen3.5-4B-Q4_K_M.gguf` | 2.7 GB | 16 GB+ computers, long contexts | https://huggingface.co/unsloth/Qwen3.5-4B-GGUF |

The links are suggested official or well-known sources; check each repository's files and license before downloading. The Qwen3 1.7B and Qwen3.5 4B files tested carry Qwen/Unsloth metadata matching these sources. The Qwen3 4B file tested was a community conversion of an AWQ checkpoint with no license metadata, so the official Qwen GGUF above is recommended instead; it has the same architecture but was not separately benchmarked. All three models are Apache-2.0 licensed upstream; keep each model's license with any copy you share. Other Qwen2/Qwen3/Qwen3.5-architecture GGUF files with a built-in chat template should be detected, but are untested. On the Settings page, **Automatic** picks a model for the computer's RAM, or you can load one manually. Downloading models needs internet; using them does not.

## 4. Start CacheNorth

1. Double-click `Launch CacheNorth.exe`.
2. Wait for "AI engine is ready". The first start on a computer can take a minute.
3. If Windows SmartScreen warns about an unrecognized app, the build is unsigned. Only continue if you built it yourself or got it from Security With Sam.
4. If the Microsoft Edge WebView2 Runtime is missing (some Windows 10 PCs), CacheNorth opens in your default browser instead. CacheNorth never installs it automatically.

To finish, choose **Close CacheNorth** (or close the window), close Kiwix, GPXSee, and any opened files, then use **Safely Remove Hardware**.

## 5. Add your documents

Use **Document Search > Add documents**, or copy PDF, TXT, or Markdown files into `Apps\Offline AI\Data\Documents` and choose **Refresh Documents** (or **Refresh All**). Scanned, image-only PDFs need OCR in another tool first. Then switch AI Chat to **Ask Documents**. Answers show source cards; open the original to confirm anything important.

## 6. Add offline archives (optional)

1. Download the **portable Windows 10/11 Electron executable** from https://github.com/kiwix/kiwix-js-pwa/releases, not the installer or Microsoft Store package. For example, place `Kiwix-JS-Electron-3.9.3-E.exe` directly in `Kiwix\` on your drive (the version may differ). CacheNorth also recognizes the older `Kiwix\kiwix-js-pwa-win32-ia32\Kiwix JS Electron.exe` layout.
2. Download `.zim` archives from https://library.kiwix.org and copy them into `Library\`.
3. Choose **Refresh All**. Each archive shows on the Knowledge Library page.

Check each archive's license before sharing a drive with others; some, such as iFixit (CC BY-NC-SA), forbid commercial use. See [THIRD_PARTY_LICENSES.md](../legal/THIRD_PARTY_LICENSES.md).

## 7. Add offline maps (optional)

1. Download **GPXSee** from https://www.gpxsee.org. To make it portable, put its program files in `Apps\GPXSee\` so that `Apps\GPXSee\GPXSee.exe` exists. Builders can include it with `build.ps1 -GpxSeeDir`.
2. Download Mapsforge `.map` files, for example from https://download.mapsforge.org, and copy them into `Maps\`.
3. Choose **Refresh All**. Map data from OpenStreetMap is © OpenStreetMap contributors under the ODbL; keep that attribution with copies you share.

Maps are for viewing only: no live traffic, closures, or GPS navigation.

## 8. Add guides (optional)

Copy PDF guides into `Guides\`. They appear on the Guides page after **Refresh All**.

## Moving between computers

The drive works on any Windows PC without installation. GPU acceleration and context-length choices are saved **per computer**, so a setting made on a powerful desktop never overloads a laptop. Each new computer starts on CPU with Automatic context.
