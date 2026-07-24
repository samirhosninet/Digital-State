# REPOSITORY CONVENTION RULES — DIGITAL STATE CORE

**STATUS:** AUTHORITATIVE REPOSITORY SPECIFICATION  
**VERSION:** 2.0.0  
**GOVERNANCE LAYER:** Digital State Core Architecture  
**REPOSITORY:** `samirhosninet/Digital-State`  

---

## 1. Directory Structure & Layering Rules

All contributions to Digital State must adhere to standard architectural layering:

```text
Digital-State/
├── .agents/skills/              # SpecKit automated skill workflows
├── .github/workflows/          # CI/CD and release automation pipelines
├── docs/                        # Specifications, ADRs, and user guides
├── governance/                  # Policy manifests, constitutions, and ADR records
├── src/digital_state/
│   ├── cli/                     # CLI entry points, installer, and updater
│   ├── device/                  # Distributed device identity and sync engine
│   ├── core/ [FROZEN]           # Core governance engine & state machine
│   ├── hermes/ [FROZEN]         # Hermes agent plugin integration
│   ├── bootstrap/ [FROZEN]      # Runtime bootstrap installer
│   ├── sdk/ [FROZEN]            # Governance SDK bindings
│   └── observability/ [FROZEN]  # Event projection and logging
└── tests/                       # Automated unit, integration, and regression tests
```

---

## 2. Frozen Scope Protection Contract

The following paths are **FROZEN** under baseline `RUNTIME-BASELINE-003`:
- `src/digital_state/core/`
- `src/digital_state/hermes/`
- `src/digital_state/bootstrap/`
- `src/digital_state/sdk/`
- `src/digital_state/observability/`

**Invariant Rule:** No task or pull request may modify files inside frozen paths unless authorized by a formal Architecture Decision Record (ADR) and approved by Prime.

---

## 3. Commit Message & Documentation Conventions

- **Conventional Commit Format:** `type(scope): succinct description`
  - `feat(cli)`: New public CLI capabilities.
  - `docs(prime)`: Architectural specifications and operating model updates.
  - `fix(updater)`: Bug fixes in updater lifecycle.
  - `ci(release)`: Automated release pipeline adjustments.
- **Evidence Requirement:** Every release commit must generate and maintain verifiable JSON evidence reports under `.specify/`.
