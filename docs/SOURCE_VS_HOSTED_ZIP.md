> **v1.0.3.1 uploaded-artifact metadata (owner reported):** [CacheNorth-v1.0.3.1-Full-Portable.zip](https://downloads.samsonschmidt.com/CacheNorth-v1.0.3.1-Full-Portable.zip) — **15,993,029,771 bytes** (15.99 GB decimal; ~14.90 GiB), SHA-256 `4D6711127EAC4803756963359AD331CA41150385B300C02D862B48B0094EAAED`. The URL follows the existing Cloudflare R2 custom-domain naming pattern, but **the new download has not yet been independently fetched or verified**. Verify the hosted copy before announcing it. The old v1.0.3 ZIP remains a separate historical artifact.

# Source code vs. the hosted ZIPs

CacheNorth has **two distinct deliverables**:

| Deliverable | Location | What changes it |
|---|---|---|
| Source and documentation | This GitHub repository, default branch `main` | GitHub commits and merged pull requests |
| Frozen full portable package | [CacheNorth-v1.0.3-Full-Portable.zip](https://downloads.samsonschmidt.com/CacheNorth-v1.0.3-Full-Portable.zip) | Only rebuilding/repackaging and uploading a new ZIP |

**Editing GitHub does not update the Cloudflare-hosted ZIP.** Treat the downloadable v1.0.3 archive as a fixed historical release candidate. Later repository changes to Python, C#, JavaScript, styles, documentation, attribution, tests, or dependencies are **not** automatically installed in that archive.

## New cleaned v1.0.3.1 ZIP record (owner-reported; hosted URL unverified)

- Filename: `CacheNorth-v1.0.3.1-Full-Portable.zip`
- Expected URL: [download](https://downloads.samsonschmidt.com/CacheNorth-v1.0.3.1-Full-Portable.zip)
- Exact compressed length: 15,993,029,771 bytes
- SHA-256 of local ZIP: `4D6711127EAC4803756963359AD331CA41150385B300C02D862B48B0094EAAED`
- The new package and checksum are distinct from the original v1.0.3 archive below.

## Historical v1.0.3 hosted ZIP record

- Filename: `CacheNorth-v1.0.3-Full-Portable.zip`
- Advertised compressed size: approximately **16.9 GiB**; exact byte length needs measurement using file **Length**, not **Size on disk**.
- Maintainer-reported SHA-256, equal for original and independently downloaded copy:
  `486824A6BE4B441417BAB6A4AF000FD5312A83602C99F03B7F9D754750791F17`
- SHA-256 confirms those two archives are byte-identical. It does not establish safety, rights to redistribute all content, or compatibility.
- Contents reportedly include app runtime, GGUF models, Kiwix ZIMs, maps, guides, third-party programs, and generated runtime data. See [Content Licenses](CONTENT_LICENSES.md) and [Full Portable Release Checklist](FULL_PORTABLE_RELEASE_CHECKLIST.md).

## What is actually verified?

| Item | Status |
|---|---|
| Source test pipeline | GitHub Actions CI has passed on `main` |
| Original ZIP vs. downloaded copy | Owner reported matching SHA-256 |
| Source dashboard byte-for-byte equal to shipped dashboard | **Not yet compared** |
| Source launcher/backend equivalent to shipped compiled binaries | **Not yet independently proven** |
| Exact bundled file and licensing inventory | **Incomplete** |
| Personal/runtime data absent from hosted ZIP | **Not verified** |
| Broad Windows 10/11, 8 GB, GPU, and managed-PC compatibility | **Not verified** |
| Clean offline startup, knowledge/maps/documents, close on every target PC | **Not verified** |

## How to compare the shipped dashboard without changing the ZIP

1. Extract the **existing** ZIP into a separate clean test folder.
2. Obtain the current source files from the `main` branch.
3. Compare `dashboard/app.js`, `dashboard/index.html`, and `dashboard/styles.css` to their equivalent paths in the extracted package using `Get-FileHash -Algorithm SHA256`.
4. Record differences and the commit tested. **Do not overwrite the hosted package** to make them match.
5. For Python/C# bundled as executables, a byte-for-byte source match generally cannot be established without reproducible build artifacts or build provenance.

## Future version updates

Collect source fixes in the [v1.0.4 backlog](V104_BACKLOG.md). When a new version is deliberately packaged, it needs a **new filename, hash, smoke-test record, bundled-rights review, and release notes**. Leave the original v1.0.3 download and published checksum intact.

## Privacy and rights

Chats, indexes, settings, logs, and browser profiles can be sensitive. Comparing a used Desktop extraction to a clean extraction or ZIP inventory can identify generated files; never expose private database/cookie contents in issues. Licensing notes for original source do not override independent third-party licenses.
