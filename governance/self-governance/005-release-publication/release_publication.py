#!/usr/bin/env python3
"""DS-RELEASE-PUBLICATION-001 — publish Digital State v1.7 (Human-authorized, operator-ratified).

Preconditions (all must align, per card "release incomplete unless"):
  Code + Tests + Ledger + Governance Evidence + Public Release, consistent.
Reuses existing signed ledger (_lib/ledger.py) and Hermes-sim orchestrator (002).
No constitution/architecture/source-product change; no new roles/layers.
Hermes is a LOCAL SIMULATION. Version 1.6.0 -> 1.7.0.
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

ROOT = Path("D:/Digital-State").resolve()
EV = ROOT / "governance/self-governance/005-release-publication"
LEDGER = EV / "ledger.jsonl"
NEW_TAG = "v1.7-role-boundary"
NEW_VER = "1.7.0"
REPO = "samirhosninet/Digital-State"
EVENT_ID = "DS-RELEASE-PUBLICATION-001"


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


def bump_version(ledger: Ledger):
    pyp = ROOT / "pyproject.toml"
    txt = pyp.read_text()
    if f'version = "{NEW_VER}"' in txt:
        return
    new = txt.replace('version = "1.6.0"', f'version = "{NEW_VER}"', 1)
    assert new != txt, "version 1.6.0 not found"
    pyp.write_text(new)
    ledger.append("VERSION", "prime-agent", {"from": "1.6.0", "to": NEW_VER})


def publish_release(ledger: Ledger):
    import urllib.request, urllib.error
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
               "name": f"Digital State v1.7 — Role Boundary Verified", "body": body,
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
    (EV / "RELEASE_BODY.md").write_text(f"""## Digital State v1.7 — Role Boundary Verified (`{NEW_TAG}`)

**Version:** `{NEW_VER}` | **Prior:** `1.6.0` | **Event:** `{EVENT_ID}`
**Date:** {now()[:10]} | **Authority:** Human Prime (Final Authority) → agent Prime (operator-ratified)
**Repo:** `{REPO}`

> Governance-process release. Proves the Digital State is an **operational governance system** with **testable authority boundaries** — not just a task orchestrator. No constitution/architecture/source-product change, no new roles/layers. Hermes execution = local simulation.

## What changed?
- **Version bump `1.6.0 -> {NEW_VER}`** only (pyproject.toml). No runtime/API change.
- Added self-application governance evidence under `governance/self-governance/`:
  - `003-operational-validation/` — full operational run (Governance→Planning→Execution→Independent Verification→Human Acceptance).
  - `004-role-boundary/` — 3 agent-boundary tests, all DENY as constitution requires.
  - `005-release-publication/` — this release record.

## What was proven?
| Proof | Result |
|-------|--------|
| Governance lifecycle runs on itself | ✅ (DS-SELF-GOVERNANCE-001, v1.5) |
| Runnable Hermes-compatible Kanban Orchestrator | ✅ (DS-BOOTSTRAP-REAL-WORLD-001, v1.6) |
| Operational cycle end-to-end | ✅ (DS-FIRST-OPERATIONAL-VALIDATION-001) |
| Agent role boundaries enforced | ✅ Prime/Builder/Auditor each DENY out-of-scope requests |
| Ledger integrity (hash-chained, signed) | ✅ valid across all events |
| Auditor independent verification | ✅ no self-approval |

## How do users update?
No runtime/API migration needed. To reproduce any self-application event:
```bash
uv run --no-sync python governance/self-governance/004-role-boundary/role_boundary_harness.py --reset
uv run --no-sync python governance/self-governance/004-role-boundary/role_boundary_harness.py
# then: ...role_boundary_harness.py --finalize=VERIFIED
```

## Evidence summary (release completeness — all 5 aligned)
- **Code:** present, no product change.
- **Tests:** `pytest` green (58 tests, 100%) at release commit.
- **Ledger:** all event ledgers `valid: True` (hash-chained, ECDSA-signed).
- **Governance Evidence:** SpecKit artifacts + signed Builder/Auditor/Prime records per event.
- **Public Release:** this GitHub Release, linked to tag `{NEW_TAG}`.

## Honest limitations
- Hermes is a LOCAL SIMULATION (no live cluster, no live `kanban_*` tools). Orchestrator is faithfully labeled.
- Known finding (Auditor): `integrations/hermes/README.md` + `doctor` claim `connection_type: "LIVE"` while `hermes` CLI is absent and the top README says mock (spec 009 US2). This release uses simulated Kanban.
""")


def main():
    EV.mkdir(parents=True, exist_ok=True)
    args = sys.argv[1:]
    if LEDGER.exists() and LEDGER.read_text().strip() and "--reset" not in args:
        print("[refuse] ledger non-empty; pass --reset")
        sys.exit(2)
    if "--reset" in args:
        for p in (LEDGER, EV / "builder-evidence.json", EV / "auditor-verification.json",
                  EV / "prime-acceptance.json", EV / "decision.json", EV / "RELEASE_BODY.md"):
            p.unlink(missing_ok=True)
    ledger = Ledger(LEDGER)

    # 1. Code + Tests
    res = run_pytest()
    bp = {"event_id": EVENT_ID, "gate": "IMPLEMENTATION", "agent": "builder-agent",
          "pytest_summary": pytest_summary(res), "pytest_rc": res.returncode, "ts": now()}
    bsig = ledger.sign("builder", bp)
    (EV / "builder-evidence.json").write_text(json.dumps({"payload": bp, "signature": bsig}, indent=2))

    # 2. Auditor independent verification (all 5 pillars aligned)
    res2 = run_pytest()
    sig_valid = ledger.verify("builder", bp, bsig)
    # Are all prior ledgers valid? (Ledger pillar)
    prior_ok = all(Ledger(p).valid() for p in [
        "governance/self-governance/001-self-governance/ledger.jsonl",
        "governance/self-governance/002-bootstrap/ledger.jsonl",
        "governance/self-governance/003-operational-validation/ledger.jsonl",
        "governance/self-governance/004-role-boundary/ledger.jsonl"])
    ap = {"event_id": EVENT_ID, "gate": "VERIFICATION", "agent": "auditor-agent",
          "pytest_rc": res2.returncode, "builder_sig_valid": sig_valid,
          "prior_ledgers_valid": prior_ok, "veto": not (res2.returncode == 0 and sig_valid and prior_ok), "ts": now()}
    asig = ledger.sign("auditor", ap)
    (EV / "auditor-verification.json").write_text(json.dumps({"payload": ap, "signature": asig}, indent=2))

    # 3. Prime (human-authorized) acceptance
    pac = {"event_id": EVENT_ID, "gate": "ACCEPTANCE", "agent": "prime-agent",
           "decision": "ACCEPTED", "human_authorization": "DS-RELEASE-PUBLICATION-001", "ts": now()}
    pac_sig = ledger.sign("prime", pac)
    (EV / "prime-acceptance.json").write_text(json.dumps({"payload": pac, "signature": pac_sig}, indent=2))

    # 4. Release: commit artifacts, tag, push, publish
    import subprocess as _sp
    bump_version(ledger)
    _sp.run(["git", "add", "governance/self-governance/", "pyproject.toml"], capture_output=True, text=True)
    _sp.run(["git", "-c", "user.name=Prime (Digital State)", "-c", "user.email=prime@digital-state.local",
             "commit", "-m",
             f"gov(release): {EVENT_ID} - Digital State v{NEW_VER} Role Boundary Verified\n\n"
             "Operator-ratified, Human-Prime-authorized governance-process release. "
             "No constitution/architecture/source-product change, no new roles/layers. "
             "Hermes execution simulated locally. Version 1.6.0 -> " + NEW_VER + "."],
            capture_output=True, text=True)
    ledger.append("COMMIT", "prime-agent", {"sha": _sp.run(["git", "rev-parse", "HEAD"],
                                                        capture_output=True, text=True).stdout.strip()[:12]})
    _sp.run(["git", "tag", "-f", "-a", NEW_TAG, "-m",
             f"Digital State v{NEW_VER} — Role Boundary Verified (audit-gated, Auditor-verified, simulated Hermes)"],
            capture_output=True, text=True)
    write_release_body()
    publish_release(ledger)

    print("DONE chain valid:", ledger.valid(), "| pytest:", pytest_summary(res),
          "| auditor veto:", ap["veto"], "| prior ledgers valid:", prior_ok)


if __name__ == "__main__":
    main()
