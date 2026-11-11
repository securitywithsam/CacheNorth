# Dependency, content and license review (maintainer reference)

**Status:** Engineering audit required before public release. This is a planning inventory, not a legal clearance or an assertion that every item is in the current final build.

| Item | Known concern | Required action |
| --- | --- | --- |
| Original CacheNorth code | No final public license selected | Confirm ownership, contributor rights, and intended license |
| KoboldCpp | AGPL-3.0 obligations | Verify exact version, official hash, corresponding source and notices for binaries |
| Kiwix / Kiwix JS | GPL obligations for redistributed applications | Verify actual bundled reader and its complete licensing/source notices |
| GPXSee and dependencies | GPL/LGPL and third-party component notices | Audit exact DLLs, source distribution and licenses |
| GGUF models | Model-specific licenses and quantizer provenance | Record exact model, version, source URL, hash, and license; replace unidentified conversion |
| ZIM archives | Different textual/media licenses, some noncommercial or unclear | Review each archive and constituent third-party content; omit uncleared archives |
| Offline maps | Provider/tiles/database terms and OSM attribution | Identify exact sources and permitted redistribution rights |
| PDF guides | Originality, citations, included images and third-party text | Review author/source rights; exclude uncleared PDFs |
| WebView2 and other dependencies | Runtime redistribution terms | Record SDK/runtime terms and supported versions |
| Security With Sam branding | Trademark/logo ownership | Confirm the maintainer owns or may license each asset |

The independent audit from November 2026 was a snapshot of an **earlier** build. Reconcile it against the final code and distribution inventory; do not carry forward findings as if unchanged.

## Evidence to record for each redistributable artifact

- Exact relative path and file size
- Source project, download URL, version/commit
- SHA-256 (and signature/publisher if relevant)
- License and attribution text
- Whether redistribution is permitted (source, free binary, commercial binary)
- Any corresponding-source or written-offer obligation
- Verification date and reviewer

Do not publish a complete USB image until this evidence is complete and distribution-approved.
