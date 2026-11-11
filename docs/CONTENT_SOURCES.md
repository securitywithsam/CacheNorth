# Models and offline content: trusted starting points

> **New to CacheNorth?** Start with **[Customize Your USB](CUSTOMIZE_YOUR_USB.md)** for a visual folder map and a three-step setup. This page collects the original download sources and important format/licensing details.

## Quick download and folder guide

| Download | File to get | USB destination |
|---|---|---|
| [Qwen GGUF models](https://huggingface.co/Qwen) | One compatible `Q4_K_M.gguf` file | `Apps\Offline AI\Models\` |
| [Kiwix Library](https://library.kiwix.org/) | A `.zim` archive | `Library\` |
| [Mapsforge maps](https://download.mapsforge.org/maps/v5/) | A regional `.map` file | `Maps\` |
| [Ready.gov emergency PDFs](https://www.ready.gov/) | A useful `.pdf` guide | `Guides\` |
| Your own documents | `.pdf`, `.txt`, `.md` | `Apps\Offline AI\Data\Documents\` |

**Add files → open CacheNorth → Refresh All.** Use the documents refresh option for Ask Documents. The full ready-to-run ZIP download link will be posted on the [README](../README.md#download-cachenorth) after release clearance; it is not yet available.


CacheNorth's source repository contains **no AI model weights, ZIM archives, map data, third-party viewers, or personal PDF collection**. You choose and download these separately. Some material can be used personally but has restrictions on redistribution; read the upstream license before copying it into a publicly shared image.

## AI models (required)

CacheNorth needs at least one GGUF model to answer questions. Start with a Q4_K_M file to balance size and memory use.

| Model | Where to find it | Suggested computer |
|---|---|---|
| Qwen3 1.7B (GGUF) | [Qwen official repository](https://huggingface.co/Qwen/Qwen3-1.7B-GGUF) | Smaller/lower-RAM systems |
| Qwen3 4B (GGUF) | [Qwen official repository](https://huggingface.co/Qwen/Qwen3-4B-GGUF) | 16 GB RAM or more preferred |
| Qwen3.5 4B (GGUF) | [Unsloth quantizations](https://huggingface.co/unsloth/Qwen3.5-4B-GGUF) | 16 GB RAM or more preferred |

**How to add a model:** open the model page, select **Files and versions**, download the desired compatible Q4_K_M GGUF file, and copy it to `Apps\Offline AI\Models\` in your finished build. The download is often over 1 GB. Launch CacheNorth and choose the model in Settings if needed.

Do not download an entire model repository by default; some contain many differently quantized multi-gigabyte files. Check the model card and license. The Qwen3 4B conversion originally tested by the developer had unresolved provenance; use the official repository above rather than assuming that specific community conversion is cleared.

## Offline knowledge (optional)

CacheNorth lists .zim files and opens them through Kiwix when the Kiwix viewer is installed.

1. Get the **portable Windows 10/11 Kiwix JS Electron `.exe`** from [Kiwix JS releases](https://github.com/kiwix/kiwix-js-pwa/releases), such as `Kiwix-JS-Electron-3.9.3-E.exe`. Place it in the USB's `Kiwix\` folder. Avoid the installer, `.appx`, and XP/Vista legacy ZIP options. Release names can change; see [installation instructions](INSTALLATION.md#6-add-offline-archives-optional).
2. Browse the [Kiwix library](https://library.kiwix.org) and download one .zim file, such as a suitable Wikipedia edition.
3. Copy the .zim into the USB's `Library\` folder and select **Refresh All**.

**Content rights vary by archive.** Kiwix is a viewer; it does not grant permission to redistribute every archive. Check each archive's information and underlying content license.

## Offline maps (optional)

CacheNorth discovers local map files and opens them with a separately installed map viewer.

1. Get [GPXSee](https://www.gpxsee.org/) from its official site. Arrange a portable Windows copy so `Apps\GPXSee\GPXSee.exe` exists in the finished drive.
2. Download a compatible **Mapsforge .map** file from [Mapsforge downloads](https://download.mapsforge.org/maps/v5/). For example, browse [US state maps](https://download.mapsforge.org/maps/v5/north-america/us/) or download [Minnesota](https://download.mapsforge.org/maps/v5/north-america/us/minnesota.map). Choose only the regions you need.
3. Copy the .map into `Maps\` and select **Refresh All**.

GPXSee and its bundled dependencies have their own license obligations. OpenStreetMap-derived maps require attribution to [© OpenStreetMap contributors](https://www.openstreetmap.org/copyright). A Map page attribution change is still pending in the application; preserve attribution alongside any map copy.

CacheNorth's maps are offline reference maps, not live traffic or turn-by-turn navigation.

## PDF guides and documents (optional)

- **Your own PDFs, text files, and Markdown:** put them in `Apps\Offline AI\Data\Documents\` to use Ask Documents.
- **Offline PDF references:** add PDFs you are allowed to keep and share to `Guides\` and select **Refresh All**. Source credibility and licensing vary.
- **Example official PDF downloads:** [Ready.gov — Are You Ready?](https://www.ready.gov/sites/default/files/2021-11/are-you-ready-guide.pdf), [emergency supply kit checklist](https://www.ready.gov/sites/default/files/2024-05/ready_supply-kit-checklist.pdf), and [family emergency communication plan](https://www.ready.gov/sites/default/files/2020-03/family-emergency-communication-planning-document.pdf).
- **Browse more official sources:** [Ready.gov](https://www.ready.gov/), [National Weather Service safety brochures](https://www.weather.gov/owlie/publication_brochures), [USGS topographic maps](https://www.usgs.gov/programs/national-geospatial-program/topographic-maps), [NOAA](https://www.noaa.gov/), and [US Forest Service](https://www.fs.usda.gov/). Check the terms and any third-party material within each document.
- Scanned PDF pages require OCR before CacheNorth can search their text.

## Safety and licensing

- Verify download domains, checksum or signatures where published, and model licenses.
- Avoid uploading your documents or conversations to public bug reports.
- Offline content can become outdated. Verify information that affects health or safety.
- [Installation](INSTALLATION.md) · [Building](BUILDING.md) · [Third-party licensing](THIRD_PARTY_LICENSES.md) · [Troubleshooting](TROUBLESHOOTING.md)