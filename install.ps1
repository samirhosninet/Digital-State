# Digital State Layer 1 Immutable Zero-Touch Bootstrap Stub (v1.16.0)
# Usage: powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/samirhosninet/Digital-State/main/install.ps1 | iex"

$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13

$Channel = if ($env:DS_CHANNEL) { $env:DS_CHANNEL } else { "stable" }
$Version = if ($env:DS_VERSION) { $env:DS_VERSION } else { "" }
$Action  = if ($env:DS_ACTION)  { $env:DS_ACTION }  else { "install" }
$DryRunBool = if ($env:DS_DRY_RUN -eq "1") { "True" } else { "False" }

$RepoOwner = "samirhosninet"
$RepoName = "Digital-State"
$BaseApiUrl = "https://api.github.com/repos/$RepoOwner/$RepoName"

# 1. Resolve Target Release Tag
try {
    if ($Version) {
        $ReleaseUrl = "$BaseApiUrl/releases/tags/$Version"
    } else {
        $ReleaseUrl = "$BaseApiUrl/releases/latest"
    }
    $ReleaseInfo = Try { Invoke-RestMethod -Uri $ReleaseUrl -Headers @{ "User-Agent" = "DigitalState-Installer" } } Catch { $null }
    $TargetTag = if ($ReleaseInfo -and $ReleaseInfo.tag_name) { $ReleaseInfo.tag_name } else { "v1.16.0" }
} catch {
    $TargetTag = "v1.16.0"
}

# 2. Locate or Auto-Provision Python 3.10+ Runtime
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

# 3. Create Isolated Temp Workspace & Fetch Installer Engine Payload
$TempWorkspace = Join-Path $env:TEMP "ds-bootstrap-$([guid]::NewGuid().ToString('N'))"
$EngineDir = Join-Path $TempWorkspace "engine"
New-Item -ItemType Directory -Path $EngineDir -Force | Out-Null

$ZipUrl = "https://github.com/$RepoOwner/$RepoName/archive/refs/heads/main.zip"
$ZipPath = Join-Path $TempWorkspace "ds-installer.zip"

try {
    # Download Engine zipball from GitHub
    Invoke-WebRequest -Uri $ZipUrl -OutFile $ZipPath -UseBasicParsing
    Expand-Archive -Path $ZipPath -DestinationPath $TempWorkspace -Force
    
    # Locate extracted src directory
    $ExtractedSrc = Get-ChildItem -Path $TempWorkspace -Filter "src" -Recurse | Select-Object -First 1
    if ($ExtractedSrc) {
        $EnginePath = $ExtractedSrc.FullName
    } else {
        $EnginePath = $EngineDir
    }
} catch {
    # Fallback to local script directory if offline
    $ScriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Get-Location }
    $EnginePath = Join-Path $ScriptDir "src"
}

# 4. Launch Layer 2 Installer Engine Process
$env:PYTHONPATH = "$EnginePath;$env:PYTHONPATH"

$EngineScript = "import sys; sys.path.insert(0, r'$EnginePath'); from digital_state.bootstrap.engine.orchestrator import run_engine_cli; sys.exit(run_engine_cli('$Action', dry_run=$DryRunBool))"

try {
    & $PythonCmd.Source -c $EngineScript
    $ExitCode = $LASTEXITCODE
} finally {
    if (Test-Path $TempWorkspace) {
        Remove-Item -Path $TempWorkspace -Recurse -Force -ErrorAction SilentlyContinue
    }
}

exit $ExitCode
