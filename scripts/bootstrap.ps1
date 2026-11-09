<#
.SYNOPSIS
  Create the CacheNorth development environment (.venv) with the pinned dependencies.

.PARAMETER Python
  Path to an existing 64-bit Python 3.12 or 3.13 interpreter. If omitted, the script tries the
  Windows "py -3.12" launcher, then installs a project-local Python 3.12.8 from the hash-verified
  python.org installer listed in third_party\manifest.json.

.PARAMETER WithDocs
  Also install the optional PDF-guide tooling (requirements\docs.txt).

Requires internet access to download packages from PyPI (and the Python installer if needed).
#>
param(
    [string]$Python = "",
    [switch]$WithDocs
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

function Test-SupportedPython([string]$Candidate) {
    if (-not $Candidate) { return $false }
    try {
        $version = & $Candidate -c "import struct,sys; print(f'{sys.version_info[0]}.{sys.version_info[1]} {struct.calcsize(chr(80))*8}')" 2>$null
        return $version -match '^3\.(12|13) 64$'
    } catch { return $false }
}

if (-not $Python) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $found = & py -3.12 -c "import sys; print(sys.executable)" 2>$null
        if ($LASTEXITCODE -eq 0 -and (Test-SupportedPython $found)) { $Python = $found }
    }
}
if (-not $Python) {
    $local = Join-Path $ProjectRoot ".tools\python312\python.exe"
    if (-not (Test-Path -LiteralPath $local)) {
        $manifest = Get-Content -LiteralPath (Join-Path $ProjectRoot "third_party\manifest.json") -Raw | ConvertFrom-Json
        $entry = $manifest.components | Where-Object name -eq "python-installer"
        $installer = Join-Path $ProjectRoot ".tools\$($entry.file)"
        New-Item -ItemType Directory -Force -Path (Split-Path $installer) | Out-Null
        if (-not (Test-Path -LiteralPath $installer)) {
            Write-Output "Python 3.12 was not found. Downloading $($entry.url)"
            Invoke-WebRequest -Uri $entry.url -OutFile $installer -UseBasicParsing
        }
        $hash = (Get-FileHash -LiteralPath $installer -Algorithm SHA256).Hash
        if ($hash -ne $entry.sha256) { throw "The Python installer's SHA-256 ($hash) does not match third_party\manifest.json. Delete $installer and try again." }
        $arguments = @("/quiet", "InstallAllUsers=0", "Include_launcher=0", "Include_test=0", "Include_doc=0",
                       "Include_dev=0", "Include_pip=1", "PrependPath=0", "Shortcuts=0", "TargetDir=$(Split-Path $local)")
        $process = Start-Process -FilePath $installer -ArgumentList $arguments -Wait -PassThru -WindowStyle Hidden
        if ($process.ExitCode -ne 0) { throw "The Python installer exited with code $($process.ExitCode)." }
    }
    $Python = $local
}
if (-not (Test-SupportedPython $Python)) { throw "CacheNorth needs 64-bit Python 3.12 or 3.13. '$Python' is not suitable. Pass -Python <path to python.exe>." }

$venv = Join-Path $ProjectRoot ".venv"
$venvPython = Join-Path $venv "Scripts\python.exe"
if (-not (Test-Path -LiteralPath $venvPython)) {
    & $Python -m venv $venv
    if ($LASTEXITCODE -ne 0) { throw "Could not create $venv." }
}
& $venvPython -m pip install --disable-pip-version-check -r (Join-Path $ProjectRoot "requirements\dev.txt")
if ($LASTEXITCODE -ne 0) { throw "Installing requirements\dev.txt failed. Check your internet connection and try again." }
if ($WithDocs) {
    & $venvPython -m pip install --disable-pip-version-check -r (Join-Path $ProjectRoot "requirements\docs.txt")
    if ($LASTEXITCODE -ne 0) { throw "Installing requirements\docs.txt failed." }
}
Write-Output "Development environment ready: $venvPython"
