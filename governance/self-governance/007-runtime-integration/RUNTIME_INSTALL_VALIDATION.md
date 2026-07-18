# DS-RUNTIME-INSTALL-VALIDATION-001 — Local Runtime Update & Version-Match Evidence

**Authority:** Human Prime (Final Authority), operator-ratified validation exception.
**Date:** 2026-07-18 · **Repo:** `samirhosninet/Digital-State`

## Execution order (as required by card)

### 1. Verify current Git status
- Branch: `spec-12/authority-remediation`
- HEAD: `b8df97518d38267d2866fd046bc7d904d126eb30`
- Working tree: clean except 3 untracked local dirs **not part of the runtime**:
  `.audit-clean/`, `.audit-venv/`, `.venv-install/` (audit/venv scratch — gitignored noise).
- Upstream: `origin/spec-012/authority-remediation` = `b8df975` (matches HEAD).

### 2. Pull latest changes if needed
- `git fetch origin` → no new objects.
- `git pull --ff-only` → **"Already up to date."** (rc=0).
- Remote `origin/main` = `81d098b`; the merge of this branch into `main` already carries `b8df975`.
- **No pull performed** — local already equals latest repository version.

### 3. Rebuild/reinstall runtime from repository
- `uv sync` → resolved 11 packages, rc=0 (editable install of `src/digital_state`,
  `framework`, `integrations` from the repo tree).
- Package name: `digital-state` (editable, runs via `uv run python <path>`, not a console script).
- `py_compile governance/self-governance/runtime.py` → OK.

### 4. Verify installed runtime uses the rebuilt (HEAD) version
| Probe | Result |
|---|---|
| `digital_state` importable from `src/` | ✅ `src/digital_state/__init__.py` |
| `runtime.py` resolves `ROOT` path-relative | ✅ `ROOT = D:/Digital-State` (repo tree, not a vendored copy) |
| `runtime.py` `TEMPLATES` (`.specify/templates`) present | ✅ |
| Runtime `--reset` + run executes | ✅ `HAPPY_PATH_OK states=11 | ILLEGAL_TRANSITIONS_DENIED=9 | chain_valid=True` |
| Runtime event recorded in ledger | ✅ `GOVERNANCE_EVENT` → `DS-RUNTIME-WORKFLOW-INTEGRATION-001`, 21 entries |
| `pyproject.toml` version = runtime `NEW_VER` | ✅ both `1.9.0` |

**Match proof:** the installed runtime is executed *from the repository working tree*
(`ROOT` is path-relative to `D:/Digital-State`, editable `src/`), and HEAD = `b8df975` is the
only checked-out commit. Therefore the running runtime **is** the repository HEAD version.
No forked/vendored copy exists.

### 5. Evidence only — no Builder task
This card is validation-only. Produced evidence above; **no Builder task created** (per card).

## Deliverables
- **Current commit SHA:** `b8df97518d38267d2866fd046bc7d904d126eb30`
- **Installed runtime version:** `1.9.0` (pyproject + runtime `NEW_VER`)
- **Runtime matches repo HEAD:** ✅ YES (path-relative execution from `D:/Digital-State`, editable `src/`, single HEAD commit)
- **Blockers:** NONE. (Local untracked `.audit-*/` dirs are non-runtime scratch and do not affect the runtime.)

## Constitutional status
Validation only — no new Roles/Layers, no constitution/architecture/`src` change, Human Final
Authority preserved. Digital State = Governance Plane; Hermes = simulated Execution Kernel.
