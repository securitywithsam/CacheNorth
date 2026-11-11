> **v1.0.3.1 packaging update (November 2026):** A separately cleaned and tested portable package is being prepared. It has 2,933 files (17,300,263,255 uncompressed bytes), refreshed beginner PDFs, three verified Qwen GGUFs, five ZIM archives, four maps, five content guides, source and attribution materials, and no retained chat/browser/log data. The original v1.0.3 [download](https://downloads.samsonschmidt.com/CacheNorth-v1.0.3-Full-Portable.zip) and its [checksum](../SHA256SUMS.txt) remain historical and unchanged. **The v1.0.3.1 download URL, compressed size and SHA-256 are pending the owner's upload; do not substitute the old checksum.** See [package changes and open issues](V1031_RELEASE_CANDIDATE.md). The repo remains private.

# Bundled content redistribution decision matrix

**Status:** Preliminary; based on the maintainer's filename-level package inventory and repository documentation. **Not a legal clearance or a verification of the 16.9 GiB ZIP's internal notices.** See [Content Licenses](CONTENT_LICENSES.md) and [Third-party Licenses](THIRD_PARTY_LICENSES.md) for detail.

| Material | Personal use | Free redistribution | Future paid bundle | Action for public release |
|---|---|---|---|---|
| CacheNorth original source and compiled app | Limited personal noncommercial evaluation of official build under [LICENSE](../LICENSE) | Owner may distribute original work, subject to third-party rights | Owner retains commercial options | Keep license/brand terms clear |
| KoboldCpp and included tools | Under applicable upstream licenses | Permitted with applicable AGPL/GPL and bundled notices/source obligations | Not categorically prohibited; obligations still apply | Confirm exact version, corresponding source and subcomponent notices (aria2, etc.) |
| Kiwix JS Electron | Under upstream terms | GPL and bundled component notices/source requirements | GPL obligations continue | Verify shipped package and notice/source availability |
| GPXSee, Qt, FFmpeg | Under upstream terms | GPL/LGPL and dependency obligations; exact bundle needs inspection | May be commercially distributed with compliance | Verify exact packaged licenses and source requirements |
| Qwen GGUF models | Depends on model card | Apache-2.0 for identified official/Unsloth sources, **if actual files match provenance** | Potentially permitted under their actual licenses | Record hashes, source repos and exact model cards |
| iFixit ZIM | Subject to CC BY-NC-SA terms | **Conditional** on a genuinely noncommercial use with credit, license link, and applicable ShareAlike | Commercial permission/license needed | Confirm this distribution qualifies or obtain permission; do not assume free means noncommercial |
| Simple Wikipedia/Wiktionary ZIMs | Subject to archive licenses | CC BY-SA content with attribution/ShareAlike; media rights vary | May be possible with license obligations | Verify exact archive metadata, notices and media |
| MedlinePlus, Ready.gov, other ZIMs | Content-specific | **Unverified** for complete archived works/third-party elements | **Unverified** | Inspect per-archive provenance and rights |
| Cloudflare Learning Center ZIM | Content-specific | **No blanket redistribution permission established** | **No blanket commercial permission established** | Exclude from redistribution unless rights are established |
| based.cooking ZIM | Content-specific | **Unverified** | **Unverified** | Review publisher and embedded media terms |
| Mapsforge/OpenStreetMap maps | Source/provider-specific | Data/derivative license conditions and © OSM attribution apply | Possible with applicable license compliance | Verify download provider, file metadata and shipped attribution |
| Seven third-party PDFs | Publisher/embedded-asset-specific | **Unverified per exact file** | **Unverified per exact file** | Trace each PDF to publisher, URL, terms, and embedded assets |
| PortableApps installers (including Foxit) | Per-app terms | **Unverified for repackaging**; proprietary freeware may restrict it | **Unverified** | Prefer links to official downloads until rights are verified |
| Python, WebView2, and runtime libraries | Respective software licenses | Generally redistributable subject to each package's terms and notices | Generally possible with compliance | Verify bundled license files and permitted redistributable components |

## Checklist for each shipped asset

Record: relative path, exact filename/version, publisher, originating URL, SHA-256, license text/link, required attribution, whether the full asset can be redistributed, whether promotional and commercial distribution are permitted, and source/notice obligations. Store evidence without secrets or personal data.

If permission is unknown, list the item as **unresolved**. The fact that someone else distributes a downloadable file does not automatically authorize repackaging it.

## Future sales

Free early access does not transfer ownership of CacheNorth's original source. Future paid offerings should use a distribution inventory that excludes restricted or unlicensed content and continues to satisfy independent GPL/AGPL/Creative Commons obligations. Consult rights holders or qualified counsel when license interpretation is material.
