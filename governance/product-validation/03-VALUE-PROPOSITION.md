# Value Proposition

**Status:** DRAFT — awaiting external validation  
**Date:** 2026-07-17  
**Authority:** PRIME (Governance)  
**Phase:** Product Validation

---

## Value Proposition Statement

> **Digital State gives autonomous AI coding agents a governance layer — so operators can prove, audit, and control what agents do, without slowing down development velocity.**

---

## Core Value Dimensions

| Dimension | Value Delivered | Evidence Required |
|-----------|-----------------|-------------------|
| **Accountability** | Every agent action is traceable to a registered identity with a verified signature | External auditor confirms audit trail holds up to scrutiny |
| **Control** | Operators define role-segregated permissions; agents cannot self-approve | Operator demonstrates "Builder cannot approve own work" in live session |
| **Velocity** | Governance is local, file-based, and zero-latency — no remote API calls | Benchmark: < 10ms per governance decision in live workflow |
| **Portability** | Works with any agent runtime (Hermes, Codex CLI, Claude Code, custom) | Install and run governance check on 2+ different agent runtimes |
| **Compliance Readiness** | Cryptographically chained audit log satisfies SOC2/GDPR evidence requirements | Compliance officer validates log structure and chain integrity |

---

## Differentiation vs. Alternatives

| Alternative | Digital State Advantage |
|-------------|-------------------------|
| **Manual PR review** | Cryptographic proof of *who authorized what*, not just who clicked "approve" |
| **Git signed commits** | Role segregation + lifecycle gates, not just author identity |
| **CI/CD approval gates** | Agent-native (intercepts tool calls), runtime-agnostic, local-first |
| **OPA/Cedar policies** | Built-in agent identity model + lifecycle + audit chaining |
| **Custom scripts** | Standardized, tested, governed framework — not ad-hoc glue code |

---

## Quantified Value Claims (Hypotheses — Require Validation)

| Claim | Hypothesis | Validation Method |
|-------|------------|-------------------|
| **Time to first governed workflow** | < 5 minutes from `pip install` to first approved gate | Time new user through `init` → `doctor` → first `approve` |
| **Governance overhead per task** | < 30 seconds additional per feature gate | Measure real workflow vs. ungoverned baseline |
| **Audit preparation time** | 90% reduction vs. manual evidence gathering | Compare audit prep with/without Digital State |
| **Agent error interception** | 100% of unauthorized tool calls blocked | Run red-team tests with unauthorized actions |

---

## Target Value Delivery Scenarios

### Scenario 1: Solo Developer → Client Delivery
**Context:** Freelancer uses Codex CLI to build a feature for a client. Client requires proof of review.
**Value:** `digitalstate approve` + audit log = instant compliance evidence. No manual screenshotting.

### Scenario 2: Team with Regulatory Requirements
**Context:** FinTech team uses Hermes Agent for internal tooling. SOC2 audit requires segregation of duties.
**Value:** Builder/Auditor role enforcement + immutable log = audit passes without process overhaul.

### Scenario 3: AI-First Startup Selling "Governed AI Development"
**Context:** Startup sells "we build with AI, but it's audited" as a competitive advantage.
**Value:** Digital State becomes a product feature they bundle — their differentiator.

---

## Why Now (Timing)

| Signal | Evidence |
|--------|----------|
| Autonomous agents hitting production | Codex CLI, Claude Code, Hermes Agent all GA/released 2025-2026 |
| Enterprise adoption of AI coding | GitHub Copilot Enterprise, Cursor Enterprise, Sourcegraph Cody |
| Regulatory pressure on AI use | EU AI Act, US Executive Orders, client contractual requirements |
| No incumbent governance layer exists | Search "AI agent governance" → consulting frameworks, not tools |

---

## Value Delivery Architecture

```
Developer / Operator
       │
       ▼
┌─────────────────────────────────────┐
│  digitalstate init                  │  ← 30 sec: workspace + identities + audit log
│  digitalstate register --role=Prime │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Agent starts task                  │  ← Hermes / Codex / Claude Code
│  digitalstate submit --gate=SPEC    │  ← Operator submits spec evidence
│  digitalstate approve --gate=SPEC   │  ← Independent auditor approves
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Immutable audit_log.jsonl          │  ← Cryptographic chain, court-admissible
│  state.json (current phases)        │
└─────────────────────────────────────┘
```

---

## Validation Status

| Claim | Status |
|-------|--------|
| Problem exists | CONFIRMED (self-referential) |
| Problem is painful enough to pay for | UNVALIDATED |
| Digital State solves it (technical) | ✅ RESOLVED — BUG-VAL-001/002/003/004 fixed; full workflow verified end-to-end |
| Users can install independently | ✅ TECHNICAL — clean `pip install` of regenerated wheel works; `doctor`=PASS; both launchers present |
| Users can operate without vendor help | ✅ TECHNICAL — full lifecycle SPECIFICATION→COMPLETED verified via proxy |
| Works across multiple runtimes | UNVALIDATED (Hermes mock only) |
| Onboarding workflow completes | ✅ TECHNICAL PROXY — completed via `scripts/smoke_e2e.py` (see REMEDIATION-EVIDENCE.md) |

**Critical Path:** (1) ✅ Fix BUG-VAL-001/002/003/004 — DONE → (2) External human user validation of every row above remains OPEN (human gate).