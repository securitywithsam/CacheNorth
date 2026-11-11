> **v1.0.3.1 packaging update (November 2026):** A separately cleaned and tested portable package is being prepared. It has 2,933 files (17,300,263,255 uncompressed bytes), refreshed beginner PDFs, three verified Qwen GGUFs, five ZIM archives, four maps, five content guides, source and attribution materials, and no retained chat/browser/log data. The original v1.0.3 [download](https://downloads.samsonschmidt.com/CacheNorth-v1.0.3-Full-Portable.zip) and its [checksum](../SHA256SUMS.txt) remain historical and unchanged. **The v1.0.3.1 download URL, compressed size and SHA-256 are pending the owner's upload; do not substitute the old checksum.** See [package changes and open issues](V1031_RELEASE_CANDIDATE.md). The repo remains private.

# CacheNorth v1.0.3 full ZIP — content rights register

The original register was based on the maintainer's **filename-only inventory** of `CacheNorth-v1.0.3-Full-Portable.zip` supplied November 2026. It does not establish that any item is safe, authentic, or cleared for redistribution. Record exact source URLs, SHA-256, and included notices before declaring a public or commercial release.

## iFixit — required feature, special terms

**Included:** `Library/ifixit_en_all_2025-12.zim`

- iFixit's published content license is [CC BY-NC-SA 3.0](https://www.ifixit.com/Info/Licensing).
- For a genuinely noncommercial distribution satisfying the terms, attribute iFixit; link both the source and [CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/); disclose changes; and preserve ShareAlike requirements for adaptations.
- **Noncommercial is a restriction on use**, not merely whether the download has a price. A free distribution linked to promotions, sponsorships, commercial branding, or future paid offerings may require closer review.
- This ZIM is provided for **offline reading only**. Do not use its content to train an AI model: iFixit's current policy expressly prohibits that without separate permission.
- iFixit expressly invites commercial licensing inquiries at **legal@ifixit.com**. Request written permission specifying downloadable ZIP bundling, free promotional use, later paid sales, volume, territories, duration, attribution, and whether commercial redistribution of this exact ZIM is covered.
- **Until commercial permission is documented, do not assume iFixit can be part of a paid CacheNorth bundle.** For early access, have the owner assess whether distribution is noncommercial under the published terms or obtain permission first.

Suggested attribution alongside the archive:

> iFixit repair content © its respective contributors. Source: https://www.ifixit.com/ . Licensed under Creative Commons Attribution-NonCommercial-ShareAlike 3.0: https://creativecommons.org/licenses/by-nc-sa/3.0/ . Included as an offline Kiwix ZIM; iFixit does not sponsor or endorse CacheNorth. Check the ZIM's specific content metadata and any additional credits.

## Other knowledge archives

| Bundled archive | Reference/source | License verification |
|---|---|---|
| `based.cooking_en_all_2026-08.zim` | https://library.kiwix.org/ | Check collection and embedded-media licenses |
| `cloudflare.com_en_learning-center_2025-12.zim` | https://library.kiwix.org/ | **Unresolved** — obtain publisher/archival redistribution terms |
| `medlineplus.gov_en_all_2025-01.zim` | https://library.kiwix.org/ | **Unresolved** — assess third-party illustrations and source terms |
| `ready.gov_en_all_2026-10.zim` | https://library.kiwix.org/ | Check archive/embedded third-party content |
| `wikipedia_en-simple_all_maxi_2026-09.zim` | https://library.kiwix.org/ | Confirm exact archive metadata and CC BY-SA attribution/ShareAlike requirements |
| `wiktionary_en-simple_all_nopic_2026-10.zim` | https://library.kiwix.org/ | Confirm exact archive metadata and CC BY-SA attribution/ShareAlike requirements |

**Important:** Kiwix being permitted to distribute an archive does not automatically mean a downstream product may repackage it for every purpose.

## Models

| Bundled file | Recommended upstream | Action |
|---|---|---|
| `Qwen3-1.7B-Q4_K_M.gguf` | https://huggingface.co/Qwen/Qwen3-1.7B-GGUF | Confirm binary hash and actual quantization provenance |
| `Qwen3-4B-Q4_K_M.gguf` | https://huggingface.co/Qwen/Qwen3-4B-GGUF | Confirm hash; earlier community AWQ conversion had uncertain provenance |
| `Qwen3.5-4B-Q4_K_M.gguf` | https://huggingface.co/unsloth/Qwen3.5-4B-GGUF | Confirm hash and model card/version |

These upstream model repositories identify Apache-2.0 terms, but filenames alone cannot prove the bundled copies came from them.

## Maps

**Bundled:** `iowa.map`, `michigan.map`, `minnesota.map`, `wisconsin.map`.

Verify the download provider and map file terms. Include visible **© OpenStreetMap contributors** attribution and a link to https://www.openstreetmap.org/copyright ; assess any provider-specific restrictions. The source UI now contains attribution, but the already-uploaded ZIP must be rebuilt to include it.

## PDF reference guides

**Bundled in `Guides/`:**

- `Emergency Wound Care.pdf`
- `emergency_disinfection_of_drinking_water_sept2017.pdf`
- `FEMA emergency reference.pdf`
- `Map and Compass.pdf`
- `ready_emergency-supply-kit-checklist.pdf`
- `USFS BWCAW Trip Planning Guide 2023.pdf`
- `Weather Spotter's Field Guide.pdf`

**Bundled in `Start Here/`:** CacheNorth Quick Start Guide, CacheNorth Technical and Licensing Guide, and CacheNorth Troubleshooting Guide.

For each PDF, confirm the document's actual author/publisher, original URL, date/version, embedded images and redistribution terms. A government-related title alone does not establish public-domain status.

## Optional standalone programs

The full ZIP also contains installers for 7-Zip Portable, Chromium Portable, Foxit Reader Portable, Notepad++ Portable, VLC Portable, and the PortableApps.com Platform. Verify each app's current license and the publisher's **redistribution/repackaging** rights. The simplest licensing path is to publish original download links for optional apps instead of bundling unverified installers.

The core app separately bundles KoboldCpp (AGPL and included vendor components), Kiwix JS (GPL), GPXSee (GPL/Qt and FFmpeg dependencies), and a Python/WebView2 runtime. Their corresponding-source, notice, and redistribution obligations are tracked in [Third-party licenses](THIRD_PARTY_LICENSES.md).

## Release record

- Existing uploaded ZIP SHA-256 (owner supplied, independently matched after re-download): `486824A6BE4B441417BAB6A4AF000FD5312A83602C99F03B7F9D754750791F17`
- Owner reports an independent hosted download with an **identical SHA-256**. This verifies transfer integrity but is **not** approval of the archive's contents, privacy, or redistribution rights.
- Updated, cleaned ZIP hash: **pending**.
- iFixit commercial permission: **pending**.
- Individually approved archive/PDF/installer register: **pending**.
