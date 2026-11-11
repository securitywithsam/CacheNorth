# CacheNorth content rights — v1.0.3.1 package

This applies to the **v1.0.3.1 portable download**. Its filename, reported size and checksum are listed in the [README](../../README.md). See [release candidate](../maintainers/V1031_RELEASE_NOTES.md).

Free access does not automatically establish noncommercial use or override upstream licenses. This is a tracking record rather than legal clearance.

## Included materials

| Material | Current package state | License or remaining action |
|---|---|---|
| Qwen3 1.7B, Qwen3 4B, Qwen3.5 4B GGUF | All three included; the maintainer compared to official published hashes | Follow each model's license and notice; model manager accepts Qwen-family architectures only |
| Five ZIM archives | Five included; sources and provenance recorded in package notices | Wikipedia/Wiktionary attribution and ShareAlike where applicable; verify each archive's embedded content |
| iFixit repair ZIM | Included, approximately 3.3 GB | [CC BY-NC-SA 3.0](https://www.ifixit.com/Info/Licensing); confirm this distribution qualifies as noncommercial or secure permission before public release. No iFixit endorsement is implied |
| Four Mapsforge maps | Included with OpenStreetMap attribution in dashboard and `Maps/ATTRIBUTION.txt` | Follow OSM/ODbL and map provider attribution terms |
| Five reference PDFs | Included; the CDC *Emergency Wound Care* fact sheet was matched to the official copy and credited | Preserve publisher notices and any third-party-media restrictions |
| Core viewers, models and runtimes | Included with third-party notices, corresponding source archives, and relinking materials | [Third-party licenses](THIRD_PARTY_LICENSES.md); Chromium/Electron source availability remains under review |

### Excluded from v1.0.3.1

- Cloudflare Learning Center and MedlinePlus ZIM archives (rights not sufficiently established for downstream redistribution).
- `Map and Compass.pdf` and `Weather Spotter's Field Guide.pdf` (publisher/media-rights uncertainties).
- Six optional PortableApps installers (Chromium, Foxit Reader, VLC, 7-Zip, Notepad++, PortableApps Platform), a duplicate GPXSee installer and the legacy batch launcher.

## Attribution and permission

iFixit repair content © respective contributors, provided for offline reading without endorsement. See [iFixit licensing](https://www.ifixit.com/Info/Licensing) and [CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/). Any future paid CacheNorth distribution needs a fresh item-by-item rights review and likely an alternative arrangement for iFixit.

For component source/licensing details, see [Third-party licenses](THIRD_PARTY_LICENSES.md) and the notices shipped in the portable app. The private `_work/reports/LICENSING_REPORT.md` holds exact package evidence; it is not distributed with the customer ZIP.


---

## Detailed third-party component inventory

This inventory separates the source-build dependencies from the **v1.0.3.1 full portable package** and from third-party projects. The tables below describe source/build inputs unless noted; the full ZIP bundles additional material. It is an engineering inventory, not legal advice. Items marked **Unresolved** must not be treated as cleared for redistribution. The current package inventory and iFixit commercial-rights analysis are in [CONTENT_LICENSES.md](THIRD_PARTY_LICENSES.md).

## 1. Original CacheNorth work (Security With Sam)

| Part | Location |
|---|---|
| Python backend | `src/security_with_sam/`, `run_offline_ai.py` |
| Dashboard (HTML/CSS/JavaScript, no third-party libraries or web fonts) | `dashboard/` |
| Native launcher (C#) | `launcher/` |
| Build, fetch, test, and acceptance scripts | `scripts/` |
| Tests and fixtures | `tests/` |
| Documentation | `README.md`, `SECURITY.md`, `docs/` |
| CacheNorth and Security With Sam logos and icons | `dashboard/cache-north-logo.png`, `dashboard/favicon.ico`, `launcher/CacheNorth.ico`, `docs/assets/` |

**License:** original CacheNorth code and branding remain proprietary with limited personal early-access permission under [LICENSE](../../LICENSE); see [LICENSE_RECOMMENDATION.md](../maintainers/LICENSE_DECISION.md). The names and logos are brand assets and stay outside any code license.

## 2. Components bundled into a CacheNorth build

None of these binaries are in the source repository; `fetch_third_party.ps1` and `bootstrap.ps1` download them from official sources at build time.

| Component | Version | Official URL | License | How CacheNorth uses it | Redistribution | Notices / source obligations | Open issues |
|---|---|---|---|---|---|---|---|
| KoboldCpp (unpacked `koboldcpp-nocuda`) | 1.124.2 | https://github.com/LostRuins/koboldcpp | AGPL-3.0; bundled parts carry their own licenses (llama.cpp/ggml MIT and others in `vendor_licenses\`) | Local inference engine, separate process | Permitted under AGPL-3.0 | Ship `LICENSE.md` and `vendor_licenses\` (the build copies the whole folder). Anyone distributing builds must provide the **exact corresponding source** for v1.124.2 (for example, a source archive of tag v1.124.2 published alongside each release), not just a link that may disappear. | v1.0.3.1 includes aria2 corresponding source and refreshed notices; source-built redistributors should check the exact resulting runtime's included libraries and licenses. |
| Python runtime | 3.12.8 | https://www.python.org | PSF License (includes notices for OpenSSL 3.0.15, SQLite 3.45.3, libffi, zlib, Tcl/Tk 8.6, expat, bzip2, xz) | Embedded interpreter for the backend | Permitted | Python's `LICENSE.txt` is copied into `Documentation\Licenses\Runtime Licenses` | — |
| PyInstaller bootloader | 6.16.0 | https://pyinstaller.org | GPL-2.0 with bootloader exception | Starts the packaged backend | Permitted for any application license (exception) | None beyond the exception | — |
| Flask | 3.1.3 | https://palletsprojects.com/p/flask | BSD-3-Clause | Local web API | Permitted | License copied by build | — |
| Werkzeug | 3.1.9 | https://palletsprojects.com/p/werkzeug | BSD-3-Clause | Flask dependency | Permitted | License copied by build | — |
| Jinja2 | 3.1.6 | https://palletsprojects.com/p/jinja | BSD-3-Clause | Flask dependency | Permitted | License copied by build | — |
| MarkupSafe | 3.0.4 | https://palletsprojects.com/p/markupsafe | BSD-3-Clause | Flask dependency | Permitted | License copied by build | — |
| itsdangerous | 2.2.0 | https://palletsprojects.com/p/itsdangerous | BSD-3-Clause | Flask dependency | Permitted | License copied by build | — |
| click | 8.5.0 | https://palletsprojects.com/p/click | BSD-3-Clause | Flask dependency | Permitted | License copied by build | — |
| colorama | 0.4.6 | https://github.com/tartley/colorama | BSD-3-Clause | click dependency on Windows | Permitted | License copied by build | — |
| blinker | 1.9.0 | https://github.com/pallets-eco/blinker | MIT | Flask dependency | Permitted | License copied by build | — |
| waitress | 3.0.2 | https://github.com/Pylons/waitress | ZPL-2.1 | Local HTTP server | Permitted | License copied by build | — |
| pypdf | 6.21.4 | https://github.com/py-pdf/pypdf | BSD-3-Clause | PDF text extraction | Permitted | License copied by build | — |
| cryptography (+ cffi 2.1.1, pycparser 3.12) | 50.0.2 | https://github.com/pyca/cryptography | Apache-2.0 OR BSD-3-Clause (cffi MIT, pycparser BSD-3); the wheel bundles OpenSSL 3.x (Apache-2.0) | Lets pypdf open AES-encrypted PDFs | Permitted | Licenses copied by build | v1.0.x builds made before this source release also bundled Pillow incidentally; source builds do not. |
| psutil | 7.1.2 | https://github.com/giampaolo/psutil | BSD-3-Clause | Memory and process management | Permitted | License copied by build | — |
| py-cpuinfo | 9.0.0 | https://github.com/workhorsy/py-cpuinfo | MIT | CPU name and fallback detection | Permitted | License copied by build | — |
| Microsoft WebView2 SDK (Core, WinForms, Loader DLLs) | 1.0.4314.35 | https://www.nuget.org/packages/Microsoft.Web.WebView2 | Microsoft WebView2 SDK license | Native dashboard window | Permitted for the listed redistributable DLLs under the package license | Package `LICENSE.txt` copied to `Documentation\Licenses\Microsoft.Web.WebView2-SDK.txt`. The Evergreen WebView2 Runtime is **not** bundled. | — |
| Microsoft Visual C++ runtime DLLs | as shipped with Python/KoboldCpp | https://learn.microsoft.com/cpp/windows/redistributing-visual-cpp-files | Microsoft redistributable terms | Required by the native libraries | Permitted as application-local redistributables | — | — |

## 3. Optional components for source builders (already included in the full portable package)

| Component | Version tested | Official URL | License | Use | Redistribution | Obligations / issues |
|---|---|---|---|---|---|---|
| Kiwix JS Electron | 3.9.3 (viewer), Electron 43.7.5 (source reported in package) (win32) | https://github.com/kiwix/kiwix-js-pwa | GPL-3.0 plus Electron/Chromium notices | Opens `.zim` archives | Permitted with GPL source availability and notices | The Kiwix JS viewer is bundled in the ZIP; review offline behavior and upstream update checker. Electron/Chromium LGPL/MPL source availability remains an open redistribution issue. |
| GPXSee | 16.18 (x64) | https://www.gpxsee.org | GPL-3.0; bundles Qt 6 (LGPL-3.0) and FFmpeg (LGPL/GPL) | Opens `.map` files | Permitted with GPL/LGPL obligations | v1.0.3.1 includes GPXSee and version-matched Qt 6.12.0 and FFmpeg 9.0.1 source archives, license notices and relinking instructions. Future source builds must arrange these separately. |
| Qwen3 1.7B / Qwen3 4B GGUF | Q4_K_M | https://huggingface.co/Qwen | Apache-2.0 | AI models | Permitted with license and attribution | The retained Qwen3 4B file was reported byte-identical to the official Qwen GGUF during the v1.0.3.1 cleanup, as were the other two included models. Keep the maintainer's exact hash evidence with the release. |
| Qwen3.5 4B GGUF | Q4_K_M (Unsloth quantization) | https://huggingface.co/Qwen, https://huggingface.co/unsloth | Apache-2.0 | AI model | Permitted with license and attribution | — |
| Kiwix ZIM archives | various | https://library.kiwix.org | Per archive | Offline reference content | Varies (see below) | See section 4 |
| Mapsforge `.map` files | various | https://download.mapsforge.org | OpenStreetMap data, ODbL-1.0 | Offline maps | Permitted with attribution and share-alike | Display "© OpenStreetMap contributors". **Open item:** the dashboard's Maps page does not yet show this attribution (planned for v1.0.4). |

## Bundled archive content and its terms

| Archive | License status | Redistribution |
|---|---|---|
| Simple English Wikipedia, Simple English Wiktionary | CC BY-SA (text); media vary | Permitted with attribution and share-alike |
| iFixit | CC BY-NC-SA 3.0 | **Non-commercial only**; commercial use needs iFixit's written permission |
| MedlinePlus | Removed from v1.0.3.1 | Not part of the current package |
| Ready.gov | U.S. federal content, generally public domain; may contain third-party items and seals | **Unresolved** pending review |
| based.cooking | Not verified | **Unresolved** |
| Cloudflare Learning Center | Removed from v1.0.3.1 | Not part of the current package |
| PDF guides (FEMA, USFS, EPA, NOAA, Ready.gov, others) | U.S. government works generally public domain; "Emergency Wound Care" and "Map and Compass" have unknown sources | **Unresolved** for the two unknown-source PDFs |

## 5. Development and test tools (not shipped)

pytest 9.0.3 (MIT), pytest-cov 7.0.0 (MIT), coverage 7.17.1 (Apache-2.0), PyInstaller 6.16.0 (GPL-2.0 with exception), reportlab 4.4.4 (BSD), pdfplumber 0.11.10 (MIT), Node.js (MIT; built-in `node:test` only), and the .NET Framework C# compiler (part of Windows).

## License texts

`licenses/` contains the full texts referenced above: AGPL-3.0, GPL-3.0, Apache-2.0, ODbL-1.0, CC BY-SA 4.0, CC BY-NC-SA 3.0, and Python. Builds copy them, plus each runtime package's own license files, into `Apps\Offline AI\Documentation\Licenses`.
