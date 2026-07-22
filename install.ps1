# Digital State Layer 1 Immutable Zero-Touch Bootstrap Stub (v1.16.1)
# Usage: powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/samirhosninet/Digital-State/main/install.ps1 | iex"

$ErrorActionPreference = "Stop"

# --- Transport security (safe on stock Windows PowerShell 5.1 / legacy .NET) ---
# The Tls13 enum member is NOT present on stock .NET Framework 4.x and referencing it
# by name throws at parse time. Use numeric constants (Tls12=3072, Tls13=12288) and
# only OR-in Tls13 when the enum actually defines it.
try {
    $secProto = [Net.ServicePointManager]::SecurityProtocol -bor 3072
    if ([Net.SecurityProtocolType]::GetNames([Net.SecurityProtocolType]) -contains 'Tls13') {
        $secProto = $secProto -bor 12288
    }
    [Net.ServicePointManager]::SecurityProtocol = $secProto
} catch {
    # Best-effort: modern Windows ships sane TLS defaults.
}

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
    $ReleaseInfo = Invoke-RestMethod -Uri $ReleaseUrl -Headers @{ "User-Agent" = "DigitalState-Installer" } -ErrorAction SilentlyContinue
    $TargetTag = if ($ReleaseInfo -and $ReleaseInfo.tag_name) { $ReleaseInfo.tag_name } else { "v1.16.0" }
} catch {
    $TargetTag = "v1.16.0"
}

# 2. Locate or Auto-Provision Python 3.10+ Runtime
function Find-Python {
    $p = Get-Command "python" -ErrorAction SilentlyContinue
    if ($p) { return $p.Source }
    $p = Get-Command "python3" -ErrorAction SilentlyContinue
    if ($p) { return $p.Source }

    # Winget installs do not refresh PATH in the current session; probe known locations.
    $probePaths = @(
        "$env:LOCALAPPDATA\Microsoft\WindowsApps\python.exe",
        "$env:LOCALAPPDATA\Microsoft\WindowsApps\python3.exe",
        "$env:ProgramFiles\Python311\python.exe",
        "$env:ProgramFiles\Python310\python.exe",
        "$env:ProgramFiles\Python312\python.exe",
        "${env:ProgramFiles(x86)}\Python311\python.exe"
    )
    foreach ($pp in $probePaths) {
        if ($pp -and (Test-Path $pp)) { return $pp }
    }
    return $null
}

$PythonCmd = Find-Python

if (-not $PythonCmd) {
    Write-Host "[*] Python 3.10+ missing. Attempting Winget auto-provisioning..." -ForegroundColor Yellow
    try {
        winget install Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements --scope user
    } catch {}
    # Refresh PATH from machine + user stores and re-probe.
    try {
        $env:PATH = [Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [Environment]::GetEnvironmentVariable("PATH", "User")
    } catch {}
    $PythonCmd = Find-Python
}

if (-not $PythonCmd) {
    Write-Error "[-] Python 3.10+ is required to execute Digital State Installer Engine. Installation aborted."
    exit 1
}

# Verify minimum Python version explicitly (do not assume Get-Command result).
try {
    $verOut = & $PythonCmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
    $maj, $min = ($verOut.Trim() -split '\.')[0, 1]
    if (-not (($maj -eq 3 -and [int]$min -ge 10) -or ([int]$maj -gt 3))) {
        Write-Error "[-] Python 3.10+ required (found $verOut). Installation aborted."
        exit 1
    }
} catch {
    Write-Error "[-] Unable to query Python version from '$PythonCmd'. Installation aborted."
    exit 1
}

# 3. Create Isolated Temp Workspace & Fetch Package Payload
$TempWorkspace = Join-Path $env:TEMP "ds-bootstrap-$([guid]::NewGuid().ToString('N'))"
$EngineDir = Join-Path $TempWorkspace "engine"
New-Item -ItemType Directory -Path $EngineDir -Force | Out-Null

$ZipUrl = "https://github.com/$RepoOwner/$RepoName/archive/refs/heads/main.zip"
$ZipPath = Join-Path $TempWorkspace "ds-installer.zip"

$PackageRoot = $null
try {
    Write-Host "[*] Downloading Digital State package payload..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri $ZipUrl -OutFile $ZipPath -UseBasicParsing -ErrorAction Stop
    Expand-Archive -Path $ZipPath -DestinationPath $TempWorkspace -Force -ErrorAction Stop

    # Extracted root is <repo>-<branch>, e.g. Digital-State-main
    $ExtractedRoot = Get-ChildItem -Path $TempWorkspace -Filter "pyproject.toml" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($ExtractedRoot) {
        $PackageRoot = $ExtractedRoot.DirectoryName
    }
} catch {
    Write-Error "[-] Failed to download or extract Digital State package payload: $_"
    if (Test-Path $TempWorkspace) { Remove-Item -Path $TempWorkspace -Recurse -Force -ErrorAction SilentlyContinue }
    exit 1
}

if (-not $PackageRoot -or -not (Test-Path (Join-Path $PackageRoot "pyproject.toml"))) {
    Write-Error "[-] Package payload is missing pyproject.toml; cannot install. Installation aborted."
    if (Test-Path $TempWorkspace) { Remove-Item -Path $TempWorkspace -Recurse -Force -ErrorAction SilentlyContinue }
    exit 1
}

# 4. Install digital_state package permanently into the resolved Python runtime.
#    Fail loudly (no discarded stderr, explicit exit-code check) so the user gets a real signal.
Write-Host "[*] Installing digital_state into $PythonCmd ..." -ForegroundColor Cyan
try {
    & $PythonCmd -m pip install --upgrade --quiet $PackageRoot
    if ($LASTEXITCODE -ne 0) { throw "pip exited with code $LASTEXITCODE" }
} catch {
    Write-Error "[-] pip install of digital_state failed: $_"
    if (Test-Path $TempWorkspace) { Remove-Item -Path $TempWorkspace -Recurse -Force -ErrorAction SilentlyContinue }
    exit 1
}

# 5. Launch Layer 2 Installer Engine Process.
#    Pass the extracted source root so Layer 2 can install into a *different* target
#    runtime (e.g. a Hermes venv) without re-discovering a bogus path.
$env:DS_PACKAGE_ROOT = $PackageRoot
$EngineScript = "import sys; from digital_state.bootstrap.engine.orchestrator import run_engine_cli; sys.exit(run_engine_cli('$Action', dry_run=$DryRunBool))"

try {
    & $PythonCmd -c $EngineScript
    $ExitCode = $LASTEXITCODE
} finally {
    if (Test-Path $TempWorkspace) {
        Remove-Item -Path $TempWorkspace -Recurse -Force -ErrorAction SilentlyContinue
    }
}

exit $ExitCode
