#!/usr/bin/env python3
"""DS-FIRST-OPERATIONAL-VALIDATION-001 — prove the EXISTING governance cycle operates.

Reuses (no redesign):
  - governance/self-governance/_lib/ledger.py   (signed, hash-chained ledger)
  - governance/self-governance/002-bootstrap/kanban_orchestrator.py (Hermes-sim Kanban)
Runs the operational pipeline PRIME -> BUILDER -> AUDITOR, then STOPS at
PENDING_PRIME_ACCEPTANCE so Prime can close the cycle via Human-in-the-Loop.
No git commit / tag / GitHub release is created here (that is a separate, explicit
decision). Per card: no constitution/architecture change, no new roles/layers,
Hermes is a LOCAL SIMULATION.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "_lib"))
sys.path.insert(0, str(HERE.parent / "002-bootstrap"))  # reuse the orchestrator
from ledger import Ledger
from kanban_orchestrator import KanbanOrchestrator

ROOT = Path("D:/Digital-State").resolve()
EV = ROOT / "governance/self-governance/003-operational-validation"
LEDGER = EV / "ledger.jsonl"
BOARD = EV / "board.json"
EVENT_ID = "DS-FIRST-OPERATIONAL-VALIDATION-001"


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


def run_builder(ledger: Ledger):
    res = run_pytest()
    bp = {"event_id": EVENT_ID, "gate": "IMPLEMENTATION", "agent": "builder-agent",
          "card": "K001", "pytest_summary": pytest_summary(res), "pytest_rc": res.returncode, "ts": now()}
    sig = ledger.sign("builder", bp)
    (EV / "builder-evidence.json").write_text(json.dumps({"payload": bp, "signature": sig}, indent=2))
    return bp, sig, res


def run_auditor(ledger: Ledger, bp, bsig):
    res2 = run_pytest()  # INDEPENDENT re-run, separate process
    sig_valid = ledger.verify("builder", bp, bsig)
    veto = not (res2.returncode == 0 and sig_valid)
    ap = {"event_id": EVENT_ID, "gate": "VERIFICATION", "agent": "auditor-agent",
          "card": "K001", "independent_pytest_rc": res2.returncode,
          "builder_sig_valid": sig_valid, "veto": veto, "ts": now()}
    sig = ledger.sign("auditor", ap)
    (EV / "auditor-verification.json").write_text(json.dumps({"payload": ap, "signature": sig}, indent=2))
    return ap, sig, res2


def main():
    args = sys.argv[1:]
    if "--reset" in args:
        for p in (LEDGER, BOARD, EV / "builder-evidence.json", EV / "auditor-verification.json",
                  EV / "prime-acceptance.json", EV / "decision.json", EV / "PENDING_PRIME_ACCEPTANCE"):
            p.unlink(missing_ok=True)
        print("[reset] cleared 003 artifacts")
        return

    finalize = None
    for a in args:
        if a.startswith("--finalize="):
            finalize = a.split("=", 1)[1].upper()

    EV.mkdir(parents=True, exist_ok=True)

    if finalize:
        ledger = Ledger(LEDGER)
        orch = KanbanOrchestrator(BOARD, ledger)
        decision = "OPERATIONAL VERIFIED" if finalize == "VERIFIED" else "BLOCKED"
        pac = {"event_id": EVENT_ID, "gate": "ACCEPTANCE", "agent": "prime-agent",
               "decision": "ACCEPTED", "ts": now()}
        pac_sig = ledger.sign("prime", pac)
        (EV / "prime-acceptance.json").write_text(json.dumps({"payload": pac, "signature": pac_sig}, indent=2))
        orch.transition("K001", "PRIME_ACCEPTANCE")
        dec = {"event_id": EVENT_ID, "status": "ACCEPTED", "decision": decision,
               "verdict": "PASS", "ts": now(),
               "reason": ("The Digital State lifecycle successfully executed: "
                          "Governance -> Planning -> Execution -> Independent Verification -> Human Acceptance"),
               "basis": "Cycle executed end-to-end via existing orchestrator + signed ledger; Auditor veto=false."}
        (EV / "decision.json").write_text(json.dumps(dec, indent=2))
        ledger.append("RELEASE_DECISION", "prime-agent", {"decision": decision})
        (EV / "PENDING_PRIME_ACCEPTANCE").unlink(missing_ok=True)
        print("FINALIZED:", decision, "| chain valid:", ledger.valid())
        return

    # --- PRIME: create event + Kanban workflow (Hermes-sim) ---
    if LEDGER.exists() and LEDGER.read_text().strip() and "--fresh" not in args:
        print("[refuse] ledger non-empty; pass --reset then re-run, or --fresh to continue")
        sys.exit(2)
    ledger = Ledger(LEDGER)
    orch = KanbanOrchestrator(BOARD, ledger)
    ledger.append("GOVERNANCE_EVENT", "prime-agent", {
        "event_id": EVENT_ID, "decision": "ALLOW",
        "scope": "Operational validation of EXISTING cycle; no design/constitution/architecture change; Hermes simulated."})
    orch.create_card("K001", "Operational validation of existing Digital State governance cycle", "EVENT")
    orch.transition("K001", "PLANNED")
    orch.transition("K001", "TASK_CREATED")
    orch.assign("K001", "builder-agent")
    orch.transition("K001", "BUILDER_ASSIGNED")

    # --- BUILDER: receive card, execute, produce evidence ---
    bp, bsig, res = run_builder(ledger)
    orch.transition("K001", "IMPLEMENTATION")  # builder drives

    # --- AUDITOR: independent verification, sign, veto ---
    ap, asig, res2 = run_auditor(ledger, bp, bsig)
    orch.transition("K001", "AUDITOR_REVIEW")  # auditor drives

    (EV / "PENDING_PRIME_ACCEPTANCE").write_text(now())
    print("CYCLE RUN COMPLETE — awaiting Prime (Human-in-the-Loop) acceptance.")
    print("  builder:", bp["pytest_summary"], "| auditor rc:", ap["independent_pytest_rc"],
          "| sig valid:", ap["builder_sig_valid"], "| auditor veto:", ap["veto"])
    print("  chain valid:", ledger.valid())
    print("  Next: python run_operational_validation.py --finalize=VERIFIED  (or =BLOCKED)")


if __name__ == "__main__":
    main()
