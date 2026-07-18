# Product Positioning

**Status:** DRAFT — awaiting market validation  
**Date:** 2026-07-17  
**Authority:** PRIME (Governance)  
**Phase:** Product Validation

---

## Positioning Statement

> **For developers and teams running autonomous AI coding agents who need to
> prove their agents acted with proper authorization, Digital State is a
> local-first, cryptographic governance layer that provides immutable audit
> trails and role-segregated approvals — without blocking agent velocity or
> requiring infrastructure.**

---

## Category Definition

**Category Name:** *Agent Governance Platform* (new category)

**Category Definition:** Software that provides identity, authorization, audit,
and policy enforcement for autonomous AI agents operating in software
development workflows.

**Why a new category?** Existing categories don't fit:
- ❌ "DevSecOps" — implies CI/CD, infrastructure, enterprise scale
- ❌ "AI Safety" — implies model alignment, not operational governance
- ❌ "Code Review Tools" — human-centric, not agent-native
- ❌ "Policy Engines" — generic, no agent identity model, no audit chaining

---

## Competitive Landscape (Mental Model)

```
                          HIGH GOVERNANCE
                                   │
                    ┌────────────────┼────────────────┐
                    │                │                │
            Enterprise GRC      Digital State      LangChain
              (ServiceNow,           (this)           Guardrails
               AuditBoard)                             
                    │                │                │
                    │                │                │
         ───────────┼────────────────┼────────────────┼───────────
                    │                │                │
                    │                │                │
              GitHub Branch       Pre-commit       Custom
              Protection            hooks           scripts
                    │                │                │
                    ▼                ▼                ▼
                          LOW GOVERNANCE
                                   │
                    ┌────────────────┼────────────────┐
                    │                │                │
              HIGH VELOCITY      MEDIUM            LOW VELOCITY
                    │                │                │
                    ▼                ▼                ▼
```

**Digital State's Position:** *High Governance + High Velocity + Zero Infrastructure*

---

## Target Market Segmentation

### Primary Beachhead: "AI-Native Solo/Team Developers"
- **Size:** ~500K–2M developers (Hermes, Codex, Claude Code, Cursor users)
- **Characteristics:** Technical, early adopters, feel the pain directly
- **Budget:** $0–50/mo (individual), $100–500/mo (team)
- **Buying trigger:** Client asks for audit trail, compliance requirement, or
  agent incident

### Secondary: "AI-First Startups" (Seed–Series A)
- **Size:** ~5K–20K companies
- **Characteristics:** Building with agents, selling to enterprise, need
  compliance story
- **Budget:** $500–5K/mo
- **Buying trigger:** Enterprise prospect asks "how do you govern your AI?"

### Tertiary: "Regulated Industry Teams" (FinTech, HealthTech, GovTech)
- **Size:** Large but slow-moving
- **Characteristics:** Already have GRC tools; need agent-specific layer
- **Budget:** $10K–100K/yr
- **Buying trigger:** Audit finding or regulatory guidance on AI

---

## Differentiation Matrix

| Dimension | Digital State | Enterprise GRC | CI/CD Gates | Custom Scripts |
|-----------|---------------|----------------|-------------|----------------|
| **Agent-native identity** | ✅ | ❌ | ❌ | ⚠️ DIY |
| **Role segregation (Prime/Builder/Auditor)** | ✅ | ⚠️ Human only | ❌ | ❌ |
| **Cryptographic audit chain** | ✅ | ✅ | ❌ | ❌ |
| **Local-first, zero infra** | ✅ | ❌ | ❌ (cloud) | ✅ |
| **Runtime agnostic** | ✅ | ❌ | Platform-locked | ✅ |
| **Evidence-gated (not blocking)** | ✅ | ❌ | ❌ (blocking) | ❌ |
| **Time to first value** | < 5 min | Weeks | Hours | Days |
| **Cost** | Free (OSS) / Low | $50K+/yr | Included | Dev time |

---

## Messaging by Audience

### For Solo Developers
> **"Prove your AI didn't go rogue — in 3 commands."**
> `digitalstate init` → `digitalstate submit` → `digitalstate approve`
> Immutable audit trail. No server. No subscription.

### For Team Leads
> **"Governance that doesn't slow down your agents."**
> Role-segregated approvals. Cryptographic evidence. Works with Hermes,
> Codex, Claude Code. Deploy in your repo, not your cloud.

### For Founders (AI-First Startups)
> **"Your enterprise compliance story for AI-generated code."**
> Bundle Digital State in your delivery. Show prospects the audit log.
> Close deals faster with "we have governance built-in."

### For Compliance Officers
> **"AI agent actions — finally auditable."**
> Immutable hash-chained log. Role-based authorization. Exportable evidence
> package. SOC2/GDPR ready.

---

## Pricing Hypothesis (For Validation)

| Tier | Target | Price | Includes |
|------|--------|-------|----------|
| **Community** | Solo, OSS, hobby | Free | Core CLI, SDK, Runtime, all agents |
| **Team** | 2–10 devs | $20/seat/mo | Shared policy, centralized audit view, SSO |
| **Enterprise** | 10+ devs, regulated | $5K–25K/yr | Dedicated support, SLAs, custom policies, on-prem |

**Validation needed:** Will *anyone* pay? At what price? For what features?

---

## Go-to-Market Hypothesis

### Phase 1: Community-Led (Months 0–6)
- Open source core (MIT/Apache 2.0)
- Hermetic install: `pip install git+https://...`
- Content: "How I govern my AI agents" blog posts, tutorials
- Discord/Slack community for early adopters
- **Goal:** 100 active users, 10 external contributors

### Phase 2: Team Adoption (Months 6–18)
- Team tier with shared policy/audit view
- IDE extensions (VS Code, Cursor)
- Agent runtime plugins (Codex, Claude Code official)
- **Goal:** 500 teams, $10K MRR

### Phase 3: Enterprise (Months 18+)
- SSO, SCIM, audit export, compliance reports
- Professional services / managed offering
- **Goal:** 20 enterprise contracts, $1M ARR

---

## Risks to Positioning

| Risk | Mitigation |
|------|------------|
| "Governance" sounds heavy/enterprise | Lead with "audit trail" / "prove it" language |
| "Another tool to learn" | 3-command workflow; SDK for automation |
| "Only works with Hermes" | Document/verify multi-runtime support |
| "OSS = no moat" | Runtime + SDK + plugin ecosystem = platform moat |
| "AI agents will build their own governance" | Agents *can't* govern themselves (conflict of interest) |

---

## Validation Questions for Market

1. **Category recognition:** Do users search for "agent governance"? What terms do they use?
2. **Pain language:** How do they describe the problem? (Our words vs. theirs)
3. **Willingness to pay:** At what price does "free" become suspicious vs. "worth it"?
4. **Integration priority:** Hermes first? Codex? Claude Code? Custom?
5. **Team vs. individual:** Who champions adoption? Who pays?
6. **Compliance driver:** Is it proactive ("we want to be ready") or reactive ("auditor asked")?

---

## Positioning Statement (Final — Post-Validation)

> *[To be finalized after validation phase]*

---

## Appendix: Positioning Test Artifacts

### Homepage Hero (Hypothesis)
> **Digital State — Governance for Autonomous AI Agents**  
> *Prove what your agents did. Approve what they'll do. Ship with confidence.*  
> `[Try in 3 commands]` `[Read the architecture]` `[Join Discord]`

### One-Liner for Twitter/LinkedIn
> "Digital State gives AI coding agents a government — identities, roles,
> approvals, and an immutable audit trail. Local-first. Zero infra. Works with
> Hermes, Codex, Claude Code."

### Elevator Pitch (30 seconds)
> "You're using AI agents to write code. Great. But when your client or auditor
> asks 'who approved this change?' — you have no answer. Git shows who
> committed. It doesn't show which agent acted, which role authorized it, or
> whether policy was followed. Digital State adds a cryptographic governance
> layer: register your agents with roles (Prime, Builder, Auditor), submit
> evidence at each gate, get independent approvals, and produce an
> unforgeable audit log. It installs with pip, runs locally, works with any
> agent runtime, and adds 30 seconds per feature gate. Teams use it to sell
> 'governed AI development' to enterprise. Solo devs use it to prove they
> didn't just 'let the AI run wild.'"