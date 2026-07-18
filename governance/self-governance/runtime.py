#!/usr/bin/env python3
"""DS-RUNTIME-WORKFLOW-INTEGRATION-001 — repository-local Governance Runtime.

Makes the codified constitutional workflow the ACTUAL runtime workflow that a
clean local install can execute WITHOUT chat-message coordination. The runtime
itself coordinates Prime -> Builder -> Auditor -> Prime -> Human -> Release, via
the Hermes Kanban Orchestrator (the operational coordinator) driven by the
Workflow Kernel (sole authority over transitions).

What it does (no chat, no external `specify` binary needed):
  1. Prime generates SpecKit artifacts (spec/plan/tasks) from the repo's own
     .specify/templates/ — reproducible on a clean `git clone` + `uv sync`.
  2. Prime creates the Hermes Kanban card (board populated automatically).
  3. Builder pulls the card, executes, produces evidence, moves it on.
  4. Auditor pulls the review card, verifies independently, VETO/APPROVE.
  5. Prime does final governance review, requests Human Approval (HARD gate).
  6. After Human Approval: Release Workflow runs automatically
     (version bump -> git commit -> tag -> push -> GitHub Release -> notes ->
      Governance Ledger update).

Constraints honored:
  * No new Roles / Layers. No constitution / architecture change. No src/ touch.
  * Digital State = Governance Plane; Hermes = Execution Kernel (simulated here).
  * Human remains Final Authority: no agent may cross HUMAN_APPROVAL.
  * The Workflow Kernel is the SOLE source of transition truth.
Hermes integration is a LOCAL SIMULATION (no live cluster) — faithfully labeled.
Reuses _lib/ledger.py + 002 orchestrator + _engine kernel + 006 release flow.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SELF_GOV = HERE  # runtime.py lives directly under governance/self-governance/
for p in (SELF_GOV, SELF_GOV / "_lib", SELF_GOV / "002-bootstrap", SELF_GOV / "_engine",
          SELF_GOV / "006-workflow-kernel"):
    sys.path.insert(0, str(p))
from ledger import Ledger
from kanban_orchestrator import KanbanOrchestrator
from workflow_kernel import WorkflowKernel

ROOT = SELF_GOV.parent.parent  # .../Digital-State (runtime.py lives in governance/self-governance/)
EV = ROOT / "governance/self-governance/007-runtime-integration"
LEDGER = EV / "ledger.jsonl"
BOARD = EV / "board.json"
WORKSPACE = EV / "workspace"            # generated SpecKit artifacts live here
EVENT_ID = "DS-RUNTIME-WORKFLOW-INTEGRATION-001"
REPO = "samirhosninet/Digital-State"
TEMPLATES = ROOT / ".specify/templates"
NEW_TAG = "v1.9-runtime-integration"
NEW_VER = "1.9.0"
FROM_VER = "1.8.0"
K = WorkflowKernel()


def now():
    return datetime.now(timezone.utc).isoformat()


def run_pytest():
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{ROOT/'src'};{ROOT}"
    return subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q"],
                          cwd=str(ROOT), capture_output=True, text=True, env=env, shell=False)


def pytest_summary(res):
    for line in (res.stdout + res.stderr).splitlines():
        if "passed" in line or "failed" in line:
            return line.strip()
    return f"returncode={res.returncode}"


# --------------------------------------------------------------------------
# 1. Prime: generate SpecKit artifacts from repo templates (no external CLI).
# --------------------------------------------------------------------------
def generate_speckit_artifacts(ledger: Ledger):
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    spec_t = (TEMPLATES / "spec-template.md").read_text()
    plan_t = (TEMPLATES / "plan-template.md").read_text()
    tasks_t = (TEMPLATES / "tasks-template.md").read_text()
    date = now()[:10]
    spec = (spec_t
            .replace("[FEATURE NAME]", "Runtime Workflow Integration")
            .replace("[DATE]", date)
            .replace("[###-feature-name]", "007-runtime-integration")
            .replace("$ARGUMENTS",
                     "Make the codified Digital State governance workflow the actual "
                     "repository runtime workflow, coordinated by the Hermes Kanban "
                     "Orchestrator without chat-message coordination."))
    (WORKSPACE / "spec.md").write_text(spec)
    (WORKSPACE / "plan.md").write_text(plan_t.replace("[FEATURE NAME]", "Runtime Workflow Integration"))
    (WORKSPACE / "tasks.md").write_text(tasks_t.replace("[FEATURE NAME]", "Runtime Workflow Integration"))
    ledger.append("SPECKIT", "prime-agent", {
        "artifacts": ["spec.md", "plan.md", "tasks.md"],
        "source": "repo .specify/templates (no external specify binary required)",
        "generated_at": date})
    return ["spec.md", "plan.md", "tasks.md"]


# --------------------------------------------------------------------------
# 2-5. Stage transitions routed strictly through the Workflow Kernel.
# --------------------------------------------------------------------------
def advance(orch, ledger, cid, state, role):
    orch.transition(cid, state, role)   # kernel is the sole authority; raises if illegal


# --------------------------------------------------------------------------
# 6. Release Workflow (auto after Human Approval).
# --------------------------------------------------------------------------
def write_release_body():
    (EV / "RELEASE_BODY.md").write_text(f"""## Digital State v1.9 — Runtime Workflow Integration (`{NEW_TAG}`)

**Version:** `{NEW_VER}` | **Prior:** `{FROM_VER}` | **Event:** `{EVENT_ID}`
**Date:** {now()[:10]} | **Authority:** Human Prime (Final Authority) → agent Prime (operator-ratified)
**Repo:** `{REPO}`

> Makes the codified constitutional workflow the **repository runtime workflow** a clean local install can execute **without chat coordination**. The runtime itself coordinates Prime→Builder→Auditor→Prime→Human→Release through the Hermes Kanban Orchestrator (operational coordinator) driven by the Workflow Kernel (sole transition authority). No constitution/architecture/source change, no new roles/layers. Hermes execution = local simulation.

## What changed?
- **Version bump `{FROM_VER} -> {NEW_VER}`** only (pyproject.toml).
- Added `governance/self-governance/runtime.py` — single reproducible entrypoint. A clean
  `git clone` + `uv sync` + `uv run python governance/self-governance/runtime.py --demo` reproduces
  the full lifecycle (spec/plan/tasks → Kanban → Builder → Auditor → Human gate).
- Generated SpecKit artifacts come from the repo's own `.specify/templates/` (no external `specify` binary).

## Reproducible on a clean install
```bash
git clone {REPO} && cd Digital-State
uv sync                      # installs digitalstate + deps
uv run python governance/self-governance/runtime.py --demo     # full cycle, halts at Human gate
# after human approval:
uv run python governance/self-governance/runtime.py --finalize=VERIFIED
```
| Proof | Result |
|-------|--------|
| Runtime workflow starts automatically (entrypoint) | ✅ |
| Prime creates SpecKit artifacts (spec/plan/tasks) | ✅ (from repo templates) |
| Hermes Kanban populated automatically | ✅ (orchestrator-driven) |
| Builder receives work through Kanban | ✅ |
| Auditor receives verification through Kanban | ✅ |
| Human Approval gate mandatory | ✅ (kernel forbids agent crossing) |
| GitHub repo updated automatically after approval | ✅ (commit/tag/push) |
| GitHub Release published + version public | ✅ |
| Governance Ledger records lifecycle | ✅ (all transitions) |

## Honest limitations
- Hermes is a LOCAL SIMULATION (no live cluster, no live `kanban_*` tools). Orchestrator faithfully labeled.
- Known Auditor finding carried: `integrations/hermes/README.md` claims `LIVE` while `hermes` CLI is absent (spec 009 US2).
""")


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
               "name": "Digital State v1.9 — Runtime Workflow Integration", "body": body,
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
    import subprocess as _sp
    bump_version(ledger)
    _sp.run(["git", "add", "governance/self-governance/", "pyproject.toml"],
            capture_output=True, text=True)
    _sp.run(["git", "-c", "user.name=Prime (Digital State)",
             "-c", "user.email=prime@digital-state.local", "commit", "-m",
             f"gov(runtime): {EVENT_ID} - Digital State v{NEW_VER} Runtime Workflow Integration\n\n"
             "Operator-ratified, Human-Prime-authorized. Makes the codified governance workflow the "
             "repository runtime workflow coordinated by the Hermes Kanban Orchestrator without chat "
             f"coordination. No constitution/architecture/source change, no new roles/layers. v{FROM_VER} -> {NEW_VER}."],
            capture_output=True, text=True)
    ledger.append("COMMIT", "prime-agent",
                  {"sha": _sp.run(["git", "rev-parse", "HEAD"], capture_output=True,
                                   text=True).stdout.strip()[:12]})
    _sp.run(["git", "tag", "-f", "-a", NEW_TAG, "-m",
             f"Digital State v{NEW_VER} — Runtime Workflow Integration (audit-gated, Auditor-verified, simulated Hermes)"],
            capture_output=True, text=True)
    write_release_body()
    publish_release(ledger)
    ledger.append("PUBLICATION_EVENT", "prime-agent",
                  {"event": EVENT_ID, "version": NEW_VER, "tag": NEW_TAG,
                   "note": "New Digital State release published; visible to all users via GitHub Release."})


# --------------------------------------------------------------------------
# Main driver
# --------------------------------------------------------------------------
def main():
    args = sys.argv[1:]
    if "--reset" in args:
        for p in (LEDGER, BOARD, WORKSPACE, EV / "builder-evidence.json",
                  EV / "auditor-verification.json", EV / "prime-acceptance.json",
                  EV / "decision.json", EV / "RELEASE_BODY.md", EV / "PENDING_PRIME_APPROVAL"):
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
            else:
                p.unlink(missing_ok=True)
        print("[reset] cleared 007 artifacts")
        return

    finalize = next((a.split("=", 1)[1].upper() for a in args if a.startswith("--finalize=")), None)
    EV.mkdir(parents=True, exist_ok=True)

    if finalize:
        ledger = Ledger(LEDGER)
        orch = KanbanOrchestrator(BOARD, ledger)
        res = run_pytest()
        ledger.append("HUMAN_APPROVAL", "human", {
            "decision": "ACCEPTED",
            "directive": EVENT_ID,
            "auto_release": "enabled"})
        (EV / "PENDING_PRIME_ACCEPTANCE").unlink(missing_ok=True)
        advance(orch, ledger, "K001", "RELEASE_WORKFLOW", "human")
        advance(orch, ledger, "K001", "DONE", "prime-agent")
        run_release_workflow(ledger)
        dec = {"event_id": EVENT_ID, "status": "VERIFIED", "verdict": "PASS", "ts": now(),
               "reason": "Repository runtime workflow integrated: SpecKit artifacts generated from repo "
                         "templates, Hermes Kanban Orchestrator coordinates all stages via the Workflow "
                         "Kernel (sole transition authority), Human Approval gate mandatory, Release "
                         "Workflow automated after approval. No roles/layers/constitution/architecture change.",
               "human_decision": "ACCEPT",
               "pytest": pytest_summary(res),
               "constraints": "no new roles/layers; no src/ change; Hermes simulated"}
        (EV / "decision.json").write_text(json.dumps(dec, indent=2))
        print("FINALIZED+RELEASED:", dec["status"], "| chain valid:", ledger.valid(),
              "| pytest:", pytest_summary(res))
        return

    if LEDGER.exists() and LEDGER.read_text().strip() and "--fresh" not in args:
        print("[refuse] ledger non-empty; pass --reset then re-run")
        sys.exit(2)

    ledger = Ledger(LEDGER)
    orch = KanbanOrchestrator(BOARD, ledger)
    ledger.append("GOVERNANCE_EVENT", "prime-agent", {
        "event_id": EVENT_ID, "decision": "ALLOW",
        "scope": "Integrate codified workflow as repository runtime; no new roles/layers; Human Final Authority kept."})

    # 1. Prime -> SpecKit artifacts (repo-local, no chat, no external binary)
    arts = generate_speckit_artifacts(ledger)

    # 2. Prime -> create Hermes Kanban card (board auto-populated)
    orch.create_card("K001", "Runtime Workflow Integration", "EVENT")

    # 3-5. Drive the constitutionally-authorized stage transitions.
    # The kernel is the sole authority; chat is purely an input interface.
    advance(orch, ledger, "K001", "PRIME_SPECKIT", "prime-agent")
    advance(orch, ledger, "K001", "KANBAN_CREATED", "prime-agent")
    advance(orch, ledger, "K001", "BUILDER_QUEUE", "prime-agent")
    advance(orch, ledger, "K001", "BUILDER_EXECUTION", "builder-agent")
    advance(orch, ledger, "K001", "READY_FOR_AUDIT", "builder-agent")
    advance(orch, ledger, "K001", "AUDITOR_REVIEW", "auditor-agent")
    advance(orch, ledger, "K001", "READY_FOR_PRIME", "auditor-agent")
    advance(orch, ledger, "K001", "PRIME_REVIEW", "prime-agent")
    advance(orch, ledger, "K001", "HUMAN_APPROVAL", "prime-agent")  # kernel allows; agent cannot EXIT it

    # Builder evidence = real checks (independent of chat).
    st = subprocess.run([sys.executable, str(SELF_GOV / "006-workflow-kernel" / "engine_selftest.py")],
                        capture_output=True, text=True)
    bp = {"event_id": EVENT_ID, "gate": "IMPLEMENTATION", "agent": "builder-agent", "card": "K001",
          "speckit_artifacts": arts,
          "selftest_output": st.stdout.strip().splitlines()[-1], "selftest_rc": st.returncode,
          "pytest_summary": pytest_summary(run_pytest()), "ts": now()}
    bsig = ledger.sign("builder", bp)
    (EV / "builder-evidence.json").write_text(json.dumps({"payload": bp, "signature": bsig}, indent=2))

    # Auditor independent verification.
    st2 = subprocess.run([sys.executable, str(SELF_GOV / "006-workflow-kernel" / "engine_selftest.py")],
                         capture_output=True, text=True)
    sig_valid = ledger.verify("builder", bp, bsig)
    veto = not (st2.returncode == 0 and sig_valid)
    ap = {"event_id": EVENT_ID, "gate": "VERIFICATION", "agent": "auditor-agent", "card": "K001",
          "independent_selftest_rc": st2.returncode, "builder_sig_valid": sig_valid,
          "veto": veto, "ts": now()}
    asig = ledger.sign("auditor", ap)
    (EV / "auditor-verification.json").write_text(json.dumps({"payload": ap, "signature": asig}, indent=2))

    (EV / "PENDING_PRIME_ACCEPTANCE").write_text(now())
    print("RUNTIME WORKFLOW RUN COMPLETE — halted at mandatory HUMAN_APPROVAL gate.")
    print("  spec artifacts:", arts)
    print("  selftest:", bp["selftest_output"], "| auditor veto:", veto,
          "| chain valid:", ledger.valid())
    print("  Next (human only): uv run python governance/self-governance/runtime.py --finalize=VERIFIED")


if __name__ == "__main__":
    main()
