# Independent User Validation — Instrumentation Kit

**Authority:** PRIME (Governance)
**Phase:** Product Validation → Independent User Validation
**Date:** 2026-07-17

This kit contains everything needed to run a real external-user validation
session. It is *preparation* for human testing — not a substitute for it.

---

## 1. Recruitment Message

```
Subject: Help validate an open-source AI-agent governance tool (30–60 min, paid?)

Hi — I'm working on Digital State, a local-first governance layer for
autonomous AI coding agents (Hermes, Codex, Claude Code). It gives agents
cryptographic identities, role-segregated approvals (Prime/Builder/Auditor),
and an immutable audit trail — without slowing them down.

I need 2–3 developers to install it from the public repo and run one
governance workflow, on a screen share (or recorded). ~30–60 min. Totally
open to feedback, no prep needed.

You're a fit if you:
- Run Python 3.11+ on Windows/Linux/macOS
- Use or are evaluating AI coding agents
- Have some audit/compliance pain (client asks, SOC2, "who authorized that?")

I'll send you the repo URL + a test key pair so you skip the crypto setup.
Want to help? Reply with your OS and which agent you use.
```

---

## 2. Pre-Session Handoff (what the user receives)

```
1. Repo: https://github.com/samirhosninet/Digital-State
2. README: https://github.com/samirhosninet/Digital-State#readme
3. Test keys: ./test-keys/<role>.pem (private) + <role>.pub.pem (public)
   - prime-agent / builder-agent / auditor-agent
4. Task: "Install and run the governance workflow. Record everything.
         Don't read source code — just the README."
```

---

## 3. Observation Template (observer fills live)

| Timestamp | Event | Friction? (Y/N) | Notes |
|-----------|-------|-----------------|-------|
| 00:00 | User opened README | | |
| 00:30 | Chose Path A | | |
| 01:10 | Ran pip install | | |
| ... | ... | | |

**Per-session summary:**
- OS: ______  Python: ______  Path: A / B
- Time to `doctor` PASS: ______ min
- Time to `digitalstate status` (full lifecycle): ______ min
- "I'm stuck" moments: ______ (timestamps: ______)
- Questions asked: ________________________________________
- Missing docs: ________________________________________
- Completed full workflow: Y / N
- Can explain audit log: Y / N (quote: "______")

---

## 4. Debrief Questionnaire (5 min, async or live)

1. What made you want to try this?
2. What was the single most confusing step?
3. If the audit log were shown to your client/auditor, would it satisfy them? Why/why not?
4. Would you use this on a real project? (1–5)
5. What price would you pay? ($0 / $5 / $20 / $50+ per month)
6. What's missing that would make you adopt it tomorrow?
7. One sentence: what is Digital State, in your words?

---

## 5. Success Scorecard (post-session, per user)

| Metric | Threshold | This User |
|--------|-----------|-----------|
| Install unaided | Y | |
| Workflow complete | Y | |
| doctor ≤ 10 min | Y | |
| Stuck moments ≤ 2 | Y | |
| Explains audit log | Y | |
| Willingness to pay > $0 | ≥1/3 users | |

---

## 6. Aggregate Exit Criteria (Products Validation exit)

| Metric | Minimum | Aggregate |
|--------|---------|-----------|
| Install success (unaided) | 2/3 | __/3 |
| Workflow completion | 2/3 | __/3 |
| Explains audit log | 2/3 | __/3 |
| Willingness to pay > $0 | 1/3 | __/3 |

**EXIT ONLY WHEN all four aggregate thresholds are met.**
```

---
