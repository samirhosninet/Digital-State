# Digital State Windows Installer Script (install.ps1)
# Verifies environment, installs dependencies, and runs workspace bootstrap.

$ErrorActionPreference = "Stop"

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Digital State Governance Installer (Windows)" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# 1. Validate Python >= 3.11 prerequisite
Write-Host "[1/3] Checking Python prerequisite..." -ForegroundColor Yellow
try {
    $pyVersionRaw = & python --version 2>&1
    $pyVersionStr = ($pyVersionRaw | Out-String).Trim()
    
    if ($pyVersionStr -match "Python (\d+)\.(\d+)\.(\d+)") {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]
        Write-Host "Found Python version: $pyVersionStr" -ForegroundColor Gray
        
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 11)) {
            Write-Error "Python 3.11 or higher is required. Found version: $pyVersionStr"
        }
    } else {
        Write-Error "Could not parse Python version from: $pyVersionStr"
    }
} catch {
    Write-Error "Python is not installed or not available in system PATH. Please install Python 3.11+."
}

# 2. Install Project Dependencies
Write-Host "[2/3] Installing Digital State package dependencies..." -ForegroundColor Yellow

$hasUv = $null -ne (Get-Command uv -ErrorAction SilentlyContinue)
if ($hasUv) {
    Write-Host "Found 'uv' package manager. Installing with uv..." -ForegroundColor Gray
    & uv pip install -e .
} else {
    Write-Host "'uv' not found. Installing with pip..." -ForegroundColor Gray
    & pip install -e .
}

# 3. Initialize workspace
Write-Host "[3/3] Bootstrapping workspace state..." -ForegroundColor Yellow

$localBinPath = Join-Path $PSScriptRoot ".specify\..\.venv\Scripts\digitalstate.exe"
$localPythonPath = Join-Path $PSScriptRoot ".specify\..\.venv\Scripts\python.exe"

if (Test-Path $localBinPath) {
    Write-Host "Running bootstrap via local virtualenv CLI..." -ForegroundColor Gray
    & $localBinPath init
} elseif (Test-Path $localPythonPath) {
    Write-Host "Running bootstrap via local virtualenv Python..." -ForegroundColor Gray
    $env:PYTHONPATH = "src"
    & $localPythonPath -m digital_state.cli.cli init
} else {
    Write-Host "Running bootstrap via system Python..." -ForegroundColor Gray
    & python -m digital_state.cli.cli init
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host "  Digital State Installed Successfully!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host "To verify installation, run:" -ForegroundColor Gray

if (Test-Path $localBinPath) {
    Write-Host "  .venv\Scripts\digitalstate doctor" -ForegroundColor White
} elseif (Test-Path $localPythonPath) {
    Write-Host "  $localPythonPath -m digital_state.cli.cli doctor" -ForegroundColor White
} else {
    Write-Host "  digitalstate doctor" -ForegroundColor White
}
Write-Host ""


