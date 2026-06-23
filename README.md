---
version: 3.1.7
updated: 2026-06-23
compatibility: hermes-agent>=0.14.0
---
# Digital State

> **v3.1.7** — Reusable Hermes governance overlay: 3 profiles (prime/builder/auditor) with config.yaml, Kanban execution, Spec-Kit planning, Premortem Plus risk control, and risk-ledger.

Digital State installs three isolated Hermes profiles that coordinate any software project through evidence-based governance. It does not own the target project's source tree.

## Profiles

| Profile | Role |
|---|---|
| `prime` | Routes decisions, enforces gates, manages Kanban |
| `builder` | Produces raw evidence and authorized implementation |
| `auditor` | Judges evidence, validates risks, issues verdicts |

## Skills

| Skill | Purpose |
|---|---|
| `advisory-standard` | Shared ethical and behavioral contract for all agents |
| `digital-state` | Governance rules, handoff templates, tool permissions |
| `premortem-plus` | Risk governance, kill criteria, rescue actions, FMEA |

## Requirements

- Hermes Agent >= 0.14.0

## Quick Start

```powershell
.\scripts\\validate-final.ps1
.\scripts\\install-simple.ps1
```

For full install options, tool policy, verification steps, and non-conflict rules, see [`PACKAGE.md`](PACKAGE.md).

## Changelog

See [`CHANGELOG.md`](CHANGELOG.md).