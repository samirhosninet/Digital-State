# Simple Digital State Installer
# Copies profiles and skills, sets basic configuration
[CmdletBinding()]
param(
    [string]$HermesHome = "$env:LOCALAPPDATA\\hermes",
    [switch]$NoBackup
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $scriptDir
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$backupRoot = Join-Path $HermesHome "backups\\digital-state-$timestamp"

function Info($msg) { Write-Host "  INFO: $msg" -ForegroundColor Cyan }
function Pass($msg) { Write-Host "  OK:   $msg" -ForegroundColor Green }
function Warn($msg) { Write-Host "  WARN: $msg" -ForegroundColor Yellow }
function Fail($msg) { Write-Host "  FAIL: $msg" -ForegroundColor Red; throw $msg }

function Copy-WithBackup($source, $dest) {
    if (-not (Test-Path $source)) { Fail "Missing source: $source" }
    $destDir = Split-Path -Parent $dest
    New-Item -ItemType Directory -Force -Path $destDir | Out-Null

    if ((Test-Path $dest) -and (-not $NoBackup)) {
        $relative = $dest.Substring($HermesHome.Length).TrimStart('\\')
        $backupPath = Join-Path $backupRoot $relative
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $backupPath) | Out-Null
        Copy-Item $dest $backupPath -Force
        Info "Backed up $dest to $backupPath"
    }

    Copy-Item $source $dest -Force
}

# Ensure Hermes home exists
if (-not (Test-Path $HermesHome)) {
    New-Item -ItemType Directory -Force -Path $HermesHome | Out-Null
    Pass "Created Hermes home directory"
}

# Copy profiles
Write-Host "`nCopying profiles..." -ForegroundColor Cyan
$profilesSource = Join-Path $root 'profiles'
$profilesDest = Join-Path $HermesHome 'profiles'
if (Test-Path $profilesSource) {
    if (-not (Test-Path $profilesDest)) {
        New-Item -ItemType Directory -Force -Path $profilesDest | Out-Null
    }
    Get-ChildItem -Path $profilesSource -Directory | ForEach-Object {
        $profileName = $_.Name
        $sourceDir = $_.FullName
        $destDir = Join-Path $profilesDest $profileName
        Copy-WithBackup $sourceDir $destDir
        Pass "Copied profile: $profileName"
    }
} else {
    Warn "Profiles source directory not found: $profilesSource"
}

# Copy skills to each profile
Write-Host "`nCopying skills to profiles..." -ForegroundColor Cyan
$skillsSource = Join-Path $root 'skills'
if (Test-Path $skillsSource) {
    Get-ChildItem -Path $profilesDest -Directory | ForEach-Object {
        $profileName = $_.Name
        $profileSkillsDir = Join-Path $_.FullName 'skills'
        if (-not (Test-Path $profileSkillsDir)) {
            New-Item -ItemType Directory -Force -Path $profileSkillsDir | Out-Null
        }
        Get-ChildItem -Path $skillsSource -Directory | ForEach-Object {
            $skillName = $_.Name
            $sourceSkillDir = $_.FullName
            $destSkillDir = Join-Path $profileSkillsDir $skillName
            Copy-WithBackup $sourceSkillDir $destSkillDir
            Pass "Copied skill '$skillName' to profile '$profileName'"
        }
    }
} else {
    Warn "Skills source directory not found: $skillsSource"
}

# Configure each profile's config.yaml
Write-Host "`nConfiguring profiles..." -ForegroundColor Cyan
Get-ChildItem -Path $profilesDest -Directory | ForEach-Object {
    $profileName = $_.Name
    $configPath = Join-Path $_.FullName 'config.yaml'
    
    # Create a simple config.yaml with the required settings
    $configContent = @"
model:
  provider: nvidia
  name: nvidia/nemotron-3-super-120b-a12b
kanban:
  max_in_progress_per_profile: 1
toolsets:
  - kanban
  - terminal
  - file
"@
    
    Set-Content -Path $configPath -Value $configContent -Encoding UTF8
    Pass "Configured profile: $profileName"
}

Write-Host "`nInstallation complete." -ForegroundColor Green
Write-Host "Profiles copied to: $profilesDest"
Write-Host "Skills copied to each profile's skills directory"
Write-Host "Each profile configured with:"
Write-Host "  Model: nvidia/nemotron-3-super-120b-a12b"
Write-Host "  Concurrency limit: 1"
Write-Host "  Toolsets: kanban, terminal, file"
Write-Host ""
Write-Host "Recommended verification:"
Write-Host "  & hermes -p prime tools list"
Write-Host "  & hermes -p builder tools list"
Write-Host "  & hermes -p auditor tools list"
Write-Host '  & hermes -p prime chat -q "Who are you?"'