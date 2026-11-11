# Full portable ZIP — final release acceptance

**Candidate:** [CacheNorth-v1.0.3-Full-Portable.zip](https://downloads.samsonschmidt.com/CacheNorth-v1.0.3-Full-Portable.zip)

**Status:** Hosted by the maintainer; release verification is incomplete. Keep GitHub private and do not announce a public release until every relevant gate is complete.

## 1. Integrity and download checks

- [ ] Open the download URL in a clean/incognito browser; verify HTTP download starts and completes.
- [ ] Record the local ZIP's exact **Size** (not "Size on disk") and SHA-256.
- [ ] Download a fresh copy from the hosted URL and compare SHA-256 against the local original.
- [ ] Run `powershell -ExecutionPolicy Bypass -File scripts\verify_portable_zip.ps1 -ZipPath "C:\Path\CacheNorth-v1.0.3-Full-Portable.zip" -InventoryPath "C:\Path\cache-north-zip-inventory.csv"`.
- [ ] Extract on a clean test machine, confirm no nested extra folder breaks the launcher, and test all contents.
- [ ] Publish SHA-256 beside the release URL and retain a dated immutable backup.

**Verified local archive SHA-256:** `PENDING` (never invent a checksum).

## 2. File-by-file redistribution register

For each redistributed binary, model, ZIM, map and PDF, record the exact archive-relative path, publisher, source/version, local SHA-256, license, attribution requirements, and permission to redistribute. Use this table as the starting point:

| Component | Source | License/notice status | Action |
|---|---|---|---|
| CacheNorth original code | This repository | **License selection pending** | Choose a license; reserve brand assets separately |
| KoboldCpp and bundled aria2 | [KoboldCpp](https://github.com/LostRuins/koboldcpp) | AGPL/GPL source and notices unresolved | Add exact corresponding source and notices for distributed components |
| GPXSee/Qt | [GPXSee](https://www.gpxsee.org/) | GPL/LGPL and dependencies need inspection | Inspect bundled executable, DLLs, sources and notices |
| Kiwix JS | [Kiwix releases](https://github.com/kiwix/kiwix-js-pwa/releases) | GPL notice/source requirements need inspection | Verify exact portable package and notice bundle |
| GGUF models | [Qwen](https://huggingface.co/Qwen) | License and quantization provenance per file | Record filenames, SHA-256, source and upstream license |
| ZIM content | [Kiwix library](https://library.kiwix.org/) | Content-specific; some may be noncommercial | Exclude any archive lacking clear redistribution rights |
| Mapsforge maps | [Mapsforge](https://download.mapsforge.org/maps/v5/) | Source terms and OSM attribution | Verify map source; display **© OpenStreetMap contributors** in app |
| PDF guides | Actual publisher of each document | Verify rights per PDF and embedded content | Keep own/cleared PDFs; exclude uncertain files |

The existence of a public download does **not** grant permission to republish it inside CacheNorth. See [third-party review](THIRD_PARTY_LICENSES.md) and [release blockers](https://github.com/securitywithsam/CacheNorth/issues/4).

## 3. Windows physical smoke-test matrix

Record the Windows build, RAM, CPU, Smart App Control status, model, context size, and measured response rate for each test.

| Machine | Cold start | AI chat | Documents | ZIM & map | Offline | Clean close |
|---|---|---|---|---|---|---|
| Windows 11 AMD desktop | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| Windows 11 Intel laptop | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| Windows 11 8 GB RAM | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| Windows 11 16 GB RAM | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| Windows 10 64-bit | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| Windows with Smart App Control | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

Never disable Windows security policies to make tests pass. Document blocked components and whether CPU fallback works.

## 4. Privacy and presentation

- [ ] Inspect the extracted ZIP for conversations, document indexes, personal PDFs, settings, browser profiles, logs, session tokens, credentials, and host-specific paths.
- [ ] Confirm the advertised features work with Wi-Fi disabled.
- [ ] Take a real dashboard screenshot with fictitious inputs and no identifiable data; place it under `docs/assets/` and add it to the README.
- [ ] Check OSM attribution appears in the **actual Maps UI**.
- [ ] Review all model, ZIM, map and PDF links and document the exact recommended assets.

## Final approval

- Reviewer:
- Date:
- Release commit:
- ZIP filename:
- ZIP SHA-256:
- Test report:
- Redistribution clearance:
- **Owner approval to make the repository public / announce the download:** Pending.
