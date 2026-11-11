# Add your own content

**Make your offline USB useful for you.** Pick your AI model, favorite offline knowledge, local maps, and reference guides. Copy each file into the matching folder, then refresh CacheNorth.

**Model compatibility:** CacheNorth v1.0.3.x currently supports Qwen-family GGUF models only; an arbitrary GGUF from another model family may be marked unsupported. The package includes three verified Qwen models.

## Start in three steps

1. **Get CacheNorth.** Download the [Full Portable ZIP](../README.md#download), extract it to a USB drive (or normal folder), open the extracted `CacheNorth-v1.0.3.1-Full-Portable` folder, and double-click `Launch CacheNorth.exe`. For a separate developer workflow, see [Build from source](advanced/BUILDING.md).
2. **Choose what you want offline.** Use the links below to download an AI model, knowledge archives, maps, or PDFs **while you have internet**.
3. **Copy files into the folders shown below.** In CacheNorth, choose **Refresh All** to update your libraries. For document search, use **Refresh Documents** or the add-documents control.

You can leave optional folders empty. Keep their names and locations unchanged. CacheNorth works from different drive letters, so you do not have to use `E:`.

## Your USB folder map

The example shows the files **inside the extracted `CacheNorth-v1.0.3.1-Full-Portable` folder**. Its enclosing USB might be `D:`, `E:`, `F:`, or another drive letter. Do not place the launcher at the drive root unless you intentionally move the entire contents together.

```text
E:\CacheNorth-v1.0.3.1-Full-Portable\  ← Open this extracted folder
│
├── Launch CacheNorth.exe                  ← Double-click to start
├── Apps\
│   ├── Offline AI\
│   │   ├── Models\                        ← AI models (.gguf)
│   │   │   └── your-model.gguf
│   │   └── Data\
│   │       └── Documents\                 ← Your searchable PDF/TXT/MD files
│   └── GPXSee\
│       └── GPXSee.exe                     ← Optional offline map viewer
│
├── Library\                               ← Knowledge bases (.zim)
│   └── your-knowledge.zim
├── Maps\                                  ← Offline Mapsforge maps (.map)
│   └── your-region.map
├── Guides\                                ← PDFs you want to browse
│   └── your-guide.pdf
├── Kiwix\                              ← Bundled offline archive viewer
└── Start Here\                         ← Included help material
```

The application also has other runtime files and folders. **Keep them in place.** Add your downloads to the existing folders; do not move `Launch CacheNorth.exe`, rename application directories, or put your GGUF files into the `Documents` folder.

| What you want to add | File type | Copy it here | Where to use it |
|---|---|---|---|
| Offline AI model | `.gguf` | `Apps\Offline AI\Models` | **AI Chat / Settings → AI Model Manager** |
| Wikipedia, repair, medical or other Kiwix knowledge | `.zim` | `Library` | **Knowledge Library** |
| Regional offline map | `.map` (Mapsforge) | `Maps` | **Offline Maps** |
| Reading guides | `.pdf` | `Guides` | **Guides** |
| Your own searchable documents | `.pdf`, `.txt`, `.md` | `Apps\Offline AI\Data\Documents` | **Document Search** |

## 1. Choose your AI model

You need **at least one model** for offline AI chat. Download one `Q4_K_M` GGUF file from a model page below, not the entire repository.

| Model | Approximate size | A good starting point for | Download |
|---|---:|---|---|
| Qwen3 1.7B | 1.3 GB | Lighter/faster option; smaller RAM computers | [Official Qwen GGUF](https://huggingface.co/Qwen/Qwen3-1.7B-GGUF/tree/main) |
| Qwen3 4B | 2.5 GB | More capable option; 16 GB+ RAM preferred | [Official Qwen GGUF](https://huggingface.co/Qwen/Qwen3-4B-GGUF/tree/main) |
| Qwen3.5 4B | 2.7 GB | Alternative 4B model; 16 GB+ RAM preferred | [Unsloth GGUF](https://huggingface.co/unsloth/Qwen3.5-4B-GGUF) |

**How:** Open the model page → **Files and versions** → select a compatible `Q4_K_M.gguf` file → download → place it in `Apps\Offline AI\Models`. Open CacheNorth, choose **Refresh All**, and select it in **Settings → AI Model Manager**. Available filenames and formats can change; verify the model's license and file details before downloading.

## 2. Add offline knowledge (.zim)

A `.zim` is an offline library archive, used by [Kiwix](https://library.kiwix.org/). You can mix smaller, specialized collections with larger encyclopedias.

- [Browse the Kiwix library](https://library.kiwix.org/) — search for **Simple English Wikipedia**, **Wiktionary**, **Wikivoyage**, and other topics.

**How:** Download the selected `.zim` file → put it in `Library` → choose **Refresh All** → open **Knowledge Library**. Kiwix is bundled in the Full Portable ZIP. Install a separate viewer only if you are building CacheNorth from source.

**Important:** Every ZIM collection has its own content rights. Downloading for personal offline reading does not automatically grant permission to repackage it into a public USB ZIP. Check the archive's license before sharing.

## 3. Add your own local maps (.map)

- [Browse Mapsforge map downloads](https://download.mapsforge.org/maps/v5/) — select a continent, country, or region.
- [United States state maps](https://download.mapsforge.org/maps/v5/north-america/us/) — pick the state you need.
- [Minnesota map](https://download.mapsforge.org/maps/v5/north-america/us/minnesota.map) — example for Minnesota users.

**How:** Download a compatible **Mapsforge `.map`** file → copy to `Maps` → choose **Refresh All** → open **Offline Maps**. This feature uses Mapsforge maps, not arbitrary map images or GPX tracks. GPXSee is included in the Full Portable ZIP at `Apps\GPXSee\GPXSee.exe`.

Map data is based on OpenStreetMap. Keep the attribution **© OpenStreetMap contributors** and [ODbL details](https://www.openstreetmap.org/copyright) with shared copies. These maps do not show live traffic or provide turn-by-turn navigation.

## 4. Add PDF guides

Prefer source pages and official PDFs that you can verify and update when needed.

| Topic | Download/source |
|---|---|
| Emergency preparedness | [Ready.gov — Are You Ready? PDF](https://www.ready.gov/sites/default/files/2021-11/are-you-ready-guide.pdf) |
| Emergency supplies | [Ready.gov — Supply Kit Checklist PDF](https://www.ready.gov/sites/default/files/2024-05/ready_supply-kit-checklist.pdf) |
| Family communication | [Ready.gov — Emergency Communication Plan PDF](https://www.ready.gov/sites/default/files/2020-03/family-emergency-communication-planning-document.pdf) |
| Severe weather | [National Weather Service — Safety publications](https://www.weather.gov/owlie/publication_brochures) |
| Topographic maps | [USGS — Topographic Maps](https://www.usgs.gov/programs/national-geospatial-program/topographic-maps) |

**How:** Download a PDF you trust → copy it into `Guides` → choose **Refresh All** → open **Guides**.

Want the AI to **search and cite** a document instead? Put a copy in `Apps\Offline AI\Data\Documents`, then refresh documents and use **Document Search**. PDFs made entirely of scanned images need OCR first.

## Make it personal: three example setups

| Your goal | Try adding |
|---|---|
| **Small everyday USB** | Qwen3 1.7B + Simple English Wikipedia + personal PDFs |
| **Travel/offline reference USB** | Qwen3 4B + Wikivoyage ZIM + maps of the places you visit + travel PDFs |
| **Preparedness USB** | A compatible model + selected Kiwix references + your regional map + official emergency PDFs |

These are examples, not fixed bundles. Choose content based on your drive's free space, your computer's RAM, and the rights attached to each file.

## After copying your files

1. Safely finish copying all downloads.
2. Launch `Launch CacheNorth.exe`.
3. Choose **Refresh All**; use **Refresh Documents** for Document Search.
4. Confirm the items appear in the corresponding sections.
5. Test at least one AI prompt, one ZIM, one map, and one PDF **with Wi-Fi turned off**.
6. Close CacheNorth and any viewers before safely ejecting the USB.

## Help and safe sharing

- [Getting Started](GETTING_STARTED.md) · [Troubleshooting](TROUBLESHOOTING.md) · [Developer installation](advanced/INSTALLATION.md)
- Models, ZIMs, maps, and PDFs may have separate licensing or redistribution obligations. See [Third-party licensing](legal/THIRD_PARTY_LICENSES.md).
- Your chats, documents, indexes, and settings can contain private data. Do **not** publicly upload your personal USB copy.
- Offline content can become outdated. Verify safety-critical medical, navigation, or emergency information with current authoritative sources.

## More official starting points

- [Qwen3 1.7B GGUF](https://huggingface.co/Qwen/Qwen3-1.7B-GGUF), [Qwen3 4B GGUF](https://huggingface.co/Qwen/Qwen3-4B-GGUF), [Unsloth Qwen3.5 4B GGUF](https://huggingface.co/unsloth/Qwen3.5-4B-GGUF)
- [Kiwix offline archives](https://library.kiwix.org/)
- [Mapsforge U.S. state maps](https://download.mapsforge.org/maps/v5/north-america/us/)
- [Ready.gov](https://www.ready.gov/), [NOAA](https://www.noaa.gov/), [US Forest Service](https://www.fs.usda.gov/)

**A newly added GGUF must be a supported Qwen-family model with a chat template.** Other architectures appear as **unsupported** in the AI Model Manager. The bundled three models are ready to use without downloading more.
