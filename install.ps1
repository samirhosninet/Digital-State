# Digital State Layer 1 Immutable Bootstrap Stub (v1.16.0)
# Usage: powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/samirhosninet/Digital-State/main/install.ps1 | iex"

[CmdletBinding()]
param (
    [string]$Channel = "stable",
    [string]$Version = "",
    [switch]$Repair,
    [switch]$Uninstall,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13

$RepoOwner = "samirhosninet"
$RepoName = "Digital-State"
$BaseApiUrl = "https://api.github.com/repos/$RepoOwner/$RepoName"

# 1. Resolve Target Release Tag & Download URLs
try {
    if ($Version) {
        $ReleaseUrl = "$BaseApiUrl/releases/tags/$Version"
    } else {
        $ReleaseUrl = "$BaseApiUrl/releases/latest"
    }
    
    # Allow fallback if offline or GitHub API rate-limited during local execution
    $ReleaseInfo = Try { Invoke-RestMethod -Uri $ReleaseUrl -Headers @{ "User-Agent" = "DigitalState-Installer" } } Catch { $null }
    $TargetTag = if ($ReleaseInfo -and $ReleaseInfo.tag_name) { $ReleaseInfo.tag_name } else { "v1.16.0" }
} catch {
    $TargetTag = "v1.16.0"
}

# 2. Locate or Provision Local Python Runtime for Layer 2 Execution
$PythonCmd = Get-Command "python" -ErrorAction SilentlyContinue
if (-not $PythonCmd) {
    $PythonCmd = Get-Command "python3" -ErrorAction SilentlyContinue
}

if (-not $PythonCmd) {
    Write-Host "[*] Python 3.10+ missing. Attempting Winget auto-provisioning..." -ForegroundColor Yellow
    try {
        winget install Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
        $PythonCmd = Get-Command "python" -ErrorAction SilentlyContinue
    } catch {}
}

if (-not $PythonCmd) {
    Write-Error "[-] Python 3.10+ is required to execute Digital State Installer Engine. Installation aborted."
    exit 1
}

# 3. Launch Layer 2 Installer Engine Process
$ScriptDir = $PSScriptRoot
if (-not $ScriptDir) { $ScriptDir = Get-Location }
$env:PYTHONPATH = "$ScriptDir\src;$env:PYTHONPATH"

$Action = "install"
if ($Repair) { $Action = "repair" }
if ($Uninstall) { $Action = "uninstall" }

$DryRunBool = if ($DryRun) { "True" } else { "False" }
$EngineScript = "import sys; sys.path.insert(0, 'src'); from digital_state.bootstrap.engine.orchestrator import run_engine_cli; sys.exit(run_engine_cli('$Action', dry_run=$DryRunBool))"

& $PythonCmd.Source -c $EngineScript
exit $LASTEXITCODE
