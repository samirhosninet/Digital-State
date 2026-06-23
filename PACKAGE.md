---
version: 3.1.0
updated: 2026-06-20
compatibility: hermes-agent>=0.14.0
---
# Digital State Final Runtime Package

> **v3.1.0**

This folder contains the final runtime files for Digital State.

Digital State is a reusable, project-agnostic Hermes governance overlay for any software project.

## Core Rule

This is the clean final package. Development-only files such as ADRs, old legacy SOUL files, IDE files, and historical reports are intentionally excluded. The only scripts included are the final safe installer and final validator.

## Contents

```text
final/digital-state/
├── .gitignore
├── CHANGELOG.md
├── distribution.yaml
├── AGENTS.md
├── README.md
├── scripts/
│   ├── install.ps1
│   └── validate-final.ps1
├── profiles/
│   ├── prime/SOUL.md
│   ├── builder/SOUL.md
│   └── auditor/SOUL.md
└── skills/
    ├── advisory-standard/SKILL.md
    ├── digital-state/SKILL.md
    └── premortem-plus/SKILL.md
```

## Active Profiles

| Profile | Purpose |
|---|---|
| `prime` | Kanban orchestrator. Routes decisions and enforces gates. |
| `builder` | Evidence and authorized implementation operator. |
| `auditor` | Review, verification, risk, and evidence authority. |

## Skills

| Skill | Purpose |
|---|---|
| `advisory-standard` | Shared ethical and behavioral contract for all agents. |
| `digital-state` | Governance, handoff, Kanban, and workflow rules. |
| `premortem-plus` | Risk governance, failure scenarios, kill criteria, rescue actions, threat modeling, and FMEA hooks. |

## Operating Model

```text
Spec-Kit requirements and planning
  -> Prime creates Kanban parent/child cards
  -> Builder produces raw evidence or authorized implementation
  -> Auditor judges evidence and risk
  -> Prime records the final decision
```

## Non-Conflict Rules

- Do not modify the Hermes `default` profile.
- Install only `prime`, `builder`, and `auditor` profiles.
- Copy or merge `AGENTS.md` into a target workspace only after backing up any existing `AGENTS.md`.
- Keep target-project requirements in the target project's `specs/` directory.
- Keep execution state in Hermes Kanban.
- Keep file boundaries on Kanban cards, not in global profile files.
- Digital State agents are profile-isolated. Do not replace the `builder` or `auditor` profiles with generic subagents.
- Generic delegation is not valid Builder evidence or Auditor approval for governed work unless explicitly outside Digital State governance and labeled unofficial.

## Safe Install

Validate first:

```powershell
.\scripts\validate-final.ps1
```

Install only after validation passes:

```powershell
.\scripts\install.ps1
```

The installer copies the root Hermes model settings into `prime`, `builder`, and `auditor`, then configures Hermes toolsets per profile:

```text
prime   = file, skills, todo, memory, session_search, clarify, delegation, cronjob, kanban, terminal
builder = web, browser, terminal, file, code_execution, vision, skills, session_search, clarify, kanban
auditor = web, terminal, file, code_execution, vision, skills, session_search, clarify, kanban
```

Mandatory layers: Kanban and Spec-Kit are required for Digital State. The installer verifies `hermes kanban` and the Hermes `kanban` toolset before configuring profiles. If either is missing, update Hermes Agent before installing. Prime terminal access is limited to Kanban CLI/live-board reads, Kanban routing commands, and routing diagnostics only; implementation remains forbidden by the Prime SOUL.

To install files but skip tool changes:

```powershell
.\scripts\install.ps1 -SkipToolConfiguration
```

Optional target workspace AGENTS.md install:

```powershell
.\scripts\install.ps1 -TargetWorkspace "D:\path\to\project" -InstallAgentsFile
```

## Automatic Tool Policy

The installer (`.\scripts\install.ps1`) reads the Hermes root `config.yaml` model settings and applies them to each profile, then enables or disables toolsets according to the per-profile policy above. Use `-SkipToolConfiguration` to install files without changing toolsets.

## Verification

After installation, verify:

```powershell
hermes -p prime tools list
hermes -p builder tools list
hermes -p auditor tools list
hermes -p prime chat -q "Who are you?"
hermes -p builder chat -q "Who are you?"
hermes -p auditor chat -q "Who are you?"
```

## Changelog

See CHANGELOG.md for full history.

- **v3.1.0** (2026-06-20) — Scripts moved to `scripts/`, added advisory-standard skill, DRY version from distribution.yaml, added CHANGELOG.md and .gitignore.
