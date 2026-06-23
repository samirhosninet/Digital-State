# Digital State Final Package Installer (Windows)
# Safely installs only the prime / builder / auditor profiles and Digital State skills.
# Does not modify the Hermes default profile.
# Hermes Kanban toolset is required and hermes tools list is checked
[CmdletBinding()]
param(
    [string]$HermesHome = "$env:LOCALAPPDATA\\hermes",
    [string]$TargetWorkspace = "",
    [switch]$InstallAgentsFile,
    [switch]$NoBackup,
    [switch]$SkipToolConfiguration
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$profiles = @('prime', 'builder', 'auditor')
$skills = @('digital-state', 'premortem-plus', 'advisory-standard')
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

function Invoke-HermesConfigSet($profile, $key, $value) {
    if ([string]::IsNullOrWhiteSpace($value)) { return }
    $args = @('-p', $profile, 'config', 'set', $key, $value)
    Info "hermes $($args -join ' ')"
    & hermes @args
    if ($LASTEXITCODE -ne 0) {
        Fail "Hermes config failed for profile '$profile' key '$key'"
    }
}

function Get-RootModelConfig() {
    $configPath = Join-Path $HermesHome 'config.yaml'
    $modelConfig = @{ provider = ''; default = ''; base_url = '' }
    if (-not (Test-Path $configPath)) { return $modelConfig }
    $inModel = $false
    foreach ($line in Get-Content $configPath -Encoding UTF8) {
        if ($line -match '^model:\s*$') { $inModel = $true; continue }
        if ($inModel -and $line -match '^[^\s].*:') { break }
        if ($inModel -and $line -match '^\s+provider:\s*(.+?)\s*$') { $modelConfig.provider = $Matches[1].Trim('"', "'") }
        if ($inModel -and $line -match '^\s+default:\s*(.+?)\s*$') { $modelConfig.default = $Matches[1].Trim('"', "'") }
        if ($inModel -and $line -match '^\s+base_url:\s*(.+?)\s*$') { $modelConfig.base_url = $Matches[1].Trim('"', "'") }
    }
    return $modelConfig
}

# Ensure the top-level `toolsets:` block exists in a profile's config.yaml and
# contains `  - kanban`. We do this by direct text editing of the YAML file
# rather than via the Hermes CLI, because `kanban` is intentionally
# non-configurable through `hermes tools enable/disable` (it does not appear
# in `hermes tools list` and `hermes tools enable kanban` returns
# `Unknown toolset 'kanban'`). The `kanban` toolset must be set as a static
# top-level entry in the profile's config.yaml instead.
#
# Behavior:
#   * If the profile config directory or file is missing, create the directory
#     and write a minimal canonical block.
#   * Read the file with `Get-Content -Encoding UTF8`.
#   * Detect a TOP-LEVEL `toolsets:` key only (`^toolsets:\\s*$`). Nested
#     `toolsets:` keys (e.g. `platform_toolsets.cli`) are ignored.
#   * If `  - kanban` already appears between that key and the next
#     top-level key, report OK and make no change.
#   * If the key exists but `  - kanban` is missing, insert `  - kanban`
#     immediately before the next top-level key (or at end of file if no
#     next top-level key exists).
#   * If the key is absent, append a blank line followed by:
#         toolsets:
#           - kanban
#     at end of file.
#   * Write with `Set-Content -Encoding UTF8`.
function Ensure-KanbanInToolsets($profile) {
    $configPath = Join-Path $HermesHome "profiles\\$profile\\config.yaml"
    $configDir  = Split-Path -Parent $configPath

    # 1. Create parent directory and file if missing.
    if (-not (Test-Path $configDir)) {
        New-Item -ItemType Directory -Force -Path $configDir | Out-Null
    }
    if (-not (Test-Path $configPath)) {
        Set-Content -Path $configPath -Value "toolsets:`n  - kanban`n" -Encoding UTF8
        Pass "Created $configPath with top-level toolsets block containing - kanban"
        return
    }

    # 2. Read lines with UTF8.
    $raw = Get-Content -Path $configPath -Encoding UTF8
    if ($null -eq $raw) { $raw = @() }
    $lines = [System.Collections.Generic.List[string]]$raw

    # 3. Find the top-level `toolsets:` key (bare block form only).
    $toolsetsIdx = -1
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match '^toolsets:\\s*$') {
            $toolsetsIdx = $i
            break
        }
    }

    # Helper: returns the index of the next top-level key STRICTLY AFTER
    # $from, or $lines.Count if no such key exists. A top-level key is a
    # line that starts at column 0 and contains a colon (with optional
    # trailing value), excluding blank lines. This naturally bounds the
    # children of the `toolsets:` block.
    function Get-NextTopLevelKeyIndex($from) {
        for ($k = $from + 1; $k -lt $lines.Count; $k++) {
            $ln = $lines[$k]
            if ($ln -match '^\\s*$') { continue }          # blank line: skip
            if ($ln -match '^[A-Za-z_][A-Za-z0-9_-]*:') { return $k }
        }
        return $lines.Count
    }

    # Recovery: if a previous run inserted `  - kanban` outside the
    # `toolsets:` block (caused the file to be invalid YAML), strip those
    # orphan entries now. Only orphan lines whose value list member is
    # exactly `kanban` are removed; other orphan list items are left
    # alone to avoid silently editing user content.
    for ($j = $lines.Count - 1; $j -ge 0; $j--) {
        if ($lines[$j] -notmatch '^  - kanban\\s*$') { continue }
        # Determine whether this line is inside the `toolsets:` block.
        $inBlock = $false
        for ($b = $j - 1; $b -ge 0; $b--) {
            if ($lines[$b] -match '^toolsets:\\s*$') { $inBlock = $true; break }
            if ($lines[$b] -match '^[A-Za-z_][A-Za-z0-9_-]*:') { break }
        }
        if (-not $inBlock) { $lines.RemoveAt($j) }
    }

    # Case A: top-level `toolsets:` key is absent. Append the canonical block.
    if ($toolsetsIdx -lt 0) {
        if ($lines.Count -gt 0 -and -not [string]::IsNullOrWhiteSpace($lines[$lines.Count - 1])) {
            $lines.Add('')
        }
        $lines.Add('toolsets:')
        $lines.Add('  - kanban')
        Set-Content -Path $configPath -Value ($lines -join "`n") -Encoding UTF8
        Pass "Appended top-level 'toolsets:' block with '  - kanban' to $configPath"
        return
    }

    # Case B/C: top-level `toolsets:` key is present. Locate the next
    # top-level key so we know the end of the block.
    $nextKeyIdx = Get-NextTopLevelKeyIndex $toolsetsIdx

    # Scan list items under this key for an exact `  - kanban` entry.
    $hasKanban = $false
    for ($k = $toolsetsIdx + 1; $k -lt $nextKeyIdx; $k++) {
        if ($lines[$k] -match '^  - kanban\\s*$') {
            $hasKanban = $true
            break
        }
    }

    # Case B: already has `  - kanban` -> report OK, no change.
    if ($hasKanban) {
        Pass "toolsets already includes '  - kanban' for profile '$profile' (no change)"
        return
    }

    # Case C: present but missing `  - kanban`. Insert immediately before
    # the next top-level key (or at end of file if no next key).
    $insertAt = if ($nextKeyIdx -lt $lines.Count) { $nextKeyIdx } else { $lines.Count }
    $newLines = [System.Collections.Generic.List[string]]::new()
    for ($n = 0; $n -lt $insertAt; $n++) { $newLines.Add($lines[$n]) }
    $newLines.Add('  - kanban')
    for ($n = $insertAt; $n -lt $lines.Count; $n++) { $newLines.Add($lines[$n]) }

    Set-Content -Path $configPath -Value ($newLines -join "`n") -Encoding UTF8
    Pass "Inserted '  - kanbar' under top-level 'toolsets:' for profile '$profile'"
}

function Set-ToolsetsList($profile, $toolsets) {
    $configPath = Join-Path $HermesHome "profiles\\$profile\\config.yaml"
    $configDir  = Split-Path -Parent $configPath

    # 1. Create parent directory and file if missing.
    if (-not (Test-Path $configDir)) {
        New-Item -ItemType Directory -Force -Path $configDir | Out-Null
    }
    if (-not (Test-Path $configPath)) {
        # Create minimal file with toolsets list
        $lines = @()
        $lines.Add('toolsets:')
        foreach ($ts in $toolsets) {
            $lines.Add("  - $ts")
        }
        Set-Content -Path $configPath -Value ($lines -join "`n") -Encoding UTF8
        Pass "Created $configPath with toolsets list"
        return
    }

    # 2. Read lines with UTF8.
    $raw = Get-Content -Path $configPath -Encoding UTF8
    if ($null -eq $raw) { $raw = @() }
    $lines = [System.Collections.Generic.List[string]]$raw

    # 3. Find the top-level `toolsets:` key (bare block form only).
    $toolsetsIdx = -1
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match '^toolsets:\\s*$') {
            $toolsetsIdx = $i
            break
        }
    }

    # Helper: returns the index of the next top-level key STRICTLY AFTER
    # $from, or $lines.Count if no such key exists.
    function Get-NextTopLevelKeyIndex($from) {
        for ($k = $from + 1; $k -lt $lines.Count; $k++) {
            $ln = $lines[$k]
            if ($ln -match '^\\s*$') { continue }          # blank line: skip
            if ($ln -match '^[A-Za-z_][A-Za-z0-9_-]*:') { return $k }
        }
        return $lines.Count
    }

    # Case A: top-level `toolsets:` key is absent. Append the block.
    if ($toolsetsIdx -lt 0) {
        if ($lines.Count -gt 0 -and -not [string]::IsNullOrWhiteSpace($lines[$lines.Count - 1])) {
            $lines.Add('')
        }
        $lines.Add('toolsets:')
        foreach ($ts in $toolsets) {
            $lines.Add("  - $ts")
        }
        Set-Content -Path $configPath -Value ($lines -join "`n") -Encoding UTF8
        Pass "Appended top-level 'toolsets:' block to $configPath"
        return
    }

    # Case B: key exists. Replace the list items under this key.
    $nextKeyIdx = Get-NextTopLevelKeyIndex $toolsetsIdx

    # Build new lines: keep lines before toolsets key, then toolsets key, then new list items, then lines after next key.
    $newLines = [System.Collections.Generic.List[string]]::new()
    # Add lines from start up to and including the toolsets key line.
    for ($n = 0; $n -le $toolsetsIdx; $n++) { $newLines.Add($lines[$n]) }
    # Add the new list items.
    foreach ($ts in $toolsets) {
        $newLines.Add("  - $ts")
    }
    # Add lines from nextKeyIdx to end.
    for ($n = $nextKeyIdx; $n -lt $lines.Count; $n++) { $newLines.Add($lines[$n]) }

    Set-Content -Path $configPath -Value ($newLines -join "`n") -Encoding UTF8
    Pass "Set toolsets list for profile '$profile'"
}

function Test-HermesKanbanPrerequisites() {
    Info "Checking mandatory Hermes Kanban support"
    & hermes kanban --help *> $null
    if ($LASTEXITCODE -ne 0) {
        Fail "Hermes Kanbell CLI is required but unavailable. Update Hermes Agent or install a version that supports 'hermes kanban'."
    }
    Pass "Hermes Kanban CLI prerequisite satisfied"
}

# Ensure-DigitalStateConcurrencyCap enforces Constitution Article XIII:
# every Digital State profile (`prime`, `builder`, `auditor`) MUST be
# configured with `kanban.max_in_progress_per_profile = 1`. The function
# inspects the profile's `config.yaml`, and if the key is missing, `null`,
# or set to any value other than `1`, it inserts / corrects the key to
# `1` and writes the file back. It then RE-READS the file and runs a
# post-write verification; if the verification still fails, it exits
# the installer with a clear error message (Constitution Article XIII
# obligation: deviant installations MUST be blocked).
#
# Args:
#   $profile — one of `prime`, `builder`, `auditor`.
#
# Exits non-zero on:
#   * The file is read-only / not writable.
#   * The post-write verification cannot establish
#     `kanban.max_in_progress_per_profile: 1`.
function Ensure-DigitalStateConcurrencyCap($profile) {
    Info "Concurrency Cap Gate (Article XIII): checking kanban.max_in_progress_per_profile == 1 for profile '$profile'"
    $configPath = Join-Path $HermesHome "profiles\\$profile\\config.yaml"
    $configDir  = Split-Path -Parent $configPath

    # 1. Create parent directory and file if missing (minimal valid YAML).
    if (-not (Test-Path $configDir)) {
        New-Item -ItemType Directory -Force -Path $configDir | Out-Null
    }
    if (-not (Test-Path $configPath)) {
        $initial = @('kanban:', '  max_in_progress_per_profile: 1')
        Set-Content -Path $configPath -Value ($initial -join "`n") -Encoding UTF8
        Pass "Created $configPath with kanban.max_in_progress_per_profile: 1"
        return
    }

    # 2. Read lines with UTF8.
    $raw = Get-Content -Path $configPath -Encoding UTF8
    if ($null -eq $raw) { $raw = @() }
    $lines = [System.Collections.Generic.List[string]]$raw

    # 3. Find the TOP-LEVEL `kanban:` key (bare block form only —
    #    excludes nested keys such as `platform_toolsets.*`).
    $kanbanIdx = -1
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match '^kanban:\\s*$') {
            $kanbanIdx = $i
            break
        }
    }

    # Locate the next top-level key STRICTLY AFTER `$kanbanIdx`, or
    # $lines.Count if no such key exists. A top-level key is a line
    # that starts at column 0 and contains a colon, excluding blank
    # lines. This bounds the children of the `kanban:` block.
    $nextKeyIdx = $lines.Count
    for ($k = $kanbanIdx + 1; $k -lt $lines.Count; $k++) {
        $ln = $lines[$k]
        if ($ln -match '^\\s*$') { continue }
        if ($ln -match '^[A-Za-z_][A-Za-z0-9_-]*:') { $nextKeyIdx = $k; break }
    }

    # Case A: top-level `kanban:` key is absent. Append a new block.
    if ($kanbanIdx -lt 0) {
        if ($lines.Count -gt 0 -and -not [string]::IsNullOrWhiteSpace($lines[$lines.Count - 1])) {
            $lines.Add('')
        }
        $lines.Add('kanban:')
        $lines.Add('  max_in_progress_per_profile: 1')
        Set-Content -Path $configPath -Value ($lines -join "`n") -Encoding UTF8
        Pass "Inserted 'kanban.max_in_progress_per_profile: 1' into $configPath"
    }
    else {
        # Case B/C: `kanban:` block exists. Scan its children for the
        #            max_in_progress_per_profile key.
        $mppIdx = -1
        $mppValue = $null
        for ($k = $kanbanIdx + 1; $k -lt $nextKeyIdx; $k++) {
            if ($lines[$k] -match '^\\s+max_in_progress_per_profile:\\s*(.*?)\\s*$') {
                $mppIdx = $k
                $mppValue = $Matches[1]
                break
            }
        }

        if ($mppIdx -lt 0) {
            # Case B: key absent — insert before the next top-level key
            # (or at end of file).
            $insertAt = if ($nextKeyIdx -lt $lines.Count) { $nextKeyIdx } else { $lines.Count }
            $newLines = [System.Collections.Generic.List[string]]::new()
            for ($n = 0; $n -lt $insertAt; $n++) { $newLines.Add($lines[$n]) }
            $newLines.Add('  max_in_progress_per_profile: 1')
            for ($n = $insertAt; $n -lt $lines.Count; $n++) { $newLines.Add($lines[$n]) }
            Set-Content -Path $configPath -Value ($newLines -join "`n") -Encoding UTF8
            Pass "Inserted 'kanban.max_in_progress_per_profile: 1' under existing 'kanban:' block in $configPath"
        }
        elseif ($mppValue -ne '1') {
            # Case C: key present but not `1`. Rewrite just the value.
            $lines[$mppIdx] = '  max_in_progress_per_profile: 1'
            Set-Content -Path $configPath -Value ($lines -join "`n") -Encoding UTF8
            Pass "Corrected 'kanban.max_in_progress_per_profile' (previously '$mppValue') to 1 in $configPath"
        }
        else {
            Pass "'kanban.max_in_progress_per_profile: 1' already correct for profile '$profile' (no change)"
        }
    }

    # 4. Post-write verification (Constitution Article XIII obligation).
    $verifyRaw = Get-Content -Path $configPath -Encoding UTF8
    if ($null -eq $verifyRaw) { $verifyRaw = @() }
    $verified = $false
    foreach ($ln in $verifyRaw) {
        if ($ln -match '^\\s+max_in_progress_per_profile:\\s*1\\s*$') {
            $verified = $true
            break
        }
    }
    if (-not $verified) {
        Fail ("Concurrency Cap Gate (Article XIII) verification FAILED for profile '{0}'. " +
              "Expected literal line '  max_in_progress_per_profile: 1' within the top-level 'kanban:' block of {1}. " +
              "Native write succeeded but re-read cannot locate the line; aborting installer per Constitution Article XIII.") -f $profile, $configPath
    }
    Pass "Concurrency Cap Gate (Article XIII) verified for profile '$profile'"
}

# Kanban + Spec-Kit are mandatory Digital State layers. The `kanban` toolset must exist.
$toolPolicies = @{
    prime = @{
        enable = @('file','skills','todo','memory','session_search','clarify','delegation','cronjob','terminal')
        disable = @('web','browser','code_execution','vision','video','image_gen','video_gen','x_search','moa','tts','context_engine','homeassistant','spotify','yuanbao','computer_use')
    }
    builder = @{
        enable = @('web','browser','terminal','file','code_execution','vision','skills','session_search','clarify')
        disable = @('video','image_gen','video_gen','x_search','moa','tts','memory','context_engine','delegation','cronjob','homeassistant','spotify','yuanbao','computer_use','todo')
    }
    auditor = @{
        enable = @('web','terminal','file','code_execution','vision','skills','session_search','clarify')
        disable = @('browser','video','image_gen','video_gen','x_search','moa','tts','memory','context_engine','delegation','cronjob','homeassistant','spotify','yuanbao','computer_use','todo')
    }
}

$distYaml = Join-Path $root 'distribution.yaml'
$distVersion = 'unknown'
if (Test-Path $distYaml) {
    $match = Select-String 'version:\\s*(.+)' $distYaml
    if ($match -and $match.Matches.Count -gt 0) {
        $distVersion = $match.Matches[0].Groups[1].Value.Trim()
    }
}
Write-Host "Digital State Final Installer v$distVersion" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Package:    $root"
Write-Host "HermesHome: $HermesHome"
Write-Host ""

if (-not (Test-Path $HermesHome)) {
    New-Item -ItemType Directory -Force -Path $HermesHome | Out-Null
    Pass "Created Hermes home directory"
}

if (-not $SkipToolConfiguration) {
    if (-not (Get-Command hermes -ErrorAction SilentlyContinue)) {
        Fail "Hermes CLI not found in PATH; rerun with -SkipToolConfiguration or add hermes to PATH"
    }
    Test-HermesKanbanPrerequisites
}

# Safety: never touch default profile.
$defaultProfile = Join-Path $HermesHome 'profiles\\default\\SOUL.md'
if (Test-Path $defaultProfile) {
    Pass "default profile detected and left untouched"
} else {
    Info "default profile not present; no action needed"
}

# Copy profiles directory (entire) if it exists
Write-Host "`nCopying profiles..." -ForegroundColor Cyan
$profilesSource = Join-Path $root 'profiles'
$profilesDest = Join-Path $HermesHome 'profiles'
if (Test-Path $profilesSource) {
    if ((Test-Path $profilesDest) -and (-not $NoBackup)) {
        $backupProfiles = Join-Path $backupRoot 'profiles'
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $backupProfiles) | Out-Null
        Copy-Item $profilesDest $backupProfiles -Recurse -Force
        Info "Backed up profiles destination to $backupProfiles"
    }
    Copy-Item $profilesSource $profilesDest -Recurse -Force
    Pass "Copied profiles directory"
}
else {
    Warn "No profiles/ directory at $profilesSource -- skipping profiles copy"
}

# Copy plugins directory (entire) if it exists
Write-Host "`nCopying plugins..." -ForegroundColor Cyan
$pluginsSource = Join-Path $root 'plugins'
$pluginsDest = Join-Path $HermesHome 'plugins'
if (Test-Path $pluginsSource) {
    if ((Test-Path $pluginsDest) -and (-not $NoBackup)) {
        $backupPlugins = Join-Path $backupRoot 'plugins'
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $backupPlugins) | Out-Null
        Copy-Item $pluginsDest $backupPlugins -Recurse -Force
        Info "Backed up plugins destination to $backupPlugins"
    }
    Copy-Item $pluginsSource $pluginsDest -Recurse -Force
    Pass "Copied plugins directory"
}
else {
    Warn "No plugins/ directory at $pluginsSource -- skipping plugins copy"
}

# Configure profile model and toolsets (if not skipped)
if (-not $SkipToolConfiguration) {
    Write-Host "`nConfiguring profile model and toolsets..." -ForegroundColor Cyan
    $previousHermesHome = $env:HERMES_HOME
    $env:HERMES_HOME = $HermesHome
    try {
        $rootModel = Get-RootModelConfig
        foreach ($p in $profiles) {
            Invoke-HermesConfigSet $p 'model.provider' $rootModel.provider
            Invoke-HermesConfigSet $p 'model.default' $rootModel.default
            Invoke-HermesConfigSet $p 'model.base_url' $rootModel.base_url
            $policy = $toolPolicies[$p]
            # Set toolsets list to the enable list (we'll add kanban later)
            Set-ToolsetsList $p $policy.enable
            Ensure-KanbanInToolsets $p
            Pass "Configured model and tools for profile: $p"
        }
    } finally {
        if ($null -eq $previousHermesHome) { Remove-Item Env:HERMES_HOME -ErrorAction SilentlyContinue }
        else { $env:HERMES_HOME = $previousHermesHome }
    }
} else {
    Warn "Skipped profile-specific model and tool configuration"
}

# Install shared package metadata
Write-Host "`nInstalling shared package metadata..." -ForegroundColor Cyan
$packageDest = Join-Path $HermesHome 'distributions\\digital-state'
New-Item -ItemType Directory -Force -Path $packageDest | Out-Null
Copy-WithBackup (Join-Path $root 'distribution.yaml') (Join-Path $packageDest 'distribution.yaml')
Copy-WithBackup (Join-Path $root 'PACKAGE.md') (Join-Path $packageDest 'PACKAGE.md')
Pass "Installed distribution metadata"

# Install plugins from <DIGITAL_STATE_HOME>/plugins/ into <HERMES_HOME>/plugins/.
# (Note: we already copied the entire plugins directory above, but we also want to
#  ensure that each plugin is properly installed (this function is from the original
#  script and does per-plugin backup and copy). We'll run it as well for consistency.)
#
# Plugins live in their own per-plugin subdirectories with the mandatory
# `plugin.yaml` and `__init__.py` (Hermes v0.17.0 valid plugin shape). The
# installer copies the *entire* plugin directory verbatim so the plugin's
# auxiliary Python modules (e.g. `audit-matrix/matrix.py`, `policy.py`,
# `README.md`) are shipped alongside the manifest. We never touch the
# source tree — this is a one-way publish from digital-state to hermes.
#
# Discovery: every immediate subdirectory of <root>/plugins/ that contains
# a `plugin.yaml` is treated as a plugin. Subdirectories without a
# `plugin.yaml` are skipped (with a WARN) so the installer is robust to
# scratch folders left in the source tree.
# ---------------------------------------------------------------------------
function Install-Plugin($name, $pluginSource, $pluginsDestRoot) {
    if (-not (Test-Path $pluginSource)) {
        Warn "Plugin '$name' source directory missing: $pluginSource"
        return
    }
    $manifest = Join-Path $pluginSource 'plugin.yaml'
    if (-not (Test-Path $manifest)) {
        Warn "Plugin '$name' has no plugin.yaml at $manifest -- skipping"
        return
    }
    $dest = Join-Path $pluginsDestRoot $name
    New-Item -ItemType Directory -Force -Path $dest | Out-Null

    # Back up the entire destination plugin directory if present (one
    # backup per plugin, not per file). This mirrors the per-file backup
    # pattern elsewhere but scoped to the plugin boundary.
    if ((Test-Path $dest) -and (-not $NoBackup)) {
        $relative = $dest.Substring($HermesHome.Length).TrimStart('\\')
        $backupPath = Join-Path $backupRoot $relative
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $backupPath) | Out-Null
        Copy-Item $dest $backupPath -Recurse -Force
        Info "Backed up plugin destination $dest to $backupPath"
    }

    # Copy all files under the plugin source directory (manifest + Python
    # modules + README + auxiliary assets). Recurse so nested packages
    # like an `audit-matrix/utils/` subpackage are preserved.
    $srcItems = Get-ChildItem -Path $pluginSource -Recurse -File -ErrorAction SilentlyContinue
    if ($null -eq $srcItems) { $srcItems = @() }
    if ($srcItems.Count -eq 0) {
        Warn "Plugin '$name' source directory is empty: $pluginSource"
    }
    foreach ($item in $srcItems) {
        $relativePath = $item.FullName.Substring($pluginSource.Length).TrimStart('\\','/')
        $destPath = Join-Path $dest $relativePath
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $destPath) | Out-Null
        Copy-Item $item.FullName $destPath -Force
        Pass "Installed plugin file: $name/$relativePath"
    }
    Pass "Installed plugin: $name"
}

Write-Host "`nInstalling plugins (detailed)..." -ForegroundColor Cyan
$pluginsSourceRoot = Join-Path $root 'plugins'
$pluginsDestRoot = Join-Path $HermesHome 'plugins'
if (Test-Path $pluginsSourceRoot) {
    New-Item -ItemType Directory -Force -Path $pluginsDestRoot | Out-Null
    $pluginDirs = Get-ChildItem -Path $pluginsSourceRoot -Directory -ErrorAction SilentlyContinue
    if ($null -eq $pluginDirs) { $pluginDirs = @() }
    if ($pluginDirs.Count -eq 0) {
        Info "No plugins found under $pluginsSourceRoot -- nothing to install"
    }
    else {
        foreach ($dir in $pluginDirs) {
            Install-Plugin -name $dir.Name -pluginSource $dir.FullName -pluginsDestRoot $pluginsDestRoot
        }
    }
}
else {
    Warn "No plugins/ directory at $pluginsSourceRoot -- skipping plugin install"
}
Pass "Plugin install phase complete"

if ($InstallAgentsFile) {
    if ([string]::IsNullOrWhiteSpace($TargetWorkspace)) {
        Fail "-InstallAgentsFile requires -TargetWorkspace <path>"
    }
    if (-not (Test-Path $TargetWorkspace)) {
        Fail "Target workspace does not exist: $TargetWorkspace"
    }
    $agentsSource = Join-Path $root 'AGENTS.md'
    $agentsDest = Join-Path $TargetWorkspace 'AGENTS.md'
    if ((Test-Path $agentsDest) -and (-not $NoBackup)) {
        $workspaceBackup = Join-Path $TargetWorkspace "AGENTS.md.backup-digital-state-$timestamp"
        Copy-Item $agentsDest $workspaceBackup -Force
        Info "Backed up existing target AGENTS.md to $workspaceBackup"
    }
    Copy-Item $agentsSource $agentsDest -Force
    Pass "Installed AGENTS.md into target workspace"
} else {
    Warn "AGENTS.md was not copied to any target project. To install it later:"
    Write-Host "       .\\scripts\\install.ps1 -TargetWorkspace 'D:\\path\\to\\project' -InstallAgentsFile" -ForegroundColor Yellow
}

Write-Host "`nInstallation complete." -ForegroundColor Green
Write-Host "Installed profiles: prime, builder, auditor"
Write-Host "Installed skills:   digital-state, premortem-plus, advisory-standard"
if ($SkipToolConfiguration) {
    Write-Host "Tool policy:        skipped"
}
else {
    Write-Host "Tool policy:        configured per profile"
}
if (-not $NoBackup) { Write-Host "Backup root:        $backupRoot" }
Write-Host ""
Write-Host "Recommended verification:" -ForegroundColor Cyan
Write-Host "  hermes -p prime tools list"
Write-Host "  hermes -p builder tools list"
Write-Host "  hermes -p auditor tools list"
Write-Host '  hermes -p prime chat -q "Who are you?"'
Write-Host '  hermes -p builder chat -q "Who are you?"'
Write-Host '  hermes -p auditor chat -q "Who are you?"'