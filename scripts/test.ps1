$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) { throw "Run scripts\bootstrap.ps1 first." }
New-Item -ItemType Directory -Force -Path (Join-Path $ProjectRoot "build") | Out-Null
Push-Location $ProjectRoot
try {
    & $Python -m pytest --basetemp=build\pytest-temp --cov=security_with_sam --cov-report=term-missing
    if ($LASTEXITCODE -ne 0) { throw "Tests failed." }
    node --test tests\dashboard_keydown.test.js
    if ($LASTEXITCODE -ne 0) { throw "Dashboard keyboard tests failed." }
    node --check dashboard\app.js
    if ($LASTEXITCODE -ne 0) { throw "Dashboard syntax check failed." }
} finally { Pop-Location }
