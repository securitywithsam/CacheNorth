# Verify an existing CacheNorth portable ZIP without extracting or modifying it.
# Usage: powershell -ExecutionPolicy Bypass -File scripts\verify_portable_zip.ps1 -ZipPath "C:\Downloads\CacheNorth-v1.0.3-Full-Portable.zip"
param(
    [Parameter(Mandatory = $true)][string]$ZipPath,
    [string]$ExpectedSha256 = "",
    [string]$InventoryPath = ""
)
$ErrorActionPreference = "Stop"
$resolved = (Resolve-Path -LiteralPath $ZipPath).Path
if (-not (Test-Path -LiteralPath $resolved -PathType Leaf)) { throw "ZIP file not found: $ZipPath" }
Add-Type -AssemblyName System.IO.Compression
$hash = (Get-FileHash -LiteralPath $resolved -Algorithm SHA256).Hash.ToLowerInvariant()
Write-Host "Archive: $resolved"
Write-Host "Bytes: $((Get-Item -LiteralPath $resolved).Length)"
Write-Host "SHA-256: $hash"
if ($ExpectedSha256 -and $hash -ne $ExpectedSha256.ToLowerInvariant()) {
    throw "ZIP SHA-256 differs from expected value. Do not distribute."
}
$zip = [System.IO.Compression.ZipFile]::OpenRead($resolved)
try {
    $entries = @($zip.Entries | Where-Object { $_.Name -ne "" })
    $names = @($entries | ForEach-Object { $_.FullName.Replace('\','/') })
    $unsafe = @($names | Where-Object { $_ -match '(^/|(^|/)\.\.(/|$)|^[A-Za-z]:)' })
    $private = @($names | Where-Object {
        $_ -match '(?i)(^|/)(settings\.json|cache-north-session\.json|conversations?\.db|\.env|id_rsa|.*\.pem|.*\.key)$' -or
        $_ -match '(?i)(^|/)(Data/Documents|Data/Logs|Data/Conversations|__pycache__)/'
    })
    $dupes = @($names | Group-Object | Where-Object Count -gt 1 | Select-Object -ExpandProperty Name)
    $record = @($entries | Select-Object FullName, Length, CompressedLength)
    Write-Host "Files: $($entries.Count); uncompressed bytes: $(($entries | Measure-Object Length -Sum).Sum)"
    if ($InventoryPath) {
        $record | Export-Csv -LiteralPath $InventoryPath -NoTypeInformation -Encoding UTF8
        Write-Host "Inventory saved: $InventoryPath"
    }
    if ($unsafe.Count -or $private.Count -or $dupes.Count) {
        if ($unsafe.Count) { Write-Warning "Unsafe archive paths: $($unsafe -join ', ')" }
        if ($private.Count) { Write-Warning "Potential private runtime data: $($private -join ', ')" }
        if ($dupes.Count) { Write-Warning "Duplicate archive names: $($dupes -join ', ')" }
        throw "Archive inventory checks failed. Review the names before distributing."
    }
    Write-Host "Archive path/inventory checks passed."
    Write-Warning "This checks ZIP metadata, path safety and SHA-256. It does not validate CRC of all extracted bytes, file contents, licensing, malware, or hardware compatibility."
}
finally { $zip.Dispose() }
