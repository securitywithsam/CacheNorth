# CacheNorth v1.0.4 — candidate work backlog

This is a **planning list**, not a promise that these fixes exist in the hosted v1.0.3 ZIP. Only release a new package after verifying actual changes and rights for its contents.

## High-priority candidate fixes

- [ ] Replace model-summary HTML interpolation in `dashboard/app.js` with DOM elements and `textContent`, plus an adversarial filename/metadata test.
- [ ] Add malformed, oversized, or hostile GGUF/PDF resource-limit tests; distinguish safe rejection from application crashes.
- [ ] Review local API handling of malicious filenames, symlinks/junctions, and error paths.
- [ ] Validate startup, CPU feature detection, Vulkan selection/fallback, token throughput, clean shutdown, and orphaned subprocess behavior in the **compiled** build.
- [ ] Ensure clean builds start without carried-over chats, indexes, settings, launcher logs, cookies, or WebView2 profile data.
- [ ] Include license notices, required corresponding-source information, and OpenStreetMap attribution in the **shipped** UI/package as applicable.
- [ ] Check the specific Qwen GGUF sources, hashes, and licenses; exclude unknown conversions from distributed builds.
- [ ] Decide which third-party archives, PDFs, and portable apps can lawfully be bundled; allow users to download uncertain content themselves.

## Release-process improvements

- [ ] Run the full ZIP verifier against the candidate and store exact archive length, SHA-256, manifest, and clean-extraction results.
- [ ] Record dashboard source/build correspondence and the Git commit used for package construction.
- [ ] Test 8 GB / 16 GB Windows 11, Windows 10, and Windows App Control restrictions on independent PCs.
- [ ] Measure cold-start time, tokens/sec, memory, document indexing, Kiwix/map/PDF opening, and clean close.
- [ ] Capture reviewed screenshots and update release documentation.
- [ ] Retest all download URLs and upstream content-source permissions.

## Commercialization (later)

- [ ] Separate CacheNorth-owned code from externally licensed assets in any paid bundle.
- [ ] Review iFixit, noncommercial knowledge archives, proprietary installers, GPL/AGPL source obligations, and model provenance with appropriate rights holders.
- [ ] Decide on paid packaging, support, updates, and license terms only after redistribution compliance.

**The existing Cloudflare-hosted v1.0.3 ZIP must not be modified as part of these source/documentation tasks.**
