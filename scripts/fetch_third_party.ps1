<#
.SYNOPSIS
  Download and verify the third-party build inputs listed in third_party\manifest.json.

.DESCRIPTION
  Downloads (or reuses) KoboldCpp and the WebView2 SDK, verifies each file's SHA-256 against the
  manifest, extracts the WebView2 package, and unpacks KoboldCpp into a portable folder. Nothing is
  used unless its hash matches. Requires internet access unless every file is already in -CacheDir.

.PARAMETER CacheDir
  Where downloads and extracted files are kept. Default: third_party\cache (ignored by Git).

.PARAMETER Offline
  Never download. Fail with a clear message if a file is missing from -CacheDir.
#>
param(
    [string]$CacheDir = "",
    [switch]$Offline
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
if (-not $CacheDir) { $CacheDir = Join-Path $ProjectRoot "third_party\cache" }
$CacheDir = [System.IO.Path]::GetFullPath($CacheDir)
$Manifest = Get-Content -LiteralPath (Join-Path $ProjectRoot "third_party\manifest.json") -Raw | ConvertFrom-Json
New-Item -ItemType Directory -Force -Path $CacheDir | Out-Null

function Get-Component([string]$Name) {
    $item = $Manifest.components | Where-Object name -eq $Name
    if (-not $item) { throw "third_party\manifest.json has no entry named '$Name'." }
    return $item
}

function Get-VerifiedFile($Component) {
    $path = Join-Path $CacheDir $Component.file
    if (-not (Test-Path -LiteralPath $path)) {
        if ($Offline) { throw "Missing $($Component.file) in $CacheDir. Download it from $($Component.url) or run without -Offline." }
        # Write-Host, not Write-Output: anything written to the output stream becomes part of the return value.
        Write-Host "Downloading $($Component.name) $($Component.version) from $($Component.url)"
        $partial = "$path.partial"
        Invoke-WebRequest -Uri $Component.url -OutFile $partial -UseBasicParsing
        Move-Item -LiteralPath $partial -Destination $path -Force
    }
    $actual = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash
    if ($actual -ne $Component.sha256) {
        throw "SHA-256 mismatch for $($Component.file).`nExpected $($Component.sha256)`nActual   $actual`nDelete the file and download it again from $($Component.url). Do not use a file that fails this check."
    }
    Write-Host "Verified $($Component.file) ($actual)"
    return $path
}

function Get-TreeHash([string]$Root) {
    $lines = [System.Collections.Generic.List[string]]::new()
    Get-ChildItem -LiteralPath $Root -Recurse -File | ForEach-Object {
        $relative = $_.FullName.Substring($Root.Length + 1).Replace('\', '/')
        $lines.Add("$relative`t$((Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash)`n")
    }
    $array = $lines.ToArray()
    [Array]::Sort($array, [StringComparer]::Ordinal)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes(($array -join ""))
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { return @{ Hash = ([BitConverter]::ToString($sha.ComputeHash($bytes)) -replace '-', ''); Count = $array.Count } } finally { $sha.Dispose() }
}

# WebView2 SDK: a NuGet package is a ZIP. .NET's extractor rejects entries that escape the target folder.
$webview = Get-Component "webview2-sdk"
$nupkg = Get-VerifiedFile $webview
$webviewDir = Join-Path $CacheDir "webview2-$($webview.version)"
if (-not (Test-Path -LiteralPath (Join-Path $webviewDir "lib\net462\Microsoft.Web.WebView2.WinForms.dll"))) {
    if (Test-Path -LiteralPath $webviewDir) { Remove-Item -LiteralPath $webviewDir -Recurse -Force }
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::ExtractToDirectory($nupkg, $webviewDir)
}
Write-Output "WebView2 SDK ready: $webviewDir"

# KoboldCpp: unpack the verified one-file release with its own --unpack option, then verify every file.
$kobold = Get-Component "koboldcpp"
$exe = Get-VerifiedFile $kobold
$unpacked = Join-Path $CacheDir "koboldcpp-unpacked-$($kobold.version)"
if (-not (Test-Path -LiteralPath (Join-Path $unpacked "koboldcpp-launcher.exe"))) {
    if (Test-Path -LiteralPath $unpacked) { Remove-Item -LiteralPath $unpacked -Recurse -Force }
    Write-Output "Unpacking KoboldCpp (this runs the verified official executable once)..."
    $process = Start-Process -FilePath $exe -ArgumentList @("--unpack", "`"$unpacked`"") -Wait -PassThru -WindowStyle Hidden
    if ($process.ExitCode -ne 0) { throw "KoboldCpp --unpack exited with code $($process.ExitCode)." }
}
$tree = Get-TreeHash $unpacked
if ($tree.Hash -ne $kobold.unpacked_tree_sha256 -or $tree.Count -ne $kobold.unpacked_file_count) {
    throw "The unpacked KoboldCpp folder does not match the expected contents ($($tree.Count) files, tree $($tree.Hash)). Delete $unpacked and run this script again."
}
Write-Output "KoboldCpp unpacked and verified: $unpacked ($($tree.Count) files)"
Write-Output "Third-party inputs ready in $CacheDir"
