# Data Model: Hermes Runtime Integration

This document defines the schemas and structures used to pass verification contexts between the Hermes Plugin and the Digital State SDK.

---

## Verification Context Schema

Each hook passes a context dictionary containing signature headers, agent profile information, and the target workspace path:

```json
{
  "feature_id": "feature-abc",
  "agent_key": {
    "key_id": "key-prime",
    "signature": "base64-signature-payload",
    "role": "Prime"
  }
}
```

### Context Resolution Pipeline (ADR-013 / Option E)

Governance context (`feature_id`, `agent_key`) is resolved via `digital_state.runtime.adapter` using a 3-tier lookup pipeline:

1. **Tier 1 (Explicit Context)**: Direct keys passed in the hook invocation dictionary (`context["feature_id"]`, `context["agent_key"]`).
2. **Tier 2 (Process Environment)**: Environment variables set by process invocation (`DS_FEATURE_ID`, `DS_AGENT_KEY`, `HERMES_KANBAN_TASK`, `HERMES_PROFILE`).
3. **Tier 3 (RuntimeStore Authority & Workspace Fallback)**: Active workspace state (`.specify/state.json`) and registered identity records in `RuntimeStore` matching the active `HERMES_PROFILE`.

If identity cannot be authoritatively resolved through any tier, the plugin triggers a Fail-Safe Default-Deny.


---

## Hook Lifecycle Mapping

| Hook Name | Invocation Timing | Purpose | SDK Method Called |
|:---|:---|:---|:---|
| `on_session_start` | Session initiation | Validate caller identity and set active context | `check_governance_status` |
| `pre_llm_call` | Prior to model request | Check prompt/policy permissions | `validate_gate_approval` |
| `post_llm_call` | After model response | Log prompts/responses for trace-completeness | `submit_evidence` |
| `pre_tool_call` | Prior to tool call | Validate execution permissions for target tool | `validate_gate_approval` |
| `post_tool_call` | After tool execution | Log execution evidence and outcomes | `submit_evidence` |
| `on_session_end` | Session completion | Commit final session states | `verify_audit_log` |
