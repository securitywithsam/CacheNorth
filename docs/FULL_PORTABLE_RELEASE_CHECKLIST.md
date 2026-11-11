# CacheNorth v1.0.3.1 — release checklist

**Current status:** application tested. Owner reports ZIP `CacheNorth-v1.0.3.1-Full-Portable.zip`, 15,993,029,771 compressed bytes and SHA-256 `4D6711127EAC4803756963359AD331CA41150385B300C02D862B48B0094EAAED`. Hosted availability/integrity and rights questions remain pending. The [current ZIP checksum](../SHA256SUMS.txt) is for v1.0.3.1. See [release candidate details](V1031_RELEASE_CANDIDATE.md).

## Before updating the download link

- [x] Remove generated chats, indexes, WebView2 profiles, logs and sessions from portable package.
- [x] Verify retained Qwen models, archives and maps against known published files as reported by maintainer.
- [x] Include notices, attribution and corresponding source materials identified during cleanup.
- [x] Update three branded help PDFs and verify they open.
- [x] Test startup, CPU model loading, document citations, Kiwix, maps, guides, shutdown and alternate drive mapping on one PC (19 checks reported passed).
- [ ] Confirm iFixit redistribution qualifies under its NC license or obtain permission/remove.
- [ ] Resolve exact Chromium/Electron LGPL/MPL source availability and relinking obligations.
- [ ] Add a public licensing/support contact.
- [ ] ZIP **only the application folder**, excluding private `_work`; preserve four empty `Data` folders.
- [x] Record owner-reported new ZIP filename, compressed file length and SHA-256.
- [ ] Extract a sample of the finished ZIP and verify it launches.
- [ ] Upload to Cloudflare using a **new filename**; verify link and a downloaded-copy SHA-256.
- [ ] Update README and [SHA256SUMS.txt](../SHA256SUMS.txt) with the new verified artifact while preserving original checksum.
- [ ] Make GitHub public only if the owner explicitly authorizes that separate step.

## Recommended follow-up testing

- [ ] Test a real USB 3 drive and slower USB drive.
- [ ] Test another machine, Windows 10 and 8 GiB RAM.
- [ ] Test GPU acceleration, document file picker and actual downloaded-ZIP SmartScreen behavior.
- [ ] Confirm all user-facing links and in-package PDF file paths.

The repository's source CI does **not** certify the large hosted ZIP. 
