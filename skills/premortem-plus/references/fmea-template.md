# Premortem Plus — FMEA Worksheet Template

> Use this template when a Digital State task requires FMEA analysis per `skills/premortem-plus/SKILL.md`.

## FMEA Worksheet

**Task/Card ID**: <card_id>
**Date**: YYYY-MM-DD
**Reviewer**: <agent or operator name>
**Process/Function**: <name of the process or function under analysis>

### 1. Failure Mode Identification

| ID | Component / Step | Failure Mode | Failure Effect | Severity (1–10) |
|----|------------------|--------------|-----------------|-----------------|
| FM-1 | | | | |
| FM-2 | | | | |
| FM-3 | | | | |

### 2. Cause Analysis

| ID | Failure Mode | Potential Cause | Occurrence (1–10) | Current Controls | Detection (1–10) |
|----|-------------|-----------------|-------------------|------------------|-------------------|
| FM-1 | | | | | |
| FM-2 | | | | | |
| FM-3 | | | | | |

### 3. Risk Priority Number (RPN)

| ID | Severity | Occurrence | Detection | RPN (S×O×D) | Criticality Rating |
|----|----------|------------|-----------|-------------|---------------------|
| FM-1 | | | | | Low / Medium / High / Critical |
| FM-2 | | | | | Low / Medium / High / Critical |
| FM-3 | | | | | Low / Medium / High / Critical |

**RPN Thresholds**:
- **1–50**: Low — monitor, no immediate action required
- **51–100**: Medium — compensating controls recommended
- **101–200**: High — corrective action required before proceeding
- **201+**: Critical — kill criterion; halt and rescue per Premortem Plus

### 4. Recommended Actions

| ID | Recommended Action | Responsible | Target Date | Revised RPN |
|----|-------------------|-------------|-------------|-------------|
| FM-1 | | | | |
| FM-2 | | | | |
| FM-3 | | | | |

### 5. Compensating Controls

| Control | Covers Failure Mode(s) | Effectiveness | Verification Method |
|---------|----------------------|----------------|---------------------|
| | | Low / Medium / High | |

### 6. FMEA Conclusion

**Premortem Status**: [NOT_TRIGGERED | TRIGGERED: <reason>]
**Overall Risk Level**: [Low / Medium / High / Critical]
**Decision**: [Proceed | Proceed with controls | Block and rework | Kill and rescue]
**Risk Ledger Entry**: [RISK-XXX | N/A]

---
*Managed per `skills/premortem-plus/SKILL.md`. Store completed worksheets alongside audit evidence on the relevant Kanban card.*
