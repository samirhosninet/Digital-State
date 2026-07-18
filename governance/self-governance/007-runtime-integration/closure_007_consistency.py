"""Prime closure procedure for card DS-RELEASE-CONSISTENCY-001.

Human Final Authority (card DS-RELEASE-CONSISTENCY-001 — FINAL AUTHORIZATION)
APPROVED this closure. This script, executed by Prime (governance authority only),
performs the authorized administrative actions:
  1. Append a PRIME_CLOSURE entry to the event ledger (hash-chained).
  2. Mark card DS-RELEASE-CONSISTENCY-001 as COMPLETED in board.json.
  3. Publish the governance completion record.

It does NOT modify: repository source, commits, tags, release artifacts,
architecture, constitution, or runtime. Check-list item #6 wording correction is
handled separately in AUDITOR_VERIFICATION_CARD.md (documentation-only).
"""
import sys, json
from pathlib import Path
from datetime import datetime, timezone

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE.parent / "_lib"))
from ledger import Ledger

# --- 1. Ledger PRIME_CLOSURE entry -----------------------------------------
ledger_path = BASE / "ledger.jsonl"
L = Ledger(str(ledger_path))
entry = L.append("PRIME_CLOSURE", "prime-agent", {
    "card": "DS-RELEASE-CONSISTENCY-001",
    "parent_event": "DS-RUNTIME-WORKFLOW-INTEGRATION-001",
    "release": "v1.9-runtime-integration",
    "release_id": 356074804,
    "target_commitish": "b1798d7328bc2ff1d7055f81a2db35fdd4ebc57b",
    "annotated_tag_object": "9db0fabfdeec55b98966d120da60b72f843f2788",
    "decision": "CLOSED",
    "verdict": "PASS",
    "veto": False,
    "correction": "checklist item #6 wording clarified (annotated tag object vs peeled commit ^{}); documentation-only, no veto, outcome unchanged",
    "human_authorization": "DS-RELEASE-CONSISTENCY-001 — FINAL AUTHORIZATION (Human Final Authority: AUTHORIZED)",
    "note": "Constitutional lifecycle complete: Prime->Builder->Auditor->Prime Closure. GitHub is the official published baseline; future installs must use v1.9-runtime-integration.",
})
seq = entry["sequence_id"]
ts = entry["timestamp"]
h = entry["hash"]
valid = L.valid()
print(f"PRIME_CLOSURE appended: seq={seq} ts={ts} hash={h} valid={valid}")

# --- 2. board.json: mark card COMPLETED ------------------------------------
board_path = BASE / "board.json"
board = json.loads(board_path.read_text())
board.setdefault("cards", {})["DS-RELEASE-CONSISTENCY-001"] = {
    "id": "DS-RELEASE-CONSISTENCY-001",
    "title": "Release Metadata Reconciliation — Final Closure",
    "gate": "VERIFICATION",
    "state": "COMPLETED",
    "assignee": "prime-agent",
    "comments": [],
}
board.setdefault("history", []).append({
    "ts": ts,
    "action": "closure",
    "by": "prime-agent",
    "card": "DS-RELEASE-CONSISTENCY-001",
    "to": "COMPLETED",
    "authorized_by": "human",
})
board_path.write_text(json.dumps(board, indent=2) + "\n")
print("board.json updated")

# --- 3. Publish completion record ------------------------------------------
record = f"""# Governance Completion Record — DS-RELEASE-CONSISTENCY-001

**Event (parent):** DS-RUNTIME-WORKFLOW-INTEGRATION-001
**Card:** DS-RELEASE-CONSISTENCY-001 — Release Metadata Reconciliation (Final Handoff)
**Release:** v1.9-runtime-integration (id 356074804)
**Target commitish:** b1798d7328bc2ff1d7055f81a2db35fdd4ebc57b
**Annotated tag object:** 9db0fabfdeec55b98966d120da60b72f843f2788 (peels to b1798d7…)
**Status:** COMPLETED
**Verdict:** PASS (Auditor) / CLOSED (Prime)
**Veto:** none

## Constitutional Lifecycle
Prime -> Builder -> Auditor -> Prime Closure — complete. No constitutional, architectural, runtime, repository, or release defects.

## Auditor Handoff (summary)
- GitHub Release verified.
- Release metadata synchronized.
- Approved tag verified.
- Repository baseline verified.
- Commit integrity verified.
- No force push detected.
- No repository modifications during reconciliation.
- No constitutional / architectural / runtime changes.
- No VETO conditions triggered.
- **PASS** — independent verification complete; proceed to constitutional closure.

## Prime Review (independent re-verification)
8 claims re-checked locally: 7 confirmed; claim #6 required a wording correction (annotated tag object vs peeled commit) — documentation only, outcome unchanged.

## Documentation Clarification (Prime)
Checklist item #6 originally stated the tag "derefs to b1798d7…". Corrected to: tag v1.9-runtime-integration is an **annotated** tag; the ref resolves to tag object 9db0fab… which peels (^{{}}) to commit b1798d7328bc2ff1d7055f81a2db35fdd4ebc57b. Local and remote unchanged. Wording fix only.

## Human Final Authority Authorization
Card DS-RELEASE-CONSISTENCY-001 — FINAL AUTHORIZATION: **APPROVED**. Authorized Prime to (1) correct #6 wording, (2) record as doc clarification, (3) not modify repo/commits/tags/artifacts/architecture/constitution/runtime, (4) append PRIME_CLOSURE ledger entry, (5) mark card COMPLETED, (6) publish completion record. No VETO. Human Final Authority: AUTHORIZED.

## Final Determinations
- GitHub is the official published baseline.
- The published release v1.9-runtime-integration is the current production baseline.
- Future installations must use this published release.
- No additional Builder or Auditor tasks created for this event.

## Ledger
PRIME_CLOSURE entry appended: sequence_id={seq}, timestamp={ts}, hash={h}. Chain valid: {valid}.
"""
(BASE / "COMPLETION_RECORD_DS-RELEASE-CONSISTENCY-001.md").write_text(record)
print("COMPLETION_RECORD written")
