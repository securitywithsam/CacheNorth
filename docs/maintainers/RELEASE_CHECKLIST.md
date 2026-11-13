# CacheNorth v1.0.3.1 — maintainer release checklist

**Current status:** application tested. Owner reports ZIP `CacheNorth-v1.0.3.1-Full-Portable.zip`, 15,993,029,771 compressed bytes and SHA-256 `4D6711127EAC4803756963359AD331CA41150385B300C02D862B48B0094EAAED`. The repository is public and v1.0.3.1 is a published early-access prerelease. The ZIP is hosted at [downloads.samsonschmidt.com](https://downloads.samsonschmidt.com/CacheNorth-v1.0.3.1-Full-Portable.zip); the owner confirmed the downloaded hosted copy matches this hash. iFixit and Chromium/Electron rights questions remain unresolved. The [current ZIP checksum](../../SHA256SUMS.txt) is for v1.0.3.1. See [release record](V1031_RELEASE_NOTES.md).

## Release status and remaining checks

- [x] Remove generated chats, indexes, WebView2 profiles, logs and sessions from portable package.
- [x] Verify retained Qwen models, archives and maps against known published files as reported by maintainer.
- [x] Include notices, attribution and corresponding source materials identified during cleanup.
- [x] Update three branded help PDFs and verify they open.
- [x] Test startup, CPU model loading, document citations, Kiwix, maps, guides, shutdown and alternate drive mapping on one PC (19 checks reported passed).
- [ ] Confirm iFixit redistribution qualifies under its NC license or obtain permission/remove.
- [ ] Resolve exact Chromium/Electron LGPL/MPL source availability and relinking obligations.
- [x] Provide [GitHub Issues](https://github.com/securitywithsam/CacheNorth/issues) for general licensing inquiries; see [Security](../../SECURITY.md) for private security reporting guidance.
- [ ] Confirm the finished ZIP contains **only the application folder**, excludes private `_work` and preserves four empty `Data` folders.
- [x] Record owner-reported new ZIP filename, compressed file length and SHA-256.
- [ ] Extract a sample of the finished ZIP and verify it launches.
- [x] Publish the full portable ZIP at downloads.samsonschmidt.com; owner confirmed a matching downloaded-copy SHA-256.
- [x] Record the hosted artifact in README and [SHA256SUMS.txt](../../SHA256SUMS.txt), preserving the checksum and attributing the hosted hash confirmation to the owner.
- [x] Repository is public and v1.0.3.1 is published as a prerelease.

## Recommended follow-up testing

- [ ] Test a real USB 3 drive and slower USB drive.
- [ ] Test another machine, Windows 10 and 8 GiB RAM. Windows 10 is expected to work but remains untested.
- [ ] Test GPU acceleration, document file picker and actual downloaded-ZIP SmartScreen behavior.
- [ ] Confirm all user-facing links and in-package PDF file paths.

The repository's source CI does **not** certify the large hosted ZIP. 
