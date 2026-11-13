<p align="center"><img src="dashboard/cache-north-logo.png" alt="CacheNorth logo" width="120"></p>

# CacheNorth

<p align="center"><strong>Your knowledge. Anywhere.</strong><br>Portable offline AI, reference libraries, maps, and guides.</p>

<p align="center">
  <img src="https://img.shields.io/badge/Windows-10%20%7C%2011-blue" alt="Windows 10 or 11">
  <img src="https://img.shields.io/badge/version-1.0.3.1-blue" alt="Version 1.0.3.1">
  <img src="https://img.shields.io/badge/status-early%20access-orange" alt="Early access">
  <img src="https://img.shields.io/badge/license-proprietary-lightgrey" alt="Proprietary original code">
</p>

CacheNorth is a portable toolkit you can put on a USB drive or use from a Windows folder. After setup, its main features work without an internet connection.

- **AI Chat:** ask questions using an AI model running on your computer.
- **Document Search:** search PDF, TXT, and Markdown documents, with source cards.
- **Knowledge Library:** browse offline reference archives in Kiwix.
- **Offline Maps:** open regional Mapsforge maps in GPXSee.
- **Guides:** keep useful reference PDFs together.

## Download

### [Download CacheNorth v1.0.3.1 — Full Portable ZIP](https://downloads.samsonschmidt.com/CacheNorth-v1.0.3.1-Full-Portable.zip)

> [!IMPORTANT]
> The Full Portable ZIP is approximately 16 GB. Browser downloads may fail with `Failed – Network error`. If that happens, use the resumable PowerShell method below.

<details>
<summary><strong>Alternative download method (Windows PowerShell — resumable)</strong></summary>

Windows 10 and 11 include `curl.exe`; no extra download software is needed. Open **PowerShell**, paste the entire block, and press **Enter**. Before starting, move or rename any **unrelated browser-generated partial ZIP** with the same filename in Downloads. Keep any partial file previously created by this method so it can resume.

```powershell
$ErrorActionPreference = "Stop"
$url = "https://downloads.samsonschmidt.com/CacheNorth-v1.0.3.1-Full-Portable.zip"
$file = Join-Path $env:USERPROFILE "Downloads\CacheNorth-v1.0.3.1-Full-Portable.zip"
$expectedSize = [long]15993029771
$expectedHash = "4D6711127EAC4803756963359AD331CA41150385B300C02D862B48B0094EAAED"

for ($attempt = 1; $attempt -le 50; $attempt++) {
    $size = if (Test-Path -LiteralPath $file) { (Get-Item -LiteralPath $file).Length } else { 0 }
    if ($size -gt $expectedSize) { throw "File is larger than expected. Stop and check the file." }
    if ($size -eq $expectedSize) { break }

    Write-Host "Download attempt $attempt of 50 (already have $size bytes)..."
    & curl.exe --http1.1 --fail -L -C - --connect-timeout 30 -o $file $url
    $curlExitCode = $LASTEXITCODE

    $size = if (Test-Path -LiteralPath $file) { (Get-Item -LiteralPath $file).Length } else { 0 }
    if ($size -eq $expectedSize) { break }
    if ($size -gt $expectedSize) { throw "File is larger than expected. Stop and check the file." }
    Write-Warning "Transfer interrupted (curl exit code $curlExitCode); retrying in 5 seconds..."
    Start-Sleep -Seconds 5
}

if (!(Test-Path -LiteralPath $file) -or (Get-Item -LiteralPath $file).Length -ne $expectedSize) {
    throw "Download incomplete after 50 attempts. Run this same block again to resume."
}

Write-Host "Checking SHA-256 (this may take a minute)..."
$actualHash = (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash
if ($actualHash -ne $expectedHash) {
    throw "CHECKSUM MISMATCH. Do not extract or run this ZIP. Get a fresh copy."
}
Write-Host "Download complete and SHA-256 verified: $file"
```

This automatically retries connection resets, resuming from the bytes already downloaded. You can rerun the same block after closing PowerShell or if all 50 attempts fail. **A stable connection cannot be guaranteed.** The script reports success only when the full file size and SHA-256 match; if the checksum fails, do not use the ZIP.

</details>

**ZIP size:** 15,993,029,771 bytes (about 14.9 GiB).

**SHA-256 checksum (verified against the hosted ZIP):**
```text
4D6711127EAC4803756963359AD331CA41150385B300C02D862B48B0094EAAED
```

To verify your downloaded file, open PowerShell and run:

```powershell
Get-FileHash "C:\Path\To\CacheNorth-v1.0.3.1-Full-Portable.zip" -Algorithm SHA256
```

Replace `C:\Path\To\` with where you saved the ZIP. The hash should match the value above. A matching checksum confirms the file is identical to the expected release; it does not prove that software is safe.

> [!NOTE]
> **Free early access:** CacheNorth is still being tested across different computers. Windows 11 CPU operation was tested. Windows 10 is expected to work but has not been tested; compatibility is not guaranteed. 8 GB systems, GPU acceleration, and some security-managed PCs also need additional testing.

## Start in four steps

1. **Download** the Full Portable ZIP above. GitHub's **Code → Download ZIP** contains source code, not the ready-to-run app.
2. **Extract** the ZIP to a writable folder or USB drive. Keep all the extracted files together.
3. **Open** the `CacheNorth-v1.0.3.1-Full-Portable` folder and double-click `Launch CacheNorth.exe`.
4. **Try AI Chat.** CacheNorth selects a bundled Qwen model automatically based on memory. Use **Refresh All** after adding your own content.

[Detailed setup guide](docs/GETTING_STARTED.md)

## Requirements

| Component | Guidance |
|---|---|
| Operating system | 64-bit Windows 10 or 11; Windows 11 tested, Windows 10 expected to work but untested |
| Memory | 16 GB recommended; 8 GB compatibility needs more testing |
| CPU | 64-bit Windows-compatible processor; AVX2 is faster. Compatibility with every older CPU is not guaranteed |
| GPU | Optional; CPU mode works without one. Vulkan acceleration is experimental |
| Storage | About 17.3 GB for extracted files, plus room for the ZIP during extraction |
| USB | 32 GB or larger USB 3 drive or SSD; use a writable exFAT or NTFS volume |

## Where your files go

These paths are **inside** the extracted CacheNorth folder; the drive letter can change.

| Add | Folder | Format |
|---|---|---|
| AI models | `Apps\Offline AI\Models\` | Qwen-family `.gguf` |
| Knowledge archives | `Library\` | `.zim` |
| Maps | `Maps\` | Mapsforge `.map` |
| Guides | `Guides\` | `.pdf` |
| Documents for AI search | `Apps\Offline AI\Data\Documents\` | `.pdf`, `.txt`, `.md` |

[How to add models, archives, maps and documents](docs/ADD_YOUR_CONTENT.md)

## Windows security

CacheNorth's executables are unsigned. Windows SmartScreen or Smart App Control may warn about or block them. Check the download source and checksum, understand the risk, and follow your computer's security policy. **Do not disable Microsoft Defender, SmartScreen, or Smart App Control** to run it. If Windows blocks an optional GPU component, CacheNorth can fall back to CPU mode.

## Need help?

- [First-time setup](docs/GETTING_STARTED.md)
- [Add your own content](docs/ADD_YOUR_CONTENT.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Frequently asked questions](docs/FAQ.md)

## License and safety

Original CacheNorth code and branding are **proprietary**, with limited personal, noncommercial early-access permission under [LICENSE](LICENSE). Bundled third-party components and content have their own terms; see [third-party and content licenses](docs/legal/THIRD_PARTY_LICENSES.md). iFixit noncommercial use and some Chromium/Electron source obligations remain open for redistribution review.

AI answers and offline reference material may be incorrect or outdated. Verify emergency, medical, and navigation information using authoritative sources.

## For developers

The [source project](docs/advanced/BUILDING.md) is separate from the full portable download and does not include the curated model or content files.

- [Build from source](docs/advanced/BUILDING.md)
- [Architecture](docs/advanced/ARCHITECTURE.md)
- [Configuration](docs/advanced/CONFIGURATION.md)
- [Security policy](SECURITY.md)
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)

<!-- Add a privacy-reviewed real screenshot here when one is available. -->
