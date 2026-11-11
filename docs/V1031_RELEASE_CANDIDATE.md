# CacheNorth v1.0.3.1 — portable release candidate

**Status: prepared locally; new hosted ZIP URL, compressed size, and SHA-256 pending.** This repository remains private. The existing [v1.0.3 ZIP](https://downloads.samsonschmidt.com/CacheNorth-v1.0.3-Full-Portable.zip) is the original historical artifact, with [its own checksum](../SHA256SUMS.txt); it has **not** been replaced by editing this repository.

## What changed compared with the original v1.0.3 package

This is a packaging, documentation, content-rights and privacy cleanup. **The application binaries and AI behavior were not rebuilt or changed.** The maintainer's clean folder contains 2,933 files totaling **17,300,263,255 bytes uncompressed** (decimal GB: 17.30; GiB: about 16.11). This is **not** the ZIP's final compressed size.

- Removed generated browser/WebView2 state, chat and search databases, session data, logs and local test artifacts. The cleaned `Data` folder contains default settings and four empty directories.
- Removed the Cloudflare and MedlinePlus ZIM archives and two PDFs without established complete redistribution rights: *Map and Compass* and the NWS spotter guide with third-party photographs.
- Removed six optional PortableApps installers, a duplicate GPXSee installer and legacy `Start Offline AI.bat`.
- Retained three GGUFs **Qwen3 1.7B, Qwen3 4B and Qwen3.5 4B**, whose files were confirmed to match their official published hashes. **Qwen-family models only** are supported by this v1.0.3.x model manager.
- Retained five ZIM archives (including iFixit under noncommercial-license review), four Mapsforge maps and five reference content guides. The verified CDC *Emergency Wound Care* guide is retained with attribution.
- Added/upgraded third-party license notices and content attribution; added corresponding source archives for KoboldCpp, aria2, Kiwix JS, GPXSee, Qt 6.12.0, FFmpeg 9.0.1 and Electron/Chromium FFmpeg components. Full Chromium-source compliance for some statically linked LGPL/MPL components remains under review.
- Updated the dashboard's static OpenStreetMap attribution and regenerated the branded Quick Start (7 pages), Troubleshooting (7 pages) and Technical and Licensing (4 pages) PDFs. The PDFs include synthetic screenshots and current Settings names.

## What was actually tested

The maintainer reports **19/19 tests passed on one Windows 11 PC**, including native launch, CPU chat with all three models, Automatic model selection, synthetic document search with citations, Kiwix, GPXSee, PDF open, Refresh All, path boundary checks, clean shutdown and an alternate mapped drive letter. Key shipped application binaries were checked as unchanged. The cleanup reports and file-level checksums are maintained privately outside the customer ZIP.

**Not acceptance-tested:** a real USB 3 or slow USB drive, another PC, Windows 10, an 8 GB machine, GPU acceleration, the documents file-picker control and Windows SmartScreen behavior for a newly downloaded ZIP. The SHA-256 proves a file matches the published artifact; it does not prove safety.

## Release verification still required

1. Compress the **application folder only**; exclude the private `_work` reports/hosting folder. Preserve four empty `Data` directories.
2. Record **exact ZIP filename, compressed byte length and SHA-256** from the finished archive, and check extraction and startup. Publish these values together with the new Cloudflare download link. **Never reuse the v1.0.3 checksum for v1.0.3.1.**
3. Resolve the applicable source-distribution obligations for bundled Chromium/Electron components, including the LGPL/MPL source availability/relinking questions.
4. Confirm that distribution of the iFixit CC BY-NC-SA archive qualifies as noncommercial or obtain appropriate permission; remove the archive if neither condition is satisfied.
5. Set a usable public licensing/contact address before broad distribution. Original CacheNorth code remains under its [limited proprietary early-access license](../LICENSE).
6. Perform a second-machine/USB smoke test where practical.

These are engineering and rights-tracking notes, not a legal certification. Distribution for free does not itself establish noncommercial status under all content licenses.

## Documentation scope

This page describes the **cleaned v1.0.3.1 package**, based on the maintainer's final cleanup and test report. Other documentation may still discuss historical v1.0.3 source builds, optional third-party dependencies and original package behavior; those descriptions should not be interpreted as the final cleaned package inventory.

For setup see [Getting Started](GETTING_STARTED.md), [Customization](CUSTOMIZE_YOUR_USB.md) and [Troubleshooting](TROUBLESHOOTING.md). For historical package identity, see [Source vs hosted ZIP](SOURCE_VS_HOSTED_ZIP.md).
