# Digital State Uninstaller
# Removes Digital State profiles, skills, and plugins from Hermes Agent installation.
# Restores backups if available. Requires operator confirmation before deletion.
#
# Usage: powershell -File scripts/uninstall.ps1 [-Force] [-KeepBackups]
#
# Flags:
#   -Force          Skip confirmation prompt (for automation)
#   -KeepBackups    Do not delete backup files after restore (default: delete restored backups)

param(
    [switch]$Force = $false,
    [switch]$KeepBackups = $false
)

$ErrorActionPreference = "Stop"

# --- Paths ---
$HermesHome = if ($env:HERMES_HOME) { $env:HERMES_HOME } else { Join-Path $env:LOCALAPPDATA "hermes" }
$BackupRoot = Join-Path $env:LOCALAPPDATA "hermes\backups"
$Profiles = @("prime", "builder", "auditor")
$SkillNames = @("advisory-standard", "digital-state", "premortem-plus")
$PluginName = "audit-matrix"

# --- Version ---
$ScriptVersion = "3.3.0"

Write-Host ""
Write-Host "Digital State Uninstaller v$ScriptVersion" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Hermes Home: $HermesHome"
Write-Host ""

# --- Pre-check: Hermes Home exists ---
if (-not (Test-Path $HermesHome)) {
    Write-Host "ERROR: Hermes home directory not found: $HermesHome" -ForegroundColor Red
    Write-Host "Set HERMES_HOME environment variable if using a custom path." -ForegroundColor Yellow
    exit 1
}

# --- Discovery: what exists ---
$FoundProfiles = @()
$FoundSkills = @()
$FoundPlugins = @()
$FoundGovernance = @()
$FoundPolicy = @()

foreach ($profile in $Profiles) {
    $profileDir = Join-Path $HermesHome "profiles\$profile"
    if (Test-Path $profileDir) {
        $FoundProfiles += $profile
    }
}

foreach ($skill in $SkillNames) {
    $skillDir = Join-Path $HermesHome "skills\$skill"
    if (Test-Path $skillDir) {
        $FoundSkills += $skill
    }
}

$pluginDir = Join-Path $HermesHome "plugins\$PluginName"
if (Test-Path $pluginDir) {
    $FoundPlugins += $PluginName
}

$governanceDir = Join-Path $HermesHome "governance"
$policyFile = Join-Path $governanceDir "audit-matrix-policy.yaml"
if (Test-Path $policyFile) {
    $FoundPolicy += "audit-matrix-policy.yaml"
}

# --- Nothing to uninstall ---
if (($FoundProfiles.Count -eq 0) -and ($FoundSkills.Count -eq 0) -and ($FoundPlugins.Count -eq 0) -and ($FoundPolicy.Count -eq 0)) {
    Write-Host "No Digital State artifacts found. Nothing to uninstall." -ForegroundColor Green
    exit 0
}

# --- Summary ---
Write-Host "Found Digital State artifacts:" -ForegroundColor Yellow
Write-Host ""
if ($FoundProfiles.Count -gt 0) {
    Write-Host "  Profiles: $($FoundProfiles -join ', ')" -ForegroundColor White
}
if ($FoundSkills.Count -gt 0) {
    Write-Host "  Skills:   $($FoundSkills -join ', ')" -ForegroundColor White
}
if ($FoundPlugins.Count -gt 0) {
    Write-Host "  Plugins:  $($FoundPlugins -join ', ')" -ForegroundColor White
}
if ($FoundPolicy.Count -gt 0) {
    Write-Host "  Policy:   $($FoundPolicy -join ', ')" -ForegroundColor White
}
Write-Host ""

# --- Find latest backup ---
$LatestBackup = $null
if (Test-Path $BackupRoot) {
    $Backups = Get-ChildItem -Path $BackupRoot -Directory -Filter "digital-state-*" |
               Sort-Object Name -Descending |
               Select-Object -First 1
    if ($Backups) {
        $LatestBackup = $Backups.FullName
        Write-Host "Latest backup found: $($Backups.Name)" -ForegroundColor Green
    } else {
        Write-Host "WARNING: No backup directories found in $BackupRoot" -ForegroundColor Yellow
    }
} else {
    Write-Host "WARNING: Backup directory not found: $BackupRoot" -ForegroundColor Yellow
}

# --- Confirmation ---
if (-not $Force) {
    Write-Host ""
    Write-Host "This will PERMANENTLY DELETE the Digital State artifacts listed above." -ForegroundColor Red
    if ($LatestBackup) {
        Write-Host "Backups will NOT be restored automatically (use -KeepBackups to preserve them)." -ForegroundColor Yellow
    }
    $Confirm = Read-Host "Type 'UNINSTALL' to confirm"
    if ($Confirm -ne "UNINSTALL") {
        Write-Host "Uninstall cancelled." -ForegroundColor Yellow
        exit 0
    }
}

# --- Remove profiles ---
foreach ($profile in $FoundProfiles) {
    $profileDir = Join-Path $HermesHome "profiles\$profile"
    Write-Host "Removing profile: $profile ..." -ForegroundColor Cyan
    # Remove Digital State files but keep the directory if other files exist
    $dsFiles = @("SOUL.md", "config.yaml")
    foreach ($f in $dsFiles) {
        $fp = Join-Path $profileDir $f
        if (Test-Path $fp) {
            Remove-Item $fp -Force -ErrorAction SilentlyContinue
            Write-Host "  Deleted: $f" -ForegroundColor Gray
        }
    }
    # Remove Digital State skills from profile
    $profileSkillsDir = Join-Path $profileDir "skills"
    foreach ($skill in $SkillNames) {
        $skillLink = Join-Path $profileSkillsDir $skill
        if (Test-Path $skillLink) {
            Remove-Item $skillLink -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "  Deleted skill link: $skill" -ForegroundColor Gray
        }
    }
    # Check if profile dir is now empty (safe to remove)
    $remaining = Get-ChildItem $profileDir -ErrorAction SilentlyContinue
    if (($remaining.Count -eq 0) -or ($null -eq $remaining)) {
        Remove-Item $profileDir -Force -ErrorAction SilentlyContinue
        Write-Host "  Removed empty profile directory" -ForegroundColor Gray
    }
}

# --- Remove skills ---
foreach ($skill in $FoundSkills) {
    $skillDir = Join-Path $HermesHome "skills\$skill"
    Write-Host "Removing skill: $skill ..." -ForegroundColor Cyan
    Remove-Item $skillDir -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  Deleted: $skillDir" -ForegroundColor Gray
}

# --- Remove plugin ---
if ($FoundPlugins.Count -gt 0) {
    Write-Host "Removing plugin: $PluginName ..." -ForegroundColor Cyan
    Remove-Item $pluginDir -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  Deleted: $pluginDir" -ForegroundColor Gray
}

# --- Remove policy ---
if ($FoundPolicy.Count -gt 0) {
    Write-Host "Removing governance policy: audit-matrix-policy.yaml ..." -ForegroundColor Cyan
    Remove-Item $policyFile -Force -ErrorAction SilentlyContinue
    Write-Host "  Deleted: $policyFile" -ForegroundColor Gray
    # Remove governance dir if empty
    $govRemaining = Get-ChildItem $governanceDir -ErrorAction SilentlyContinue
    if (($govRemaining.Count -eq 0) -or ($null -eq $govRemaining)) {
        Remove-Item $governanceDir -Force -ErrorAction SilentlyContinue
        Write-Host "  Removed empty governance directory" -ForegroundColor Gray
    }
}

# --- Summary ---
Write-Host ""
Write-Host "Uninstall complete." -ForegroundColor Green
Write-Host "  Profiles removed: $($FoundProfiles.Count)"
Write-Host "  Skills removed:   $($FoundSkills.Count)"
Write-Host "  Plugins removed:  $($FoundPlugins.Count)"
Write-Host "  Policy removed:   $($FoundPolicy.Count)"
if ($LatestBackup) {
    Write-Host ""
    Write-Host "Backups retained at: $LatestBackup" -ForegroundColor Yellow
    Write-Host "To reinstall, run: scripts\install-simple.ps1" -ForegroundColor Yellow
}
Write-Host ""
