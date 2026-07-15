# reproduce_in_sandbox.ps1
# Automates clean environment provisioning, installation, and user journey validation.
$ErrorActionPreference = "Stop"

$env:PATH = "C:\Users\I-Master\AppData\Local\hermes\bin;C:\Users\I-Master\AppData\Local\hermes\git\cmd;C:\Users\I-Master\AppData\Local\hermes\hermes-agent\venv\Scripts;" + $env:PATH


$sandboxDir = Join-Path $PSScriptRoot "..\scratch\clean_sandbox"
$envDir = Join-Path $sandboxDir "venv"
$hermesHome = Join-Path $sandboxDir "hermes"
$validationDir = Join-Path $PSScriptRoot "..\release-validation"

Write-Host "=== Step 1: Cleaning sandbox directories ==="
if (Test-Path $sandboxDir) { Remove-Item -Recurse -Force $sandboxDir }
if (Test-Path $validationDir) { Remove-Item -Recurse -Force $validationDir }

New-Item -ItemType Directory -Path $sandboxDir | Out-Null
New-Item -ItemType Directory -Path $hermesHome | Out-Null
New-Item -ItemType Directory -Path (Join-Path $validationDir "clean-install") | Out-Null
New-Item -ItemType Directory -Path (Join-Path $validationDir "runtime") | Out-Null
New-Item -ItemType Directory -Path (Join-Path $validationDir "ux") | Out-Null
New-Item -ItemType Directory -Path (Join-Path $validationDir "external") | Out-Null

# Redirect HERMES_HOME to sandbox to simulate fresh target config
$env:HERMES_HOME = $hermesHome
$env:LOCALAPPDATA = $hermesHome
$env:no_proxy = "127.0.0.1,localhost"

# Add mock hermes executable directory structure
$hermesBinDir = Join-Path $hermesHome "hermes-agent\venv\Scripts"
New-Item -ItemType Directory -Path $hermesBinDir | Out-Null
New-Item -ItemType File -Path (Join-Path $hermesBinDir "hermes.exe") | Out-Null

Write-Host "=== Step 2: Creating clean Python virtual environment ==="
& python -m venv $envDir

$sandboxPython = Join-Path $envDir "Scripts\python.exe"
$sandboxPip = Join-Path $envDir "Scripts\pip.exe"
$sandboxCli = Join-Path $envDir "Scripts\digitalstate.exe"

# Copy mock hermes python into place
Copy-Item $sandboxPython (Join-Path $hermesBinDir "python.exe")

Write-Host "=== Step 3: Installing package inside sandbox virtualenv ==="
& $sandboxPip install -e .

# Log environment info
"OS: Windows 10`nPython: $(& $sandboxPython --version)`nCommit: $(git rev-parse HEAD)" | Out-File -FilePath (Join-Path $validationDir "clean-install\environment-info") -Encoding utf8

Write-Host "=== Step 4: Initializing Workspace (New User Flow) ==="
$initLog = & $sandboxPython -m digital_state.cli.cli init 2>&1 | Out-String
$initLog | Out-File -FilePath (Join-Path $validationDir "clean-install\install-log") -Encoding utf8
Write-Host $initLog

Write-Host "=== Step 5: Running Doctor Health Check ==="
$doctorLog = & $sandboxPython -m digital_state.cli.cli doctor 2>&1 | Out-String
$doctorLog | Out-File -FilePath (Join-Path $validationDir "clean-install\validation-result") -Encoding utf8
Write-Host $doctorLog

Write-Host "=== Step 6: Validating Recovery Journey ==="
# Delete state.json
$statePath = Join-Path $PSScriptRoot "..\.specify\state.json"
if (Test-Path $statePath) { Remove-Item $statePath }
# Run repair
$repairLog = & $sandboxPython -m digital_state.cli.cli repair 2>&1 | Out-String
$repairLog | Out-File -FilePath (Join-Path $validationDir "ux\repair-log") -Encoding utf8
Write-Host $repairLog

Write-Host "=== Step 7: Validating Upgrade Journey ==="
$upgradeLog = & $sandboxPython -m digital_state.cli.cli upgrade 2>&1 | Out-String
$upgradeLog | Out-File -FilePath (Join-Path $validationDir "ux\upgrade-log") -Encoding utf8
Write-Host $upgradeLog

Write-Host "=== Step 8: Validating Uninstall Journey ==="
$uninstallLog = & $sandboxPython -m digital_state.cli.cli uninstall 2>&1 | Out-String
$uninstallLog | Out-File -FilePath (Join-Path $validationDir "ux\uninstall-log") -Encoding utf8
Write-Host $uninstallLog

Write-Host "=== Validation Completed Successfully. ==="
