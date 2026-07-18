# Independent Installation Validation

**Status:** DESIGN PHASE — no external validation performed  
**Date:** 2026-07-17  
**Authority:** PRIME (Governance)  
**Phase:** Product Validation

---

## Purpose

Validate that a **completely independent user** (not the repository owner, not a
collaborator, no prior knowledge) can:

1. Install Digital State from the public GitHub repository
2. Initialize a workspace
3. Run the diagnostics (`doctor`)
4. Execute a complete governance workflow (register → submit → approve)
5. Understand what happened without documentation hand-holding

---

## Installation Paths Documented (README)

### Path A: Primary User Installation (GitHub Remote Package)

```bash
pip install git+https://github.com/samirhosninet/Digital-State.git
digitalstate init
digitalstate doctor
```

**Expected duration:** 2–5 minutes  
**Prerequisites:** Python ≥ 3.11, pip, internet access  
**Target audience:** End users consuming as a dependency

### Path B: Developer Repository Installation (Local Clone)

```bash
git clone https://github.com/samirhosninet/Digital-State.git
cd Digital-State
# Windows:
powershell -ExecutionPolicy Bypass -File install.ps1
# Linux/macOS:
chmod +x install.sh && ./install.sh
.venv/Scripts/digitalstate doctor   # or ./.venv/bin/digitalstate doctor
```

**Expected duration:** 3–10 minutes  
**Prerequisites:** Git, Python ≥ 3.11, PowerShell/Bash  
**Target audience:** Developers modifying the codebase

---

## What the Installer Does (install.ps1 / install.sh)

| Step | Action | Validation |
|------|--------|------------|
| 1 | Check Python ≥ 3.11 | `python --version` |
| 2 | Create virtualenv | `python -m venv .venv` |
| 3 | Upgrade pip/setuptools/wheel | `pip install -U pip setuptools wheel` |
| 4 | Install package in editable mode | `pip install -e .` |
| 5 | Bootstrap workspace | `digitalstate init` |
| 6 | Verify installation | `digitalstate doctor` |

---

## What `digitalstate init` Creates

```
project-root/
└── .specify/
    ├── integration.json          # Hermes integration marker
    ├── init-options.json         # Initialization options
    ├── state.json                # Feature lifecycle states
    ├── agents.json               # Legacy workspace registry (migrated)
    ├── memory/
    │   ├── audit_log.jsonl       # Hash-chained audit trail
    │   └── constitution.md       # Governance constitution
    └── governance.lock/          # Concurrency lock directory
```

---

## What `digitalstate doctor` Checks

| Check | Pass Criteria |
|-------|---------------|
| **Installation** | `cryptography` import succeeds, version ≥ 41.0.0 |
| **Configuration** | All `.specify/` files exist and are readable |
| **Governance** | `state.json` parses as valid JSON |
| **Hermes Integration** | Mock adapter self-test passes; connection type = "MOCK" |

---

## Known Installation Risks (Hypotheses)

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Windows PATH issues (uv/pip not on PATH) | Medium | High | Document `python -m pip` usage |
| Python version mismatch (< 3.11) | Low | High | Explicit check in installer |
| GitHub rate limiting on `pip install git+https` | Low | Medium | Recommend local clone for CI |
| Hermes not installed (mock adapter warning) | High | Low | Expected — warning is informational |
| Permission errors writing to `.specify/` | Low | Medium | Run in user-owned directory |
| Virtualenv activation confusion | Medium | Medium | Clear docs on `.venv/Scripts/activate` |

---

## Validation Protocol for External User

### Recruitment Criteria
- [ ] Not the repository owner
- [ ] Has not seen the codebase before
- [ ] Has Python development experience
- [ ] Uses or wants to use AI coding agents
- [ ] Runs Windows, macOS, or Linux

### Test Script (to give the user)

```
TASK: Install Digital State and run a governance workflow

1. Choose Path A or Path B from README
2. Run the commands exactly as written
3. Record: time taken, errors, confusion points
4. Run: digitalstate doctor
5. Run: digitalstate register --id test-user --role Prime --public-key-file <provided> --key-id test-key
6. Run: digitalstate submit --feature test-001 --gate SPECIFICATION --evidence '{"spec_file":"test.md","requirements_count":3,"signature":"..."}' --agent test-user
7. Report: What happened? What was unclear? What failed?
```

### Success Metrics

| Metric | Target |
|--------|--------|
| Path A install success rate | ≥ 80% |
| Path B install success rate | ≥ 90% |
| Time to `doctor` PASS | < 5 minutes |
| Time to first `submit` + `approve` | < 10 minutes |
| User can explain what the audit log contains | Yes |
| Zero "I don't know what to do next" moments | Target: 0 |

---

## Current Validation Status

| Validation | Status | Evidence |
|------------|--------|----------|
| Path A documented | ✅ | README.md lines 47–78 |
| Path B documented | ✅ | README.md lines 82–119 |
| Installer scripts exist | ✅ | `install.ps1`, `install.sh` |
| `init` command works | ✅ | Proxy: clean temp workspace, returns Success |
| `doctor` command works | ✅ | Proxy: PASS (LIVE when Hermes present, MOCK when absent) |
| `register` works (distinct id) | ✅ | Proxy: writes to workspace registry |
| `submit` works (signed) | ✅ | Proxy: state→SPECIFICATION |
| `digitalstate approve SPECIFICATION` (auditor) | ❌→✅ BUG-VAL-001 FIXED: permissions now resolve |
| Full lifecycle to COMPLETED | ❌→✅ FIXED (5 transitions, see REMEDIATION-EVIDENCE.md) |
| External user tested Path A | ❌ | **NOT DONE — required for exit (human gate)** |
| External user tested Path B | ❌ | **NOT DONE — required for exit (human gate)** |
| External user completed workflow | ❌→✅ TECHNICAL PROXY | **Code path verified; human gate still open** |
| Windows user tested | ✅ (proxy, this remediation) | Technical proxy on Windows host |
| Linux user tested | ❌ | **NOT DONE — required for exit (human gate)** |
| macOS user tested | ❌ | **NOT DONE — required for exit (human gate)** |

---

## Proxy Install Findings (Technical, NOT human-substitute)

A technical proxy install was executed in a clean temp workspace using the
actual CLI (`init` → `register` → `submit` → `approve`). It surfaced **two
real defects** that would block 100% of independent users:

1. **BUG-VAL-001 (CRITICAL):** Runtime-seeded agents resolve to `permissions=[]`
   because `get_agent()` passes a capitalized role (`"Auditor"`) to
   `_permissions_for_role()`, but `roles.json` keys are lowercase. Result: no
   agent can ever approve/veto/verify. Full detail + proposed fix in
   `VALIDATION-BUG-LOG.md`.

2. **BUG-VAL-002 (MEDIUM):** `init` pre-seeds `prime-agent`/`builder-agent`/
   `auditor-agent` (public-key only, no private key). A user who then runs
   `register` with those IDs is rejected ("already registered") yet cannot sign
   as the seeded identity (no private key). Workaround: register under new IDs,
   but that still hits BUG-VAL-001.

**These bugs prove the value of the Product Validation phase:** docs look
complete, 47 tests pass, but a real install path is broken at the first
approval gate. The repo is READ-ONLY per directive — fixes are documented and
verified, but NOT applied. They become the first action when the phase unlocks.

See `VALIDATION-BUG-LOG.md` for full reproduction and verified fix.

---

## Next Actions Required

1. **Recruit 2–3 external testers** matching criteria
2. **Provide test keys** (pre-generated ECDSA P-256 key pairs)
3. **Run validation sessions** (screen share or async with screen recording)
4. **Document results** in this file (update status table)
5. **Fix installation blockers** found during validation
6. **Re-test** after fixes

**Blocker for Product Validation exit:** At least 1 external user must successfully
complete the full workflow on a fresh machine without assistance.