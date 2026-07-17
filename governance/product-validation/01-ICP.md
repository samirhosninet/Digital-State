# Initial Customer Profile (ICP)

**Status:** DRAFT — awaiting real-world validation  
**Date:** 2026-07-17  
**Authority:** PRIME (Governance)  
**Phase:** Product Validation

---

## Primary ICP

### Profile: The Autonomous Agent Operator

**Who they are:** An individual developer, team lead, or DevOps engineer who runs
or plans to run one or more autonomous AI coding agents (Hermes Agent, Claude
Code, Codex CLI, OpenCode, or similar) in production development workflows.

**What they do:**
- Delegate real coding tasks to AI agents — feature implementation, bug fixes, PRs
- Operate in repositories with compliance, security, or audit requirements
- Need to prove that agent actions were authorized and reviewed
- Run on self-hosted machines (Windows/Linux workstations or servers)
- Currently use ad-hoc "manual review" → "merge" workflows with no audit trail

**Team size:** 1–10 developers
**Budget:** Individual ($0–50/mo for tools) to small team (existing infra)

**Technical sophistication:** High — comfortable with CLI, git, Python, package
managers (pip/uv), YAML config, and basic cryptography concepts.

**Current pain:**
- "Did the agent really have permission to write that file?"
- "How do I prove to my client/auditor that our AI-generated code was reviewed?"
- "I have 3 agents working on different repos and I can't track who did what"
- "We want to use AI agents but our compliance team says we need governance first"

---

## Secondary ICPs

### 2. Compliance-Conscious Freelancer
Freelance developer using AI agents who needs to demonstrate to clients that
agent-generated code passed governance gates.

### 3. AI Startup (Seed/Pre-Seed)
Small team (2–8) shipping AI-native products who want to prove to investors and
early enterprise customers that their AI development process is auditable.

### 4. Open-Source Maintainer
Maintainers of projects that accept AI-generated PRs and need lightweight
governance to validate contributions were authorized.

---

## Anti-ICP (who this is NOT for)

- Users with no CLI experience (GUI-only devs)
- Teams already using full compliance suites (SOC2, HIPAA) — Digital State is
  too lightweight for enterprise compliance
- Users who don't currently run AI coding agents (no pain point)
- Large enterprises ( require commercial support, SLAs, SSO, etc.)
- Non-technical stakeholders requiring dashboards (Digital State is
  CLI + JSON audit trail — no GUI)

---

## First Real User Candidate

**User:** `I-Master` (repository owner, current operator)
**Status:** Power user and developer — not an independent external user

**Feed for first real user:** None identified yet — this is the core validation
gap.

---

## Next Steps

1. Identify 1–2 real external testers who fit the primary ICP
2. Have them install Digital State independently (Path A or B from README)
3. Document their experience (installation time, confusion points, errors)
4. Validate they understand the value proposition