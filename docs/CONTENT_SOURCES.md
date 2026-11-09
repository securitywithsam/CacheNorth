# Models and offline content: trusted starting points

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

1. Get a **Windows Kiwix JS Electron application** from [Kiwix JS releases](https://github.com/kiwix/kiwix-js-pwa/releases). Release asset names and packaging can change. Check the downloaded archive, then arrange the executable at the path in [the installation instructions](INSTALLATION.md#6-add-offline-archives-optional).
2. Browse the [Kiwix library](https://library.kiwix.org) and download one .zim file, such as a suitable Wikipedia edition.
3. Copy the .zim into the USB's `Library\` folder and select **Refresh All**.

**Content rights vary by archive.** Kiwix is a viewer; it does not grant permission to redistribute every archive. Check each archive's information and underlying content license.

## Offline maps (optional)

CacheNorth discovers local map files and opens them with a separately installed map viewer.

1. Get [GPXSee](https://www.gpxsee.org/) from its official site. Arrange a portable Windows copy so `Apps\GPXSee\GPXSee.exe` exists in the finished drive.
2. Download a compatible **Mapsforge .map** file from [Mapsforge downloads](https://download.mapsforge.org/). Choose only the geographic region you need.
3. Copy the .map into `Maps\` and select **Refresh All**.

GPXSee and its bundled dependencies have their own license obligations. OpenStreetMap-derived maps require attribution to [© OpenStreetMap contributors](https://www.openstreetmap.org/copyright). A Map page attribution change is still pending in the application; preserve attribution alongside any map copy.

CacheNorth's maps are offline reference maps, not live traffic or turn-by-turn navigation.

## PDF guides and documents (optional)

- **Your own PDFs, text files, and Markdown:** put them in `Apps\Offline AI\Data\Documents\` to use Ask Documents.
- **Offline PDF references:** add PDFs you are allowed to keep and share to `Guides\` and select **Refresh All**. Source credibility and licensing vary.
- **Public information examples:** [Ready.gov](https://www.ready.gov/), [NOAA](https://www.noaa.gov/), and [US Forest Service](https://www.fs.usda.gov/). Check the terms and any third-party material within a specific document.
- Scanned PDF pages require OCR before CacheNorth can search their text.

## Safety and licensing

- Verify download domains, checksum or signatures where published, and model licenses.
- Avoid uploading your documents or conversations to public bug reports.
- Offline content can become outdated. Verify information that affects health or safety.
- [Installation](INSTALLATION.md) · [Building](BUILDING.md) · [Third-party licensing](THIRD_PARTY_LICENSES.md) · [Troubleshooting](TROUBLESHOOTING.md)