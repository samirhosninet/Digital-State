# Problem Statement

**Status:** DRAFT — awaiting user validation  
**Date:** 2026-07-17  
**Authority:** PRIME (Governance)  
**Phase:** Product Validation

---

## The Problem in One Sentence

> **Developers running autonomous AI coding agents have no way to prove their
> agents acted with proper authorization — creating compliance risk, audit gaps,
> and trust barriers to adoption.**

---

## Problem Decomposition

### 1. The Authorization Gap
- **What happens:** An AI agent (Hermes, Claude Code, Codex, OpenCode) writes
  code, modifies files, runs commands, creates PRs.
- **What's missing:** Cryptographic proof that the agent *was authorized* to do
  that specific action at that specific time by the right role.
- **Current state:** Git shows *who* committed. It doesn't show *which agent*
  acted, *which role* approved it, or *whether* the action matched policy.

### 2. The Audit Trail Vacuum
- **Compliance asks:** "Show me the approval chain for this AI-generated code."
- **Teams answer:** "Uh... there's a PR review?" or "We trust the developer."
- **Reality:** No immutable, queryable, cryptographically verifiable audit trail
  exists for agent actions.

### 3. The Governance-Velocity Tradeoff
| Approach | Governance | Velocity |
|----------|------------|----------|
| Manual PR review for every agent action | ✅ High | ❌ Slow |
| Pre-commit hooks / CI gates | ✅ Medium | ❌ Blocks agent |
| Trust-but-verify (merge first, audit later) | ❌ None | ✅ Fast |
| **Digital State (evidence-gated)** | ✅ High | ✅ Fast |

**The false choice:** Teams believe they must choose between governance and
speed. They don't — they need *evidence-gated* governance, not *execution-blocking* governance.

### 4. The Infrastructure Barrier
- Existing governance tools (OPA, Gatekeeper, ServiceNow, AuditBoard) require:
  - Servers / Kubernetes
  - Databases
  - SSO / identity providers
  - Dedicated DevOps maintenance
- **Result:** Individual developers and small teams *cannot adopt* governance.
  They either go without or build brittle custom scripts.

### 5. The Agent Identity Crisis
- Agents have no standard identity model.
- No role-based permissions for agents (Prime/Builder/Auditor).
- No key rotation, no revocation, no delegation model.
- Each agent runtime invents its own (or has none).

---

## Who Feels This Pain

| Persona | Pain Manifestation |
|---------|-------------------|
| **Solo dev using Hermes** | "I can't prove to my client the AI didn't go rogue" |
| **Team lead with 3 agents** | "I have no central view of what agents did across repos" |
| **Freelancer delivering AI-assisted work** | "Client asks for audit trail — I send screenshots" |
| **Startup selling AI-generated code** | "Enterprise prospect asks for SOC2 evidence for AI pipeline" |
| **Open source maintainer** | "Bot PRs merged — who authorized the bot? The maintainer who slept?" |

---

## Why Existing Solutions Fail This Problem

| Solution | Why It Fails |
|----------|--------------|
| **Git signed commits** | Signs *commits*, not *agent actions*; no roles, no gates, no policy |
| **GitHub branch protection** | Cloud-only; human-centric; blocks rather than audits |
| **Pre-commit hooks** | Runs locally; no crypto identity; no audit log; easily bypassed |
| **CI/CD gates** | Blocks execution; slow; no agent identity model |
| **Enterprise GRC** | $50k+/yr; requires infra; built for humans, not agents |
| **LangChain guardrails** | Runtime only; no persistence; no human governance roles |
| **Custom scripts** | Brittle; no crypto; not portable; bus factor = 1 |

---

## The Cost of Not Solving This

1. **Adoption blocker:** Enterprises won't allow AI agents without governance
2. **Compliance failures:** Auditors will flag "uncontrolled AI code generation"
3. **Trust erosion:** High-profile agent incident → industry backlash
4. **Legal liability:** Who's responsible when an agent deletes production data?
5. **Competitive disadvantage:** Teams with governance ship AI-assisted code
   confidently; teams without hesitate

---

## Problem Validation Criteria

| Hypothesis | Validation Method | Success Threshold |
|------------|-------------------|-------------------|
| Devs *feel* this pain | 10+ ICP interviews | ≥ 7/10 rate it "significant" or "critical" |
| Devs *act* on this pain | Search volume, forum posts | "AI agent audit trail" → measurable queries |
| Devs *pay* for solution | Pricing conversations | ≥ 3/10 willing to pay >$0 |
| Current workarounds *fail* | Observe workaround attempts | Custom scripts break, git logs insufficient |

---

## Current Evidence (Internal)

| Evidence | Strength | Gap |
|----------|----------|-----|
| SPEC-009/012 governance specs exist | Strong technical definition | No external validation |
| 47/47 tests pass | Strong technical quality | Tests ≠ user need |
| README documents installation | Good DX intent | No user tested it |
| Architecture supports standalone | Proven in code | No external user confirmed |

---

## Next Steps

1. **Conduct 5–10 ICP interviews** using the interview guide in `01-ICP.md`
2. **Search for existing discussions** on Reddit, Discord, GitHub Issues about
   "AI agent governance," "AI code audit trail," "prove agent was authorized"
3. **Run landing page smoke test** with problem-focused copy
4. **Update this document** with validated problem statements in user language

---

## Problem Statement (Validated Version — TBD)

> *[To be filled after validation phase-gpt-5 TO FILL AFTER USER RESEARCH ]*