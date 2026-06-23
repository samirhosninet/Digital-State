---
version: 3.1.7
updated: 2026-06-23
compatibility: hermes-agent>=0.14.0
---
# Contributing to Digital State

Thank you for contributing to Digital State — a reusable Hermes governance overlay.

## Development Workflow

All changes follow the 3-agent Digital State governance cycle:

1. **Prime** routes the change as a Kanban card with acceptance criteria.
2. **Builder** produces evidence or implementation within authorized file boundaries.
3. **Auditor** reviews raw evidence and issues a binding verdict (APPROVE / APPROVE WITH WARNINGS / REJECT / ESCALATE).

No change to governance files, skills, profiles, or scripts is treated as complete without Auditor approval.

## Version Governance

Per Constitution Article VIII, every governance file change must:

1. Increment the `version:` field in YAML frontmatter.
2. Add a `CHANGELOG.md` entry with the version, date, and summary.
3. Pass Builder → Auditor review before being treated as in effect.

## File Boundaries

- **Reusable framework files** (`AGENTS.md`, `SOUL.md`, `skills/`, `scripts/`) must not contain project-specific content (card IDs, local paths, model choices).
- **Target-project data** belongs in `specs/`, Kanban, or the target repository.
- Keep Product requirements in `specs/spec.md`, not in framework files.

## Risk Governance

If a change introduces, modifies, or audits a risk surface:

1. Run the Premortem Plus kill-criteria check (`skills/premortem-plus/SKILL.md`).
2. Record the `Premortem Status` line on the relevant Kanban card.
3. Add or update the `risk-ledger.md` entry before proceeding.

## Concurrency

Digital State enforces `kanban.max_in_progress_per_profile: 1` (Constitution Article XIII). Only one Kanban card per profile may be `running` at a time.

## Commit Conventions

- `feat:` new feature or skill
- `fix:` bug fix or correction
- `chore:` maintenance, version bumps, documentation
- `govern:` constitutional or governance changes

## Pull Requests

- Reference the Kanban card ID in the PR description.
- Attach raw evidence (command output, log excerpts, screenshots).
- Ensure `validate-final.ps1` passes before requesting review.
