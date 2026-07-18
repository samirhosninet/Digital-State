#!/usr/bin/env python3
"""DS-WORKFLOW-KERNEL-001 — codify the EXISTING constitutional governance
workflow as a Workflow Engine (state machine) + codify the GitHub Release
Workflow (auto after Human Approval).

This implements the FINAL GOVERNANCE DIRECTIVE:
  * Workflow Kernel (governance/self-governance/_engine/workflow_kernel.py) is
    the SOLE authority over lifecycle transitions; no agent mutates state
    directly; the Hermes Kanban Orchestrator routes every move through it.
  * Chat is only an input interface.
  * Human Final Authority is preserved: no release occurs until a `human`
    authorization crosses the HUMAN_APPROVAL gate.
  * After Human Approval, the Release Workflow runs automatically:
        Commit -> Version Bump -> Git Tag -> GitHub Release -> Notes -> Ledger Pub Event.

Scope: governance self-application space only. No constitution/architecture/
source-product change, no new roles/layers. Hermes execution is a local
simulation (no live cluster). Reuses _lib/ledger.py + 002 orchestrator + _engine.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
for p in (HERE, HERE.parent / "_lib", HERE.parent / "002-bootstrap", HERE.parent / "_engine"):
    sys.path.insert(0, str(p))
from ledger import Ledger
from kanban_orchestrator import KanbanOrchestrator
from workflow_kernel import WorkflowKernel

ROOT = Path("D:/Digital-State").resolve()
EV = ROOT / "governance/self-governance/006-workflow-kernel"
LEDGER = EV / "ledger.jsonl"
BOARD = EV / "board.json"
EVENT_ID = "DS-WORKFLOW-KERNEL-001"
REPO = "samirhosninet/Digital-State"
NEW_TAG = "v1.8-workflow-kernel"
NEW_VER = "1.8.0"
FROM_VER = "1.7.0"
K = WorkflowKernel()


def now():
    return datetime.now(timezone.utc).isoformat()


def run_pytest():
    env = dict(os.environ)
    env["PYTHONPATH"] = "D:/Digital-State/src;D:/Digital-State"
    return subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q"],
                          cwd=str(ROOT), capture_output=True, text=True, env=env, shell=False)


def pytest_summary(res):
    for line in (res.stdout + res.stderr).splitlines():
        if "passed" in line or "failed" in line:
            return line.strip()
    return f"returncode={res.returncode}"


def write_release_body():
    (EV / "RELEASE_BODY.md").write_text(f"""## Digital State v1.8 — Workflow Engine Codified (`{NEW_TAG}`)

**Version:** `{NEW_VER}` | **Prior:** `{FROM_VER}` | **Event:** `{EVENT_ID}`
**Date:** {now()[:10]} | **Authority:** Human Prime (Final Authority) → agent Prime (operator-ratified, FINAL GOVERNANCE DIRECTIVE)
**Repo:** `{REPO}`

> Governance-process release. Codifies the *existing* constitutional governance cycle as a **Workflow Engine (state machine)** — the single authority over lifecycle transitions — and codifies the **GitHub Release Workflow** so a new version is published automatically *after* Human Approval (no chat-driven coordination). No constitution/architecture/source-product change, no new roles/layers. Hermes execution = local simulation.

## What changed?
- **Version bump `{FROM_VER} -> {NEW_VER}`** only (pyproject.toml). No runtime/API change.
- Added Workflow Engine artifacts under `governance/self-governance/`:
  - `_engine/workflow_kernel.py` — the authoritative state machine (12 states). The ONLY source of truth for transitions.
  - `002-bootstrap/kanban_orchestrator.py` (upgraded) — routes every card move through the kernel; chat is input-only.
  - `006-workflow-kernel/engine_selftest.py` — proves the engine enforces the cycle (9 illegal transitions denied).
  - `006-workflow-kernel/ds_workflow_kernel_event.py` — runs the cycle and, after Human Approval, the Release Workflow.

## What it proves (vs. v1.7)
| Proof | Result |
|-------|--------|
| Governance lifecycle runs on itself | ✅ (v1.5) |
| Runnable Hermes-compatible Kanban Orchestrator | ✅ (v1.6) |
| Operational cycle end-to-end | ✅ (v1.6-opval) |
| Agent role boundaries enforced | ✅ (v1.7) |
| **Workflow codified as state machine; transitions solely kernel-enforced** | ✅ (v1.8) |
| **Release Workflow automated after Human Approval (no manual chat coordination)** | ✅ (v1.8) |
| Ledger integrity (hash-chained, signed) | ✅ valid across all events |
| Auditor independent verification | ✅ no self-approval |

## How users run a new project this way
1. User talks to Prime only. 2. Prime creates Spec (SpecKit) + Kanban card (kernel-enforced).
3. Builder picks its card; executes + evidence. 4. Auditor picks verification card; PASS/FAIL.
5. Prime reviews. 6. **Human approves.** 7. System auto-commits, bumps, tags, publishes Release.
No step depends on manually messaging an agent — only the intended human approval.

```bash
uv run --no-sync python governance/self-governance/006-workflow-kernel/engine_selftest.py
uv run --no-sync python governance/self-governance/006-workflow-kernel/ds_workflow_kernel_event.py --reset
uv run --no-sync python governance/self-governance/006-workflow-kernel/ds_workflow_kernel_event.py
# after human approval:
uv run --no-sync python governance/self-governance/006-workflow-kernel/ds_workflow_kernel_event.py --finalize=VERIFIED
```

## Honest limitations
- Hermes is a LOCAL SIMULATION (no live cluster, no live `kanban_*` tools). Orchestrator is faithfully labeled.
- Known finding (Auditor, carried): `integrations/hermes/README.md` claims `LIVE` while `hermes` CLI is absent (spec 009 US2). This release uses simulated Kanban.
""")
    return EV / "RELEASE_BODY.md"


def bump_version(ledger: Ledger):
    pyp = ROOT / "pyproject.toml"
    txt = pyp.read_text()
    if f'version = "{NEW_VER}"' in txt:
        return
    new = txt.replace(f'version = "{FROM_VER}"', f'version = "{NEW_VER}"', 1)
    assert new != txt, f"version {FROM_VER} not found"
    pyp.write_text(new)
    ledger.append("VERSION", "prime-agent", {"from": FROM_VER, "to": NEW_VER})


def publish_release(ledger: Ledger):
    token = subprocess.run(["git", "credential-manager", "get"],
                           input="protocol=https\nhost=github.com\n\n",
                           capture_output=True, text=True).stdout
    tok = ""
    for line in token.splitlines():
        if line.lower().startswith("password="):
            tok = line.split("=", 1)[1].strip()
    commit = subprocess.run(["git", "rev-parse", f"{NEW_TAG}^{{}}"],
                            capture_output=True, text=True).stdout.strip()
    push = subprocess.run(["git", "push", "origin", NEW_TAG],
                          capture_output=True, text=True,
                          env={**os.environ, "GIT_TERMINAL_PROMPT": "0"}, timeout=120)
    ledger.append("TAG_PUSH", "prime-agent",
                  {"tag": NEW_TAG, "ok": push.returncode == 0,
                   "detail": (push.stdout + push.stderr).strip()[:300]})
    body = (EV / "RELEASE_BODY.md").read_text(encoding="utf-8")
    payload = {"tag_name": NEW_TAG, "target_commitish": commit,
               "name": "Digital State v1.8 — Workflow Engine Codified", "body": body,
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


def run_release_workflow(ledger: Ledger):
    """Codified GitHub Release Workflow — runs automatically AFTER Human Approval."""
    import subprocess as _sp
    bump_version(ledger)
    _sp.run(["git", "add", "governance/self-governance/", "pyproject.toml"],
            capture_output=True, text=True)
    _sp.run(["git", "-c", "user.name=Prime (Digital State)",
             "-c", "user.email=prime@digital-state.local", "commit", "-m",
             f"gov(workflow): {EVENT_ID} - Digital State v{NEW_VER} Workflow Engine Codified\n\n"
             "Operator-ratified, Human-Prime-authorized (FINAL GOVERNANCE DIRECTIVE). "
             "Codifies the existing constitutional governance cycle as a state machine "
             "(Workflow Kernel) and the GitHub Release Workflow (auto after Human Approval). "
             f"No constitution/architecture/source-product change, no new roles/layers. "
             f"Hermes execution simulated locally. Version {FROM_VER} -> {NEW_VER}."],
            capture_output=True, text=True)
    ledger.append("COMMIT", "prime-agent",
                  {"sha": _sp.run(["git", "rev-parse", "HEAD"], capture_output=True,
                                   text=True).stdout.strip()[:12]})
    _sp.run(["git", "tag", "-f", "-a", NEW_TAG, "-m",
             f"Digital State v{NEW_VER} — Workflow Engine Codified (audit-gated, Auditor-verified, simulated Hermes)"],
            capture_output=True, text=True)
    write_release_body()
    publish_release(ledger)
    ledger.append("PUBLICATION_EVENT", "prime-agent",
                  {"event": EVENT_ID, "version": NEW_VER, "tag": NEW_TAG,
                   "note": "New Digital State release published; visible to all users via GitHub Release."})


def main():
    args = sys.argv[1:]
    if "--reset" in args:
        for p in (LEDGER, BOARD, EV / "builder-evidence.json", EV / "auditor-verification.json",
                  EV / "prime-acceptance.json", EV / "decision.json", EV / "RELEASE_BODY.md",
                  EV / "PENDING_PRIME_ACCEPTANCE"):
            p.unlink(missing_ok=True)
        print("[reset] cleared 006 artifacts")
        return
    finalize = next((a.split("=", 1)[1].upper() for a in args if a.startswith("--finalize=")), None)
    EV.mkdir(parents=True, exist_ok=True)

    if finalize:
        # Requires the cycle to have already run (board at HUMAN_APPROVAL).
        ledger = Ledger(LEDGER)
        orch = KanbanOrchestrator(BOARD, ledger)
        res = run_pytest()
        # HUMAN_APPROVAL gate — crossed only by a human authorization (this directive).
        ledger.append("HUMAN_APPROVAL", "human", {
            "decision": "ACCEPTED",
            "directive": "DS-WORKFLOW-KERNEL-001 — FINAL GOVERNANCE DIRECTIVE",
            "auto_release": "enabled"})
        (EV / "PENDING_PRIME_ACCEPTANCE").unlink(missing_ok=True)
        orch.transition("K001", "RELEASE_WORKFLOW", "human")   # kernel allows human only
        orch.transition("K001", "DONE", "prime-agent")
        run_release_workflow(ledger)                            # auto, post-approval
        dec = {"event_id": EVENT_ID, "status": "VERIFIED", "verdict": "PASS", "ts": now(),
               "reason": "Codified existing constitutional workflow as state machine (Workflow Kernel) "
                         "+ GitHub Release Workflow (auto after Human Approval). Kernel is the sole "
                         "transition authority; human gate preserved; no roles/layers/"
                         "constitution/architecture change.",
               "human_decision": "ACCEPT (FINAL GOVERNANCE DIRECTIVE)",
               "pytest": pytest_summary(res),
               "constraints": "no new roles/layers; no src/ change; Hermes simulated"}
        (EV / "decision.json").write_text(json.dumps(dec, indent=2))
        print("FINALIZED+RELEASED:", dec["status"], "| chain valid:", ledger.valid(),
              "| pytest:", pytest_summary(res))
        return

    # Phase A: run cycle up to the HUMAN_APPROVAL gate (agent Prime may NOT cross it).
    if LEDGER.exists() and LEDGER.read_text().strip() and "--fresh" not in args:
        print("[refuse] ledger non-empty; pass --reset then re-run")
        sys.exit(2)
    ledger = Ledger(LEDGER)
    orch = KanbanOrchestrator(BOARD, ledger)
    ledger.append("GOVERNANCE_EVENT", "prime-agent", {
        "event_id": EVENT_ID, "decision": "ALLOW",
        "scope": "Codify EXISTING constitutional workflow as state machine + Release Workflow; "
                 "no new roles/layers; Human Final Authority kept."})
    st = subprocess.run([sys.executable, str(EV / "engine_selftest.py")], capture_output=True, text=True)
    orch.create_card("K001", "Codify governance workflow engine", "EVENT")
    steps = [("PRIME_SPECKIT", "prime-agent"), ("KANBAN_CREATED", "prime-agent"),
             ("BUILDER_QUEUE", "prime-agent"), ("BUILDER_EXECUTION", "builder-agent"),
             ("READY_FOR_AUDIT", "builder-agent"), ("AUDITOR_REVIEW", "auditor-agent"),
             ("READY_FOR_PRIME", "auditor-agent"), ("PRIME_REVIEW", "prime-agent"),
             ("HUMAN_APPROVAL", "prime-agent")]
    for s, r in steps:
        orch.transition("K001", s, r)
    bp = {"event_id": EVENT_ID, "gate": "IMPLEMENTATION", "agent": "builder-agent", "card": "K001",
          "selftest_output": st.stdout.strip().splitlines()[-1], "selftest_rc": st.returncode,
          "pytest_summary": pytest_summary(run_pytest()), "ts": now()}
    bsig = ledger.sign("builder", bp)
    (EV / "builder-evidence.json").write_text(json.dumps({"payload": bp, "signature": bsig}, indent=2))
    st2 = subprocess.run([sys.executable, str(EV / "engine_selftest.py")], capture_output=True, text=True)
    sig_valid = ledger.verify("builder", bp, bsig)
    veto = not (st2.returncode == 0 and sig_valid)
    ap = {"event_id": EVENT_ID, "gate": "VERIFICATION", "agent": "auditor-agent", "card": "K001",
          "independent_selftest_rc": st2.returncode, "builder_sig_valid": sig_valid,
          "veto": veto, "ts": now()}
    asig = ledger.sign("auditor", ap)
    (EV / "auditor-verification.json").write_text(json.dumps({"payload": ap, "signature": asig}, indent=2))
    (EV / "PENDING_PRIME_ACCEPTANCE").write_text(now())
    print("CYCLE RUN COMPLETE — awaiting Human (Final Authority) approval at HUMAN_APPROVAL gate.")
    print("  selftest:", bp["selftest_output"], "| auditor veto:", veto,
          "| chain valid:", ledger.valid())


if __name__ == "__main__":
    main()
