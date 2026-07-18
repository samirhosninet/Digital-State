import sys
sys.path.insert(0, 'governance/self-governance/_lib')
from ledger import Ledger
L = Ledger('governance/self-governance/005-release-publication/ledger.jsonl')
entry = L.append("HUMAN_ACCEPTANCE", "prime-agent", {
    "event_id": "DS-RELEASE-PUBLICATION-001",
    "human_card": "DS-RELEASE-PUBLICATION-001 — FINAL HUMAN ACCEPTANCE",
    "decision": "APPROVE RELEASE",
    "version": "v1.7",
    "status": "ACCEPTED",
    "note": "Human Prime (Final Authority) formally adopts v1.7 as the official current release of Digital State. Recorded post-publication; not folded into tagged commit 422fcc2 without re-tag consent."
})
print("appended seq", entry["sequence_id"], "valid:", L.valid())
