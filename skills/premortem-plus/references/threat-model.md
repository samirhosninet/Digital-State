# Premortem Plus — Threat Model Template

> Use this template when a Digital State task touches irreversible operations, credentials, production systems, or external dependencies.

## Threat Model Worksheet

**Task/Card ID**: <card_id>
**Date**: YYYY-MM-DD
**Reviewer**: <agent or operator name>

### 1. Assets at Risk

| Asset | Type | Sensitivity | Location |
|-------|------|-------------|----------|
| | Data / Credential / Config / Infrastructure | Public / Internal / Confidential / Secret | |

### 2. Threat Actors

| Actor | Capability | Motivation | Access Level |
|-------|-----------|------------|--------------|
| | Low / Medium / High | N/A / Low / Medium / High | None / Read / Write / Admin |

### 3. Threat Scenarios

| ID | Threat | Actor → Asset | Likelihood | Impact | Risk | Mitigation |
|----|--------|---------------|-----------|--------|------|------------|
| T-1 | | | 1–5 | 1–5 | L×I | |
| T-2 | | | 1–5 | 1–5 | L×I | |

### 4. Attack Surface

- **Input vectors**: (user input, API calls, file reads, environment variables)
- **Output vectors**: (file writes, network calls, state mutations)
- **Privilege boundaries**: (profile isolation, file boundaries, Kanban permissions)

### 5. Security Controls

| Control | Type | Status | Coverage |
|---------|------|--------|----------|
| | Preventive / Detective / Corrective | Implemented / Planned / Missing | Partial / Full |

### 6. Residual Risk

| Risk | Accepted? | Rationale | Sign-off |
|------|-----------|-----------|----------|
| | Yes / No | | |

---

## Premortem Threat Prompts

Answer these before any irreversible action:

1. **What is the worst case?** If this change goes wrong, what is the maximum blast radius?
2. **How would it fail silently?** What failure mode would produce no error message but corrupt state?
3. **What credential leak path exists?** Could any secret appear in logs, prompts, or Kanban cards?
4. **What rollback exists?** If this change must be reversed, what is the exact reversal procedure?
5. **What cross-profile contamination could occur?** Could a Builder action affect Auditor or Prime state?
6. **What file boundary could be breached?** Could this change touch files outside the authorized scope?
7. **What dependency risk exists?** Could an external service (API, model provider) failure cascade?

If any answer reveals an unmitigable risk, the card MUST be blocked and escalated to Prime/User.
