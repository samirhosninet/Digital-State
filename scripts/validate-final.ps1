# Digital State Final Package Validator (Windows)
# Validates the clean final package only. Does not install or modify Hermes.

$ErrorActionPreference = "Continue"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$errors = @()
$warnings = @()
$checks = 0

function Pass($msg) { Write-Host "  PASS: $msg" -ForegroundColor Green; $script:checks++ }
function Fail($msg) { Write-Host "  FAIL: $msg" -ForegroundColor Red; $script:errors += $msg; $script:checks++ }
function Warn($msg) { Write-Host "  WARN: $msg" -ForegroundColor Yellow; $script:warnings += $msg; $script:checks++ }
function ReadText($relativePath) { return Get-Content (Join-Path $root $relativePath) -Raw -Encoding UTF8 }

$distYaml = Join-Path $root 'distribution.yaml'
$distVersion = if (Test-Path $distYaml) { (Select-String 'version:\s*(.+)' $distYaml).Matches[0].Groups[1].Value.Trim() } else { 'unknown' }
Write-Host "Digital State Final Package Validator v$distVersion" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Package: $root"
Write-Host ""

# 1. Required files
Write-Host "[1/9] Required Files" -ForegroundColor Cyan
$requiredFiles = @(
    'distribution.yaml',
    'AGENTS.md',
    'README.md',
    'PACKAGE.md',
    'CHANGELOG.md',
    '.gitignore',
    'scripts\install.ps1',
    'scripts\validate-final.ps1',
    'profiles\prime\SOUL.md',
    'profiles\builder\SOUL.md',
    'profiles\auditor\SOUL.md',
    'skills\advisory-standard\SKILL.md',
    'skills\digital-state\SKILL.md',
    'skills\premortem-plus\SKILL.md'
)
foreach ($f in $requiredFiles) {
    if (Test-Path (Join-Path $root $f)) { Pass "$f exists" }
    else { Fail "$f missing" }
}

# 2. No legacy profile directories
Write-Host ""
Write-Host "[2/9] Active Profile Set" -ForegroundColor Cyan
foreach ($p in @('prime','builder','auditor')) {
    if (Test-Path (Join-Path $root "profiles\$p\SOUL.md")) { Pass "active profile $p present" }
    else { Fail "active profile $p missing" }
}
foreach ($legacy in @('analyst','researcher','coder','tester','default')) {
    if (Test-Path (Join-Path $root "profiles\$legacy")) { Fail "unexpected profile directory: $legacy" }
    else { Pass "profile directory absent: $legacy" }
}

# 3. Versions and manifest
Write-Host ""
Write-Host "[3/9] Manifest and Versions" -ForegroundColor Cyan
$distribution = ReadText 'distribution.yaml'
if ($distribution -match 'name:\s*digital-state') { Pass "distribution name is digital-state" } else { Fail "distribution name is not digital-state" }
$versionPattern = [regex]::Escape($distVersion)
if ($distribution -match "version:\s*$versionPattern") { Pass "distribution version is $distVersion" } else { Fail "distribution version is not $distVersion" }
if ($distribution -match 'skills/digital-state/' -and $distribution -match 'skills/premortem-plus/') { Pass "distribution owns both skills" } else { Fail "distribution missing skill ownership" }
if ($distribution -notmatch 'scripts/start-all-gateways\.ps1|scripts/stop-all-gateways\.ps1|scripts/gateway-status\.ps1|\n\s*-\s*SOUL\.md\s*(\r?\n|$)') {
    Pass "distribution owns only final-package runtime paths"
} else {
    Fail "distribution contains stale or ambiguous owned paths"
}
$ownedLines = @($distribution -split "`r?`n" | Where-Object { $_ -match '^\s*-\s+' } | ForEach-Object { ($_ -replace '^\s*-\s+', '').Trim() })
foreach ($owned in $ownedLines) {
    $normalized = $owned -replace '/', '\'
    $ownedPath = Join-Path $root $normalized
    if ($owned.EndsWith('/')) {
        if (Test-Path $ownedPath -PathType Container) { Pass "owned directory exists: $owned" }
        else { Fail "owned directory missing: $owned" }
    } else {
        if (Test-Path $ownedPath -PathType Leaf) { Pass "owned file exists: $owned" }
        else { Fail "owned file missing: $owned" }
    }
 }
# Prime profile version
$primeContent = ReadText "profiles\prime\SOUL.md"
if ($primeContent -match "version:\s*3\.1\.1") { Pass "prime profile version is 3.1.1" } else { Fail "prime profile version is not 3.1.1" }
# Builder profile version
$builderContent = ReadText "profiles\builder\SOUL.md"
if ($builderContent -match "version:\s*3\.1\.0") { Pass "builder profile version is 3.1.0" } else { Fail "builder profile version is not 3.1.0" }
# Auditor profile version
$auditorContent = ReadText "profiles\auditor\SOUL.md"
if ($auditorContent -match "version:\s*3\.1\.0") { Pass "auditor profile version is 3.1.0" } else { Fail "auditor profile version is not 3.1.0" }
# Digital-state skill version
$digitalStateSkill = ReadText "skills\digital-state\SKILL.md"
if ($digitalStateSkill -match "version:\s*3\.2\.0") { Pass "digital-state SKILL.md version is 3.2.0" } else { Fail "digital-state SKILL.md version is not 3.2.0" }
# Advisory-standard skill version
$advisorySkill = ReadText "skills\advisory-standard\SKILL.md"
if ($advisorySkill -match "version:\s*3\.1\.0") { Pass "advisory-standard SKILL.md version is 3.1.0" } else { Fail "advisory-standard SKILL.md version is not 3.1.0" }

 # 4. Advisory standard
Write-Host ""
Write-Host "[4/9] Advisory Standard" -ForegroundColor Cyan
foreach ($p in @('prime','builder','auditor')) {
    $content = ReadText "profiles\$p\SOUL.md"
    if (($content -match 'trusted, expert, and highly intelligent personal advisor' -and $content -match 'Confidentiality is absolute and non-negotiable') -or
        $content -match 'skills/advisory-standard/SKILL\.md') {
        Pass "$p includes Advisory Standard"
    } else {
        Fail "$p missing Advisory Standard"
    }
}

# 5. Digital State workflow essentials
Write-Host ""
Write-Host "[5/9] Workflow Essentials" -ForegroundColor Cyan
$agents = ReadText 'AGENTS.md'
$digitalStateSkill = ReadText 'skills\\digital-state\\SKILL.md'
$advisoryStandardSkill = ReadText 'skills\\advisory-standard\\SKILL.md'
$filesToCheck = @(
    @{ Name = 'AGENTS.md'; Content = $agents; Required = @('Builder produces evidence','Auditor judges evidence','Prime routes decisions','Spec-Kit') }
    @{ Name = 'skills\\digital-state\\SKILL.md'; Content = $digitalStateSkill; Required = @('Builder produces evidence','Auditor judges evidence','Prime routes decisions','kanban_create()','kanban_complete()','kanban_block()','kanban_comment()','Spec-Kit') }
    @{ Name = 'skills\\advisory-standard\\SKILL.md'; Content = $advisoryStandardSkill; Required = @() } # advisory standard skill does not require workflow essentials
)
foreach ($file in $filesToCheck) {
    $contentName = $file.Name
    $content = $file.Content
    foreach ($required in $file.Required) {
        if ($content -match [regex]::Escape($required)) { Pass "$contentName has $required" }
        else { Warn "$contentName missing $required (may not apply to this file)" }
    }
}

# 6. Premortem Plus skill essentials
Write-Host ""
Write-Host "[6/9] Premortem Plus Skill" -ForegroundColor Cyan
$premortemSkill = ReadText 'skills\premortem-plus\SKILL.md'
foreach ($required in @('Premortem Plus Risk Governance','Failure Frame','Kill Criteria','Rescue Actions','Threat Model Prompts','FMEA Hooks','Spec-Kit Integration','Kanban Integration')) {
    if ($premortemSkill -match [regex]::Escape($required)) { Pass "premortem-plus has $required" }
    else { Fail "premortem-plus missing $required" }
}

# 7. Installer tool policy
Write-Host ""
Write-Host "[7/9] Installer Tool Policy" -ForegroundColor Cyan
$installer = ReadText 'scripts\install.ps1'
foreach ($required in @('SkipToolConfiguration','toolPolicies','Test-HermesKanbanPrerequisites','Kanban + Spec-Kit are mandatory','hermes kanban --help','hermes tools list','Hermes Kanban toolset is required','hermes @args','HERMES_HOME','Get-RootModelConfig','model.provider','model.default','model.base_url','prime','builder','auditor','delegation','cronjob','kanban','terminal','code_execution')) {
    if ($installer -match [regex]::Escape($required)) { Pass "install.ps1 has tool policy marker: $required" }
    else { Fail "install.ps1 missing tool policy marker: $required" }
}

# 8. No project-specific migration state
Write-Host ""
Write-Host "[8/9] Generic Package Check" -ForegroundColor Cyan
$genericFiles = @('README.md','PACKAGE.md','AGENTS.md','profiles\prime\SOUL.md','profiles\builder\SOUL.md','profiles\auditor\SOUL.md','skills\digital-state\SKILL.md','skills\premortem-plus\SKILL.md')
foreach ($f in $genericFiles) {
    $content = ReadText $f
    if ($content -match 't_[0-9a-f]{6,}|P3-FU1|P3-T5') { Fail "$f contains project-specific migration state" }
    else { Pass "$f has no known project-specific migration state" }
    if ($content -match 'docs/|docs\\|scripts/start-all-gateways|scripts/stop-all-gateways|scripts/gateway-status|install\.sh|hermes-reference-guide|architecture-blueprint|routing-playbook|premortem-plus-report|docs/adr|docs\\adr') {
        Fail "$f references missing development-only runtime files"
    } else {
        Pass "$f has no missing development-only runtime references"
    }
}

# 9. English-only / no Arabic Unicode
Write-Host ""
Write-Host "[9/9] English-Only Content" -ForegroundColor Cyan
$textExtensions = @('.md','.yaml','.yml','.ps1','.json','.txt')
$arabicFound = $false
Get-ChildItem $root -Recurse -File | Where-Object { $textExtensions -contains $_.Extension.ToLowerInvariant() } | ForEach-Object {
    $relative = $_.FullName.Substring($root.Length + 1)
    $content = Get-Content $_.FullName -Raw -Encoding UTF8
    if ($content -match '[\u0600-\u06FF]') {
        Fail "Arabic Unicode text found in $relative"
        $script:arabicFound = $true
    }
}
if (-not $arabicFound) { Pass "No Arabic Unicode text found" }

Write-Host ""
Write-Host "Validation Summary" -ForegroundColor Cyan
Write-Host "  Checks:   $checks"
Write-Host "  Errors:   $($errors.Count)"
Write-Host "  Warnings: $($warnings.Count)"
if ($warnings.Count -gt 0) {
    Write-Host "Warnings:" -ForegroundColor Yellow
    foreach ($w in $warnings) { Write-Host "  - $w" -ForegroundColor Yellow }
}
if ($errors.Count -gt 0) {
    Write-Host "Errors:" -ForegroundColor Red
    foreach ($e in $errors) { Write-Host "  - $e" -ForegroundColor Red }
    exit 1
}
Write-Host ""
Write-Host "PASS: Digital State final package is valid." -ForegroundColor Green
exit 0
