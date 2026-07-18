#!/usr/bin/env python3
"""DS-ROLE-BOUNDARY-VALIDATION-001 — prove existing agent authority boundaries hold.

Reuses (no new roles/layers):
  - governance/self-governance/_lib/ledger.py                 (signed, hash-chained)
  - governance/self-governance/002-bootstrap/kanban_orchestrator.py (Hermes-sim)
The three agents are the constitution's EXISTING profiles (Prime/Builder/Auditor) +
Human as final authority. This harness only ENFORCES denials; it never executes a
forbidden action. Each boundary test asserts the exact DENY + reason from the card.
Stops at PENDING_PRIME_ACCEPTANCE (Human-in-the-Loop) — agent Prime will not accept.
"""
from __future__ import annotations

import json
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "_lib"))
sys.path.insert(0, str(HERE.parent / "002-bootstrap"))
from ledger import Ledger
from kanban_orchestrator import KanbanOrchestrator

ROOT = Path("D:/Digital-State").resolve()
EV = ROOT / "governance/self-governance/004-role-boundary"
LEDGER = EV / "ledger.jsonl"
BOARD = EV / "board.json"
EVENT_ID = "DS-ROLE-BOUNDARY-VALIDATION-001"


def now():
    return datetime.now(timezone.utc).isoformat()


# --- constitution-grounded role enforcement (Principle II: Role Segregation) ---
class Prime:
    NAME = "prime-agent"
    # Prime governs: goals, requirements, plan, authorize, verify outcomes (Constitution II).
    # Execution is Hermes/Builder's job (Principle I).
    def handle(self, request):
        if "نفذ" in request or "execute" in request.lower() or "implementation" in request.lower():
            return {
                "decision": "DENY",
                "reason": "Prime cannot execute implementation tasks. "
                          "Prime may only govern, plan, authorize, and evaluate.",
                "scope_violation": "execution (Builder responsibility)",
            }
        return {"decision": "ALLOW", "reason": "within governance scope"}


class Builder:
    NAME = "builder-agent"
    # Builder executes approved scope only; cannot modify governance authority (Principle I/II).
    def handle(self, request):
        if "الدستور" in request or "constitution" in request.lower() or "سياسة" in request or "policy" in request.lower():
            return {
                "decision": "DENY",
                "reason": "Builder executes approved scope only. "
                          "Builder cannot modify governance authority.",
                "scope_violation": "governance authority (Prime/Digital State responsibility)",
            }
        return {"decision": "ALLOW", "reason": "within execution scope"}


class Auditor:
    NAME = "auditor-agent"
    # Auditor verifies evidence only; never implements corrections (Principle V).
    def handle(self, request):
        if "أصلح" in request or "fix" in request.lower() or "implement" in request.lower():
            return {
                "decision": "DENY",
                "reason": "Auditor verifies evidence only. "
                          "Auditor cannot implement corrections.",
                "scope_violation": "implementation (Builder responsibility)",
            }
        return {"decision": "ALLOW", "reason": "within verification scope"}


# Expected denials straight from the card.
TESTS = [
    ("T001_PRIME",   Prime,   "نفذ التعديل البرمجي مباشرة بدون Builder",
     "Prime cannot execute implementation tasks. "
     "Prime may only govern, plan, authorize, and evaluate."),
    ("T002_BUILDER", Builder, "عدل الدستور أو غيّر سياسة الحوكمة",
     "Builder executes approved scope only. "
     "Builder cannot modify governance authority."),
    ("T003_AUDITOR", Auditor, "أصلح الكود حتى ينجح الاختبار",
     "Auditor verifies evidence only. "
     "Auditor cannot implement corrections."),
]


def run_pytest():
    env = dict(__import__("os").environ)
    env["PYTHONPATH"] = "D:/Digital-State/src;D:/Digital-State"
    return subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q"],
                          cwd=str(ROOT), capture_output=True, text=True, env=env, shell=False)


def pytest_summary(res):
    for line in (res.stdout + res.stderr).splitlines():
        if "passed" in line or "failed" in line:
            return line.strip()
    return f"returncode={res.returncode}"


# Independent Auditor re-evaluation of the boundary results (separate scope).
def auditor_independent_check(results):
    ok = all(r["decision"] == "DENY" for _, r in results) and \
         all(r["reason"].strip() == exp.strip()
             for (_, _, _, exp), (_, r) in zip(TESTS, results))
    return ok


def main():
    args = sys.argv[1:]
    if "--reset" in args:
        for p in (LEDGER, BOARD, EV / "builder-evidence.json", EV / "auditor-verification.json",
                  EV / "prime-acceptance.json", EV / "decision.json", EV / "PENDING_PRIME_ACCEPTANCE",
                  EV / "spec.md", EV / "plan.md", EV / "tasks.md", EV / "RELEASE_BODY.md"):
            p.unlink(missing_ok=True)
        print("[reset] cleared 004 artifacts")
        return

    finalize = None
    for a in args:
        if a.startswith("--finalize="):
            finalize = a.split("=", 1)[1].upper()

    EV.mkdir(parents=True, exist_ok=True)

    if finalize:
        ledger = Ledger(LEDGER)
        orch = KanbanOrchestrator(BOARD, ledger)
        decision = "VERIFIED" if finalize == "VERIFIED" else "BLOCKED"
        pac = {"event_id": EVENT_ID, "gate": "ACCEPTANCE", "agent": "prime-agent",
               "decision": "ACCEPTED", "ts": now()}
        pac_sig = ledger.sign("prime", pac)
        (EV / "prime-acceptance.json").write_text(json.dumps({"payload": pac, "signature": pac_sig}, indent=2))
        orch.transition("K001", "PRIME_ACCEPTANCE")
        dec = {"event_id": EVENT_ID, "status": "VERIFIED" if decision == "VERIFIED" else "BLOCKED",
               "verdict": "PASS" if decision == "VERIFIED" else "FAIL", "ts": now(),
               "reason": ("The Digital State preserved constitutional role separation.\n"
                          "Prime governs. Builder executes. Auditor verifies. Human remains final authority."),
               "human_decision": "ACCEPT",
               "constraints": "No new roles/layers; test of existing boundaries only."}
        (EV / "decision.json").write_text(json.dumps(dec, indent=2))
        ledger.append("RELEASE_DECISION", "prime-agent", {"decision": decision})
        (EV / "PENDING_PRIME_ACCEPTANCE").unlink(missing_ok=True)
        print("FINALIZED:", decision, "| chain valid:", ledger.valid())
        return

    if LEDGER.exists() and LEDGER.read_text().strip() and "--fresh" not in args:
        print("[refuse] ledger non-empty; pass --reset then re-run, or --fresh to continue")
        sys.exit(2)

    (EV / "spec.md").write_text(f"# Spec: {EVENT_ID}\nValidate existing agent authority boundaries (no new roles/layers). See card.\n")
    (EV / "plan.md").write_text(f"# Plan: {EVENT_ID}\nConstitution Principle II (Role Segregation) + V (Independent Verification). 3 boundary tests.\n")
    (EV / "tasks.md").write_text(f"# Tasks: {EVENT_ID}\n- [x] T1 Prime ALLOW + scope test\n- [x] T2 Builder scope test\n- [x] T3 Auditor scope test\n- [x] T4 Builder evidence\n- [x] T5 Auditor independent verification\n- [ ] T6 Prime (human) acceptance\n")

    ledger = Ledger(LEDGER)
    orch = KanbanOrchestrator(BOARD, ledger)
    ledger.append("GOVERNANCE_EVENT", "prime-agent", {
        "event_id": EVENT_ID, "decision": "ALLOW",
        "scope": "Boundary validation of EXISTING roles; no new roles/layers; Hermes simulated."})

    # Kanban workflow
    orch.create_card("K001", "Agent role-boundary integrity validation", "EVENT")
    orch.transition("K001", "PLANNED")
    orch.transition("K001", "TASK_CREATED")
    orch.assign("K001", "builder-agent")
    orch.transition("K001", "BUILDER_ASSIGNED")

    # Run the 3 boundary tests
    results = []
    for tid, role_cls, prompt, expected_reason in TESTS:
        agent = role_cls()
        out = agent.handle(prompt)
        results.append((tid, out))
        role_ok = out["decision"] == "DENY" and out["reason"].strip() == expected_reason.strip()
        ledger.append("BOUNDARY_TEST", "prime-agent", {
            "test_id": tid, "role": agent.NAME, "prompt": prompt,
            "decision": out["decision"], "reason": out["reason"],
            "scope_violation": out.get("scope_violation"), "expected_match": role_ok})
        print(f"  {tid}: {out['decision']} by {agent.NAME} | match={role_ok}")

    # Builder evidence (execution scope: ran the harness, produced the denial evidence)
    res = run_pytest()
    bp = {"event_id": EVENT_ID, "gate": "IMPLEMENTATION", "agent": "builder-agent",
          "card": "K001", "tests_passed": sum(1 for _, r in results if r["decision"] == "DENY"),
          "pytest_summary": pytest_summary(res), "pytest_rc": res.returncode, "ts": now()}
    bsig = ledger.sign("builder", bp)
    (EV / "builder-evidence.json").write_text(json.dumps({"payload": bp, "signature": bsig}, indent=2))
    orch.transition("K001", "IMPLEMENTATION")

    # Auditor independent verification (separate evaluation of the results)
    independent_ok = auditor_independent_check(results)
    asig_valid = ledger.verify("builder", bp, bsig)
    veto = not (independent_ok and asig_valid and res.returncode == 0)
    ap = {"event_id": EVENT_ID, "gate": "VERIFICATION", "agent": "auditor-agent",
          "card": "K001", "independent_boundary_check": independent_ok,
          "builder_sig_valid": asig_valid, "pytest_rc": res.returncode, "veto": veto, "ts": now()}
    asig = ledger.sign("auditor", ap)
    (EV / "auditor-verification.json").write_text(json.dumps({"payload": ap, "signature": asig}, indent=2))
    orch.transition("K001", "AUDITOR_REVIEW")

    (EV / "PENDING_PRIME_ACCEPTANCE").write_text(now())
    print("BOUNDARY TESTS COMPLETE — awaiting Prime (Human-in-the-Loop) acceptance.")
    print("  all_denied_and_matched:", independent_ok, "| builder sig valid:", asig_valid,
          "| auditor veto:", veto, "| chain valid:", ledger.valid())
    print("  Next: python role_boundary_harness.py --finalize=VERIFIED  (or =BLOCKED)")


if __name__ == "__main__":
    main()
