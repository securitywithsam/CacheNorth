<#
.SYNOPSIS
  Build a portable CacheNorth folder from source.

.DESCRIPTION
  Produces dist\CacheNorth-<version>\ containing the native launcher, the packaged Python backend,
  the dashboard, the verified unpacked KoboldCpp runtime, documentation, and license notices.
  AI models, knowledge archives, maps, and guides are NOT included; add them afterwards
  (see docs\INSTALLATION.md).

  Prerequisites: run scripts\bootstrap.ps1 and scripts\fetch_third_party.ps1 first.

.PARAMETER OutputDir   Destination folder. Default: dist\CacheNorth-<version>.
.PARAMETER CacheDir    Third-party cache from fetch_third_party.ps1. Default: third_party\cache.
.PARAMETER GpxSeeDir   Optional portable GPXSee folder (containing GPXSee.exe) to bundle as the map viewer.
.PARAMETER GuidesDir   Optional folder with the three CacheNorth PDF guides to place in "Start Here".
.PARAMETER Force       Replace an existing output folder (only allowed inside this project's dist folder).
#>
param(
    [string]$OutputDir = "",
    [string]$CacheDir = "",
    [string]$GpxSeeDir = "",
    [string]$GuidesDir = "",
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$Csc = Join-Path $env:WINDIR "Microsoft.NET\Framework64\v4.0.30319\csc.exe"
$Version = (Select-String -LiteralPath (Join-Path $ProjectRoot "pyproject.toml") -Pattern '^version\s*=\s*"([^"]+)"').Matches[0].Groups[1].Value
if (-not $CacheDir) { $CacheDir = Join-Path $ProjectRoot "third_party\cache" }
if (-not $OutputDir) { $OutputDir = Join-Path $ProjectRoot "dist\CacheNorth-$Version" }
$OutputDir = [System.IO.Path]::GetFullPath($OutputDir)
$Manifest = Get-Content -LiteralPath (Join-Path $ProjectRoot "third_party\manifest.json") -Raw | ConvertFrom-Json
$KoboldVersion = ($Manifest.components | Where-Object name -eq "koboldcpp").version
$WebViewVersion = ($Manifest.components | Where-Object name -eq "webview2-sdk").version
$KoboldDir = Join-Path $CacheDir "koboldcpp-unpacked-$KoboldVersion"
$WebViewDir = Join-Path $CacheDir "webview2-$WebViewVersion"
$WebViewLib = Join-Path $WebViewDir "lib\net462"
$WebViewNative = Join-Path $WebViewDir "runtimes\win-x64\native\WebView2Loader.dll"

# Clear, early checks for every prerequisite.
if (-not (Test-Path -LiteralPath $Python)) { throw "The build environment is missing. Run scripts\bootstrap.ps1 first." }
if (-not (Test-Path -LiteralPath $Csc)) { throw "The Windows .NET Framework 4.x C# compiler was not found at $Csc. It is part of Windows 10/11; enable '.NET Framework 4.8' in Windows Features." }
if (-not (Test-Path -LiteralPath (Join-Path $KoboldDir "koboldcpp-launcher.exe"))) { throw "The verified KoboldCpp runtime is missing from $KoboldDir. Run scripts\fetch_third_party.ps1 first." }
if (-not (Test-Path -LiteralPath (Join-Path $WebViewLib "Microsoft.Web.WebView2.WinForms.dll"))) { throw "The WebView2 SDK is missing from $WebViewDir. Run scripts\fetch_third_party.ps1 first." }
if ($GpxSeeDir -and -not (Test-Path -LiteralPath (Join-Path $GpxSeeDir "GPXSee.exe"))) { throw "-GpxSeeDir must be a folder containing GPXSee.exe." }

# Never overwrite silently, and never delete outside this project's dist folder.
if (Test-Path -LiteralPath $OutputDir) {
    $distRoot = [System.IO.Path]::GetFullPath((Join-Path $ProjectRoot "dist")) + [System.IO.Path]::DirectorySeparatorChar
    if (-not $Force) { throw "$OutputDir already exists. Choose another -OutputDir or pass -Force to replace it." }
    if (-not $OutputDir.StartsWith($distRoot, [System.StringComparison]::OrdinalIgnoreCase)) { throw "-Force only replaces folders inside $distRoot." }
    Remove-Item -LiteralPath $OutputDir -Recurse -Force
}

$Product = Join-Path $OutputDir "Apps\Offline AI"
$Documentation = Join-Path $Product "Documentation"
$Licenses = Join-Path $Documentation "Licenses"
New-Item -ItemType Directory -Force -Path $Product, $Documentation, $Licenses | Out-Null

Write-Output "Building CacheNorth $Version into $OutputDir"
$BuildRoot = Join-Path $ProjectRoot "build"
Push-Location $ProjectRoot
try {
    & $Python -m PyInstaller --noconfirm --clean --windowed --onedir --name SecurityWithSamOfflineAI `
        --icon (Join-Path $ProjectRoot "launcher\CacheNorth.ico") `
        --version-file (Join-Path $ProjectRoot "scripts\cache_north_version_info.txt") `
        --paths src --distpath (Join-Path $BuildRoot "pyinstaller\dist") --workpath (Join-Path $BuildRoot "pyinstaller\work") `
        --specpath (Join-Path $BuildRoot "pyinstaller") run_offline_ai.py
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed." }
} finally { Pop-Location }

Copy-Item -LiteralPath (Join-Path $BuildRoot "pyinstaller\dist\SecurityWithSamOfflineAI") -Destination (Join-Path $Product "Runtime") -Recurse
Copy-Item -LiteralPath (Join-Path $ProjectRoot "dashboard") -Destination (Join-Path $Product "Dashboard") -Recurse
Copy-Item -LiteralPath $KoboldDir -Destination (Join-Path $Product "KoboldCpp") -Recurse
# KoboldCpp's own CPU feature probe doubles as CacheNorth's AVX/AVX2 detector.
Copy-Item -LiteralPath (Join-Path $KoboldDir "simplecpuinfo.exe") -Destination (Join-Path $Product "cache-north-cpuinfo.exe")

Copy-Item -LiteralPath (Join-Path $ProjectRoot "README.md") -Destination $Documentation
Copy-Item -Path (Join-Path $ProjectRoot "docs\*.md") -Destination $Documentation
Copy-Item -Path (Join-Path $ProjectRoot "licenses\*") -Destination $Licenses -Recurse
Copy-Item -LiteralPath (Join-Path $WebViewDir "LICENSE.txt") -Destination (Join-Path $Licenses "Microsoft.Web.WebView2-SDK.txt")
& $Python (Join-Path $ProjectRoot "scripts\collect_runtime_licenses.py") --output (Join-Path $Licenses "Runtime Licenses")
if ($LASTEXITCODE -ne 0) { throw "Collecting runtime license files failed." }

& $Csc /nologo /target:winexe /platform:x64 /optimize+ "/win32icon:$(Join-Path $ProjectRoot 'launcher\CacheNorth.ico')" `
    /reference:System.Windows.Forms.dll /reference:System.Drawing.dll /reference:System.Web.Extensions.dll `
    "/reference:$(Join-Path $WebViewLib 'Microsoft.Web.WebView2.Core.dll')" "/reference:$(Join-Path $WebViewLib 'Microsoft.Web.WebView2.WinForms.dll')" `
    "/out:$(Join-Path $OutputDir 'Launch CacheNorth.exe')" (Join-Path $ProjectRoot "launcher\StartOfflineAI.cs")
if ($LASTEXITCODE -ne 0) { throw "Native launcher build failed." }
Copy-Item -LiteralPath (Join-Path $WebViewLib "Microsoft.Web.WebView2.Core.dll"), (Join-Path $WebViewLib "Microsoft.Web.WebView2.WinForms.dll"), $WebViewNative -Destination $OutputDir

foreach ($name in "Models") { New-Item -ItemType Directory -Force -Path (Join-Path $Product $name) | Out-Null }
foreach ($name in "Documents", "Index", "Chats", "Logs", "GPXSee") { New-Item -ItemType Directory -Force -Path (Join-Path $Product "Data\$name") | Out-Null }
foreach ($name in "Library", "Maps", "Guides", "Start Here") { New-Item -ItemType Directory -Force -Path (Join-Path $OutputDir $name) | Out-Null }
Set-Content -LiteralPath (Join-Path $Product "Models\PUT GGUF MODELS HERE.txt") -Value "Copy compatible GGUF model files into this folder. See Documentation\INSTALLATION.md."
Set-Content -LiteralPath (Join-Path $OutputDir "Library\PUT ZIM ARCHIVES HERE.txt") -Value "Copy Kiwix .zim archives into this folder. See Apps\Offline AI\Documentation\INSTALLATION.md."
Set-Content -LiteralPath (Join-Path $OutputDir "Maps\PUT MAP FILES HERE.txt") -Value "Copy Mapsforge .map files into this folder. See Apps\Offline AI\Documentation\INSTALLATION.md."
Set-Content -LiteralPath (Join-Path $OutputDir "Guides\PUT PDF GUIDES HERE.txt") -Value "Copy PDF guides into this folder; CacheNorth lists them on the Guides page."
Copy-Item -LiteralPath (Join-Path $ProjectRoot "docs\INSTALLATION.md"), (Join-Path $ProjectRoot "docs\TROUBLESHOOTING.md") -Destination (Join-Path $OutputDir "Start Here")

if ($GuidesDir) {
    Get-ChildItem -LiteralPath $GuidesDir -Filter "CacheNorth *.pdf" -File | Copy-Item -Destination (Join-Path $OutputDir "Start Here")
} else {
    Write-Output "Note: no -GuidesDir given; the dashboard's Quick Start and Troubleshooting buttons need the PDF guides (see docs\BUILDING.md). Markdown copies were placed in Start Here."
}
if ($GpxSeeDir) {
    Copy-Item -LiteralPath $GpxSeeDir -Destination (Join-Path $OutputDir "Apps\GPXSee") -Recurse
    $uninstaller = Join-Path $OutputDir "Apps\GPXSee\uninstall.exe"
    if (Test-Path -LiteralPath $uninstaller) { Remove-Item -LiteralPath $uninstaller -Force }
} else {
    Write-Output "Note: no -GpxSeeDir given; Offline Maps will report the viewer as unavailable until GPXSee is added to Apps\GPXSee."
}

$inputs = foreach ($component in $Manifest.components) { "$($component.name) $($component.version) sha256=$($component.sha256)" }
@("CacheNorth $Version", "Built $(Get-Date -Format o)", "Third-party inputs:", $inputs) | Set-Content -LiteralPath (Join-Path $Product "BUILD-INFO.txt")
Write-Output "Build complete: $OutputDir"
