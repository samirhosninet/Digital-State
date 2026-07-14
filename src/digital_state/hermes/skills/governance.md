# Digital State Governance Playbook

This playbook outlines the automated governance rules enforced by the Digital State Integration.

## Operational Rules

1. **Verify State Before Action:** The agent must verify that the target feature lifecycle state matches the intended gate before proposing modifications.
2. **Submit Verifiable Evidence:** To transition gates, the agent must submit evidence containing a valid cryptographic signature matching the agent's identity.
3. **No Overrides:** Standard tools are blocked at the execution boundary unless explicitly signed off by a governance authority.
