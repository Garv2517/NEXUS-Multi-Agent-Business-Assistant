$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $repoRoot "backend"
$frontend = Join-Path $repoRoot "frontend"

Write-Host "=== NEXUS FINAL REGRESSION ===" -ForegroundColor Cyan

Write-Host "[1/4] Rebuilding analytics DB..." -ForegroundColor Yellow
Push-Location $backend
& .\.venv\Scripts\python.exe scripts\import_kaggle_dataset.py
if ($LASTEXITCODE -ne 0) { Pop-Location; throw "Analytics rebuild failed." }

Write-Host "[2/4] Running backend tests in deterministic/offline test mode..." -ForegroundColor Yellow
$oldMode = $env:ORCHESTRATION_MODE
$oldFallback = $env:FOUNDRY_FALLBACK_TO_LOCAL
try {
    # Ordinary regression tests must never spend Azure quota or depend on developer .env.
    # Foundry-specific tests inject mocked routers and explicitly select foundry_manager mode.
    $env:ORCHESTRATION_MODE = "local"
    $env:FOUNDRY_FALLBACK_TO_LOCAL = "true"
    & .\.venv\Scripts\python.exe -m pytest -W default
    if ($LASTEXITCODE -ne 0) { throw "Backend tests failed." }
}
finally {
    if ($null -eq $oldMode) { Remove-Item Env:ORCHESTRATION_MODE -ErrorAction SilentlyContinue } else { $env:ORCHESTRATION_MODE = $oldMode }
    if ($null -eq $oldFallback) { Remove-Item Env:FOUNDRY_FALLBACK_TO_LOCAL -ErrorAction SilentlyContinue } else { $env:FOUNDRY_FALLBACK_TO_LOCAL = $oldFallback }
}
Pop-Location

Write-Host "[3/4] Building frontend..." -ForegroundColor Yellow
Push-Location $frontend
& npm.cmd run build
if ($LASTEXITCODE -ne 0) { Pop-Location; throw "Frontend build failed." }
Pop-Location

Write-Host "[4/4] Git status..." -ForegroundColor Yellow
Push-Location $repoRoot
git status --short
Pop-Location

Write-Host "=== NEXUS FINAL REGRESSION PASSED ===" -ForegroundColor Green
