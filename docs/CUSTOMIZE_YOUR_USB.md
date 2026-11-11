# Customize your CacheNorth USB

**Make your offline USB useful for you.** Pick your AI model, favorite offline knowledge, local maps, and reference guides. Copy each file into the matching folder, then refresh CacheNorth.

> **Full portable USB download:** \`CacheNorth-v1.0.3-Full-Portable.zip\` is being prepared and has **not** been published yet. When the verified download is ready, its link will appear at the top of the [main page](../README.md). GitHub's green **Code → Download ZIP** downloads source code, **not** a ready-to-run CacheNorth USB.

## Start in three steps

1. **Get CacheNorth.** When the full ZIP is released, download it, extract it to a USB drive (or a normal folder), and open \`Launch CacheNorth.exe\`. Until then, see [Build from source](BUILDING.md) if you want to test the source preview.
2. **Choose what you want offline.** Use the links below to download an AI model, knowledge archives, maps, or PDFs **while you have internet**.
3. **Copy files into the folders shown below.** In CacheNorth, choose **Refresh All** to update your libraries. For document search, use **Refresh Documents** or the add-documents control.

You can leave optional folders empty. Keep their names and locations unchanged. CacheNorth works from different drive letters, so you do not have to use \`E:\`.

## Your USB folder map

The examples show a USB called \`E:\`, but yours might be \`D:\`, \`F:\`, or another letter.

\`\`\`text
E:\  CACHE NORTH USB
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
├── Kiwix\                                 ← Optional ZIM reader
│   └── kiwix-js-pwa-win32-ia32\
│       └── Kiwix JS Electron.exe
└── Start Here\                            ← Included help material (if present)
\`\`\`

The application also has other runtime files and folders. **Keep them in place.** Add your downloads to the existing folders; do not move \`Launch CacheNorth.exe\`, rename application directories, or put your GGUF files into the \`Documents\` folder.

| What you want to add | File type | Copy it here | Where to use it |
|---|---|---|---|
| Offline AI model | \`.gguf\` | \`Apps\Offline AI\Models\` | **AI Chat / Settings → Models** |
| Wikipedia, repair, medical or other Kiwix knowledge | \`.zim\` | \`Library\` | **Knowledge Base** |
| Regional offline map | \`.map\` (Mapsforge) | \`Maps\` | **Maps** |
| Reading guides | \`.pdf\` | \`Guides\` | **Guides** |
| Your own searchable documents | \`.pdf\`, \`.txt\`, \`.md\` | \`Apps\Offline AI\Data\Documents\` | **Ask Documents** |

## 1. Choose your AI model

You need **at least one model** for offline AI chat. Download one \`Q4_K_M\` GGUF file from a model page below, not the entire repository.

| Model | Approximate size | A good starting point for | Download |
|---|---:|---|---|
| Qwen3 1.7B | 1.3 GB | Lighter/faster option; smaller RAM computers | [Official Qwen GGUF](https://huggingface.co/Qwen/Qwen3-1.7B-GGUF/tree/main) |
| Qwen3 4B | 2.5 GB | More capable option; 16 GB+ RAM preferred | [Official Qwen GGUF](https://huggingface.co/Qwen/Qwen3-4B-GGUF/tree/main) |
| Qwen3.5 4B | 2.7 GB | Alternative 4B model; 16 GB+ RAM preferred | [Unsloth GGUF](https://huggingface.co/unsloth/Qwen3.5-4B-GGUF) |

**How:** Open the model page → **Files and versions** → select a compatible \`Q4_K_M.gguf\` file → download → place it in \`Apps\Offline AI\Models\`. Open CacheNorth and refresh/select the model in Settings. Available filenames and formats can change; verify the model's license and file details before downloading.

## 2. Add offline knowledge (.zim)

A \`.zim\` is an offline library archive, used by [Kiwix](https://library.kiwix.org/). You can mix smaller, specialized collections with larger encyclopedias.

- [Browse the Kiwix library](https://library.kiwix.org/) — search for **Simple English Wikipedia**, **Wiktionary**, **Wikivoyage**, and other topics.
- [Kiwix JS portable Windows downloads](https://github.com/kiwix/kiwix-js-pwa/releases) — download the appropriate portable Windows archive if your USB does not already have the Kiwix viewer.

**How:** Download the selected \`.zim\` file → put it in \`Library\` → choose **Refresh All** → open **Knowledge Base**. If an archive will not open, verify that the Kiwix viewer is present and that the path matches [Installation](INSTALLATION.md#6-add-offline-archives-optional).

**Important:** Every ZIM collection has its own content rights. Downloading for personal offline reading does not automatically grant permission to repackage it into a public USB ZIP. Check the archive's license before sharing.

## 3. Add your own local maps (.map)

- [Browse Mapsforge map downloads](https://download.mapsforge.org/maps/v5/) — select a continent, country, or region.
- [United States state maps](https://download.mapsforge.org/maps/v5/north-america/us/) — pick the state you need.
- [Minnesota map](https://download.mapsforge.org/maps/v5/north-america/us/minnesota.map) — example for Minnesota users.
- [GPXSee map viewer](https://www.gpxsee.org/) — portable map viewer, needed if it is not already included.

**How:** Download a compatible **Mapsforge \`.map\`** file → copy to \`Maps\` → choose **Refresh All** → open **Maps**. This feature uses Mapsforge maps, not arbitrary map images or GPX tracks. The viewer belongs at \`Apps\GPXSee\GPXSee.exe\`.

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

**How:** Download a PDF you trust → copy it into \`Guides\` → choose **Refresh All** → open **Guides**.

Want the AI to **search and cite** a document instead? Put a copy in \`Apps\Offline AI\Data\Documents\`, then refresh documents and use **Ask Documents**. PDFs made entirely of scanned images need OCR first.

## Make it personal: three example setups

| Your goal | Try adding |
|---|---|
| **Small everyday USB** | Qwen3 1.7B + Simple English Wikipedia + personal PDFs |
| **Travel/offline reference USB** | Qwen3 4B + Wikivoyage ZIM + maps of the places you visit + travel PDFs |
| **Preparedness USB** | A compatible model + selected Kiwix references + your regional map + official emergency PDFs |

These are examples, not fixed bundles. Choose content based on your drive's free space, your computer's RAM, and the rights attached to each file.

## After copying your files

1. Safely finish copying all downloads.
2. Launch \`Launch CacheNorth.exe\`.
3. Choose **Refresh All**; use **Refresh Documents** for Ask Documents.
4. Confirm the items appear in the corresponding sections.
5. Test at least one AI prompt, one ZIM, one map, and one PDF **with Wi-Fi turned off**.
6. Close CacheNorth and any viewers before safely ejecting the USB.

## Help and safe sharing

- [Installation details](INSTALLATION.md) · [Content source notes](CONTENT_SOURCES.md) · [Troubleshooting](TROUBLESHOOTING.md)
- Models, ZIMs, maps, and PDFs may have separate licensing or redistribution obligations. See [Third-party licensing](THIRD_PARTY_LICENSES.md).
- Your chats, documents, indexes, and settings can contain private data. Do **not** publicly upload your personal USB copy.
- Offline content can become outdated. Verify safety-critical medical, navigation, or emergency information with current authoritative sources.
