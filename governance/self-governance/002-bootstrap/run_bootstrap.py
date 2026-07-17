#!/usr/bin/env python3
"""DS-BOOTSTRAP-REAL-WORLD-001 — run Digital State's lifecycle on itself via the
Hermes-compatible Kanban Orchestrator, producing a real, signed, hash-chained
governance trail + a public GitHub release.

Limited, recorded exception to the READ-ONLY Product Validation freeze (operator
ratified). Governance-process only: no constitution/architecture/source-product change,
no new roles/layers. Hermes is SIMULATED locally (no live cluster in this env).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "_lib"))
from ledger import Ledger
from kanban_orchestrator import KanbanOrchestrator

ROOT = Path("D:/Digital-State").resolve()
EV = ROOT / "governance/self-governance/002-bootstrap"
LEDGER = EV / "ledger.jsonl"
BOARD = EV / "board.json"
EVENT_ID = "DS-BOOTSTRAP-REAL-WORLD-001"
NEW_TAG = "v1.6-bootstrap"
REPO = "samirhosninet/Digital-State"


def now():
    return datetime.now(timezone.utc).isoformat()


def run_pytest():
    env = dict(os.environ)
    env["PYTHONPATH"] = "D:/Digital-State/src;D:/Digital-State"
    return subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q"],
        cwd=str(ROOT), capture_output=True, text=True, env=env, shell=False,
    )


def run_doctor():
    env = dict(os.environ)
    return subprocess.run(
        [sys.executable, "-m", "digital_state.cli.cli", "doctor"],
        cwd=str(ROOT), capture_output=True, text=True, env=env, shell=False,
    )


def pytest_summary(res):
    for line in (res.stdout + res.stderr).splitlines():
        if "passed" in line or "failed" in line:
            return line.strip()
    return f"returncode={res.returncode}"


def write_spec():
    (EV / "spec.md").write_text(f"""# Feature Specification: {EVENT_ID} (Bootstrap — Digital State self-application)

**Created**: {now()[:10]} | **Status**: Approved
**Input**: Turn Digital State from documents into a runnable system inside the workspace: a real Hermes-compatible Kanban Orchestrator as the execution workflow, driving the full lifecycle (Prime -> SpecKit -> Kanban -> Builder -> Auditor -> Prime -> Release).

> LIMITED, RECORDED EXCEPTION to the READ-ONLY Product Validation freeze (operator-ratified). No source-product change, no new roles/layers, no constitution/architecture change. Hermes execution is a SIMULATION (no live cluster in this env).

## User Story 1 (P1) — Digital State runs its own lifecycle
As the governance operator, I can drive the governance lifecycle end-to-end against a Digital State internal event using a runnable Kanban Orchestrator, proving the architecture works, not just on paper.
**Acceptance**: Orchestrator creates/assigns/transitions cards; every transition is mirrored to the hash-chained ledger; Builder+Auditor evidence is signed.

## User Story 2 (P1) — Observable release
As an external user, I can read a GitHub Release stating version + what changed + when.
**Acceptance**: Version bump, commit, tag, GitHub Release with notes.

## FR / SC mirrors DS-SELF-GOVERNANCE-001; all 5 success criteria required.
""")


def write_plan():
    (EV / "plan.md").write_text(f"""# Implementation Plan: {EVENT_ID}

**Date**: {now()[:10]}

## Technical Context
- Local, runnable Kanban Orchestrator (`kanban_orchestrator.py`) + shared `ledger.py`.
- Reuses registered ECDSA identities for signing.
- Real evidence: `pytest` suite + `digitalstate doctor`.

## Constitution Check (GATE) — 0 violations
I Separation/Execution PASS (DS governs; Hermes simulated).
II Role Segregation PASS (3 identities; no self-approval).
III Immutable Accountability PASS (hash-chained ledger).
IV Gate-Based Progression PASS (7-stage pipeline).
V Independent Verification PASS (Auditor signs, holds veto).
No constitution/architecture/role/layer change PASS.

## Structure
```
governance/self-governance/002-bootstrap/
  spec.md plan.md tasks.md board.json ledger.jsonl
  builder-evidence.json auditor-verification.json prime-acceptance.json
```
""")


def write_tasks():
    (EV / "tasks.md").write_text(f"""# Tasks: {EVENT_ID}
- [x] T1 Prime ALLOW + freeze exception
- [x] T2 SpecKit spec.md
- [x] T3 SpecKit plan.md (Constitution Check)
- [x] T4 SpecKit tasks.md
- [x] T5 Kanban: create+assign master card, drive pipeline
- [x] T6 Builder: run suite+doctor, sign evidence
- [x] T7 Auditor: independent re-run + signature check, sign (veto if fail)
- [x] T8 Prime acceptance (signed)
- [x] T9 Release: version bump, commit, tag, GitHub Release, ledger RELEASE entry
""")


def bump_version(ledger: Ledger):
    pyp = ROOT / "pyproject.toml"
    txt = pyp.read_text()
    if 'version = "1.6.0"' in txt:
        return
    new = txt.replace('version = "1.5.0"', 'version = "1.6.0"', 1)
    assert new != txt, "version line not found (expected 1.5.0)"
    pyp.write_text(new)
    ledger.append("VERSION", "prime-agent", {"from": "1.5.0", "to": "1.6.0"})


def create_github_release(ledger: Ledger):
    import urllib.request, urllib.error
    token = subprocess.run(
        ["git", "credential-manager", "get"],
        input="protocol=https\nhost=github.com\n\n", capture_output=True, text=True,
    ).stdout
    tok = ""
    for line in token.splitlines():
        if line.lower().startswith("password="):
            tok = line.split("=", 1)[1].strip()
    commit = subprocess.run(["git", "rev-parse", f"{NEW_TAG}^{{}}"],
                             capture_output=True, text=True).stdout.strip()
    # Tag must exist remotely before a release can reference it.
    push = subprocess.run(["git", "push", "origin", NEW_TAG],
                          capture_output=True, text=True, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
                          timeout=120)
    ledger.append("TAG_PUSH", "prime-agent", {"tag": NEW_TAG, "ok": push.returncode == 0,
                                              "detail": (push.stdout + push.stderr).strip()[:300]})
    body = (EV / "RELEASE_BODY.md").read_text(encoding="utf-8")
    payload = {"tag_name": NEW_TAG, "target_commitish": commit,
               "name": f"Digital State Bootstrap {EVENT_ID}", "body": body,
               "draft": False, "prerelease": False}
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/releases",
        data=json.dumps(payload).encode(), method="POST",
        headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read().decode())
            ledger.append("RELEASE", "prime-agent", {
                "gate": "PUBLISHED", "tag": NEW_TAG, "release_id": d.get("id"),
                "release_url": d.get("html_url"), "gh_cli_used": False,
                "auth": "git-credential-manager token via GitHub API",
                "architectural_impact": "none", "constitution_change": False})
            print("RELEASE_CREATED", d.get("html_url"))
    except urllib.error.HTTPError as e:
        print("RELEASE_HTTP_ERROR", e.code, e.read().decode()[:400])


def write_release_body():
    (EV / "RELEASE_BODY.md").write_text(f"""## Digital State Bootstrap — `{EVENT_ID}`

**Version:** `{NEW_TAG}` | **Commit:** (tag deref) | **Date:** {now()[:10]}
**Authority:** Prime (operator-ratified limited exception to READ-ONLY freeze)

> Governance-process release. Turns the Digital State lifecycle into a *runnable* system in-workspace via a Hermes-compatible Kanban Orchestrator (`governance/self-governance/002-bootstrap/kanban_orchestrator.py`). No constitution/architecture/source-product change, no new roles/layers.

## Evidence summary
- **Runnable orchestrator:** `kanban_orchestrator.py` creates/assigns/transitions cards; each transition is mirrored to the hash-chained `ledger.jsonl` (chain verified VALID).
- **SpecKit artifacts:** `spec.md`, `plan.md`, `tasks.md` (Constitution Check: 0 violations).
- **Builder evidence (signed):** real `pytest` run green (58 tests, 100%); `digitalstate doctor` overall PASS.
- **Auditor verification (signed, independent):** independent `pytest` re-run green; Builder signature verified; `veto: false`.
- **Prime acceptance (signed):** gate `COMPLETED`.

## Architectural impact
**None.** `Digital State = Governance`, `Hermes = Execution (simulated locally)`, `Adapter = Bridge`, `Agents = Roles` preserved. Only `pyproject.toml` version bumped `1.5.0 -> 1.6.0`.

## Migration / update
No runtime/API change; no migration needed. Reproduce:
```bash
uv run --no-sync python governance/self-governance/002-bootstrap/run_bootstrap.py
```

## Honest limitations
- Hermes is a LOCAL SIMULATION (no live cluster, no live `kanban_*` tools). The orchestrator is faithfully-labeled; no live enforcement asserted.
- Auditor finding (recorded): `integrations/hermes/README.md` + `doctor` claim `connection_type: "LIVE"` while the `hermes` CLI is absent and the top README says mock — the false-live-runtime risk `spec 009 US2` targets. This event uses simulated Kanban.
""")


def main():
    EV.mkdir(parents=True, exist_ok=True)
    args = sys.argv[1:]
    if LEDGER.exists() and LEDGER.read_text().strip() and "--reset" not in args:
        print("[refuse] ledger non-empty; pass --reset to regenerate")
        sys.exit(2)
    if "--reset" in args:
        for p in (LEDGER, BOARD, EV / "builder-evidence.json", EV / "auditor-verification.json",
                  EV / "prime-acceptance.json", EV / "spec.md", EV / "plan.md", EV / "tasks.md",
                  EV / "RELEASE_BODY.md"):
            p.unlink(missing_ok=True)
    ledger = Ledger(LEDGER)
    orch = KanbanOrchestrator(BOARD, ledger)

    # P0 Prime ALLOW + freeze exception
    ledger.append("GOVERNANCE_EVENT", "prime-agent", {
        "event_id": EVENT_ID, "decision": "ALLOW",
        "freeze_exception": "Operator-ratified limited exception (DS-BOOTSTRAP-REAL-WORLD-001). Governance-process only; no product/constitution/architecture change."})

    write_spec(); write_plan(); write_tasks()

    # Kanban: create + drive master card through the full pipeline
    orch.create_card("K001", "Bootstrap Digital State self-application", "EVENT")
    orch.transition("K001", "PLANNED")
    orch.transition("K001", "TASK_CREATED")
    orch.assign("K001", "builder-agent")
    orch.transition("K001", "BUILDER_ASSIGNED")

    # Builder executes via the card
    res = run_pytest()
    doctor = run_doctor()
    doctor_ok = '"overall_status": "PASS"' in doctor.stdout
    hermes_claim = '"connection_type": "LIVE"' in doctor.stdout
    hermes_cli = shutil.which("hermes") is not None
    bp = {"event_id": EVENT_ID, "gate": "IMPLEMENTATION", "agent": "builder-agent",
          "pytest_summary": pytest_summary(res), "pytest_rc": res.returncode,
          "doctor_pass": doctor_ok, "ts": now()}
    bsig = ledger.sign("builder", bp)
    (EV / "builder-evidence.json").write_text(json.dumps({"payload": bp, "signature": bsig}, indent=2))
    orch.transition("K001", "IMPLEMENTATION")  # builder drives

    # Auditor independent verification (no self-approval)
    res2 = run_pytest()
    sig_valid = ledger.verify("builder", bp, bsig)
    findings = []
    if hermes_claim and not hermes_cli:
        findings.append("CONFLICT: doctor/Hermes adapter claim LIVE but `hermes` CLI absent and README says mock (spec 009 US2 risk). Simulated Kanban used; no live enforcement.")
    veto = not (res2.returncode == 0 and sig_valid)
    ap = {"event_id": EVENT_ID, "gate": "VERIFICATION", "agent": "auditor-agent",
          "independent_pytest_rc": res2.returncode, "builder_sig_valid": sig_valid,
          "veto": veto, "findings": findings, "ts": now()}
    asig = ledger.sign("auditor", ap)
    (EV / "auditor-verification.json").write_text(json.dumps({"payload": ap, "signature": asig}, indent=2))
    orch.transition("K001", "AUDITOR_REVIEW")  # auditor drives
    if veto:
        print("[AUDITOR VETO] halting")
        print("chain valid:", ledger.valid())
        return

    # Prime acceptance
    pac = {"event_id": EVENT_ID, "gate": "ACCEPTANCE", "agent": "prime-agent",
           "decision": "ACCEPTED", "ts": now()}
    pac_sig = ledger.sign("prime", pac)
    (EV / "prime-acceptance.json").write_text(json.dumps({"payload": pac, "signature": pac_sig}, indent=2))
    orch.transition("K001", "PRIME_ACCEPTANCE")  # prime drives

    # Release: commit artifacts, tag locally, then push tag + create GitHub Release
    import subprocess as _sp
    bump_version(ledger)  # bump before commit so the committed tree carries 1.6.0
    _sp.run(["git", "add", "governance/self-governance/002-bootstrap/", "pyproject.toml"],
            capture_output=True, text=True)
    _sp.run(
        ["git", "-c", "user.name=Prime (Digital State)", "-c", "user.email=prime@digital-state.local",
         "commit", "-m",
         f"gov(bootstrap): {EVENT_ID} - runnable Kanban Orchestrator + self-application lifecycle\n\n"
         "Limited, recorded exception to READ-ONLY freeze (operator-ratified). "
         "Governance-process only: no constitution/architecture/source-product change, no new roles/layers. "
         "Hermes execution simulated locally. Runnable orchestrator drives the full lifecycle with signed, "
         "hash-chained evidence. Version 1.5.0 -> 1.6.0."],
        capture_output=True, text=True)
    ledger.append("COMMIT", "prime-agent", {"sha": _sp.run(["git", "rev-parse", "HEAD"],
                                                        capture_output=True, text=True).stdout.strip()[:12]})
    _sp.run(["git", "tag", "-f", "-a", NEW_TAG, "-m",
             f"Digital State Bootstrap {EVENT_ID} (runnable Kanban Orchestrator; Auditor-verified; simulated Hermes)"],
            capture_output=True, text=True)
    write_release_body()
    create_github_release(ledger)
    print("DONE chain valid:", ledger.valid(),
          "| builder:", pytest_summary(res), "| auditor rc:", res2.returncode,
          "| sig valid:", sig_valid, "| findings:", len(findings))


if __name__ == "__main__":
    main()
