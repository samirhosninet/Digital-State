# Digital State Idempotent PowerShell Installer (v1.14.0-bootstrap)
# Usage: powershell -ExecutionPolicy Bypass -File install.ps1 [-DryRun]

[CmdletBinding()]
param (
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host " Digital State Zero-Touch Installer (v1.14.0-bootstrap)" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan

# 1. Verify Python Version
$pythonCmd = Get-Command "python" -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    $pythonCmd = Get-Command "python3" -ErrorAction SilentlyContinue
}

if (-not $pythonCmd) {
    Write-Error "Python is not installed or not available in PATH. Python 3.11+ required."
    exit 1
}

$pyVersionStr = & $pythonCmd.Source --version 2>&1
Write-Host "[+] Detected: $pyVersionStr" -ForegroundColor Green

# 2. Execute Bootstrap Dry-Run or Full Install via Python Module
$env:PYTHONPATH = "src"

if ($DryRun) {
    Write-Host "[*] Executing Dry-Run Verification..." -ForegroundColor Yellow
    & $pythonCmd.Source -c "import sys; sys.path.insert(0, 'src'); from digital_state.bootstrap.installer import BootstrapInstaller; res = BootstrapInstaller().run_bootstrap(dry_run=True); print(res); sys.exit(0 if res.get('status') == 'DRY_RUN_SUCCESS' else 1)"
} else {
    Write-Host "[*] Executing Idempotent Workspace Installation..." -ForegroundColor Yellow
    & $pythonCmd.Source -c "import sys; sys.path.insert(0, 'src'); from digital_state.bootstrap.installer import BootstrapInstaller; res = BootstrapInstaller().run_bootstrap(dry_run=False); print(res); sys.exit(0 if res.get('status') == 'SUCCESS' else 1)"
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "[+] Digital State Installation Completed Successfully." -ForegroundColor Green
} else {
    Write-Host "[-] Installation failed." -ForegroundColor Red
    exit 1
}
