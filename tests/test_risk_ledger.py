"""Risk ledger validation tests for Digital State.

Verifies that the risk-ledger.md does not contain High-severity risks
with "Open" status at release time. release-grade packages must have
all High risks either Closed, Mitigated, Accepted, or Suppressed.
"""
import re
import os
import pytest

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
RISK_LEDGER = os.path.join(ROOT, "risk-ledger.md")


def read_risk_ledger() -> str:
    with open(RISK_LEDGER, encoding="utf-8") as f:
        return f.read()


def parse_risk_table(content: str) -> list[dict]:
    """Parse the main risk table from risk-ledger.md markdown."""
    rows = []
    in_table = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("| ID ") and "Description" in stripped:
            in_table = True
            continue
        if in_table and stripped.startswith("|") and "----" in stripped:
            continue
        if in_table and stripped.startswith("## "):
            break  # table ended
        if in_table and stripped.startswith("|"):
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if len(cells) >= 4:
                rows.append({
                    "id": cells[0],
                    "description": cells[1],
                    "severity": cells[2],
                    "status": cells[3],
                })
    return rows


class TestRiskLedger:
    """Risk ledger must not have High-severity Open risks at release."""

    def test_risk_ledger_exists(self):
        assert os.path.exists(RISK_LEDGER), "risk-ledger.md must exist"

    def test_risk_ledger_parseable(self):
        content = read_risk_ledger()
        rows = parse_risk_table(content)
        assert len(rows) > 0, "risk-ledger.md must contain at least one risk entry"

    def test_no_high_severity_open_risks(self):
        """Release gate: no High-severity risks with Open status."""
        content = read_risk_ledger()
        rows = parse_risk_table(content)
        high_open = [
            r for r in rows
            if r["severity"].lower() == "high" and r["status"].lower() == "open"
        ]
        assert len(high_open) == 0, (
            f"Found {len(high_open)} High-severity Open risk(s) — must be Closed/Mitigated/Accepted before release: "
            + ", ".join(r["id"] for r in high_open)
        )

    def test_all_risks_have_id(self):
        content = read_risk_ledger()
        rows = parse_risk_table(content)
        for row in rows:
            assert row["id"], "Every risk entry must have an ID"
            assert row["id"].startswith("RISK-"), f"Risk ID must follow RISK-NNN format: {row['id']}"
