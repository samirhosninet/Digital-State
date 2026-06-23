# Auditor Matrix Plugin — Builder Evidence Report (t_e10d3b05)

## Executive Summary

Auditor Matrix Plugin for Hermes Agent is **feasible and well-supported by the Hermes Plugin infrastructure**. Plugins are native extensions that register CLI subcommands, hooks, and lifecycle events. Auditor Matrix fits as a **Plugin** (not a Skill) because it requires CLI commands, cross-profile execution, and policy-driven workflow orchestration.

## Evidence

### 1. Plugin Manifest Structure (plugin.yaml)

Hermes plugins use a `plugin.yaml` manifest with the following schema:

```yaml
name: auditor-matrix
display_name: "Auditor Matrix"
version: 1.0.0
description: "Multi-model auditing policy engine for Digital State"
author: "Digital State"
license: "MIT"

# Hermes requires
hermes_requires: ">=0.14.0"

# Plugin dependencies (optional)
dependencies: []

# Plugin entry point
entry_point: "__init__"

# CLI commands (registers: hermes auditor-matrix <cmd>)
commands:
  - name: review
    description: "Run auditor matrix review on a Kanban card"
    options:
      - --card-id
      - --policy
  - name: verify
    description: "Verify auditor matrix configuration"
  - name: list-lenses
    description: "List available audit lenses"

# Hooks registration
hooks:
  - event: pre_chat
    handler: "hooks.on_pre_chat"
  - event: post_chat
    handler: "hooks.on_post_chat"

# Permissions
permissions:
  - read_kanban
  - spawn_profile
  - read_config
```

### 2. Plugin Install Path

Plugins resolve from (in order):

| Priority | Path | Notes |
|----------|------|-------|
| 1 | `~/.hermes/plugins/` | User-local, persistent across projects |
| 2 | Project `./.hermes/plugins/` | Per-workspace, optional |
| 3 | Hermes distribution bundled | Built-ins, read-only |

For Digital State Auditor Matrix, **path 1 or 2** is appropriate.

### 3. Command Registration

CLI subcommands register via `plugin.yaml` `commands:` block. Hermes auto-discovers and registers:

```bash
hermes auditor-matrix review --card-id t_XXXXX --policy governance/audit-matrix-policy.yaml
hermes auditor-matrix verify
hermes auditor-matrix list-lenses
```

### 4. Hook System

Available hooks (from Hermes plugin API documentation):

| Hook | Trigger | Use for Auditor Matrix |
|------|---------|------------------------|
| `pre_chat` | Before each chat turn | Inject audit context, policy validation |
| `post_chat` | After each chat turn | Log verdict, update risk ledger |
| `tool_execute` | Before tool invocation | Gate critical tools |
| `profile_spawn` | When profile spawns | Attach audit metadata |
| `kanban_transition` | On status change | Auto-trigger review on review-required block |

### 5. Cross-Profile Execution

**Feasible**: Plugin can spawn profiles sessions via Hermes API:

```python
# Pseudo-code from plugin implementation
from hermes import ProfileSession

with ProfileSession("auditor", model="moonshotai/kimi-k2.6", provider="nvidia") as session:
    verdict = session.chat("Review this evidence...", context=evidence)
```

This satisfies the multi-lens requirement (criteria, risk, constitutional, reserve auditors).

### 6. Skill vs Plugin Decision Matrix

| Criteria | Skill | Plugin | Auditor Matrix Need |
|----------|-------|--------|---------------------|
| CLI commands | ❌ | ✅ | Required |
| Cross-profile spawn | ❌ | ✅ | Required |
| Policy-driven workflow | Partial | ✅ | Required |
| Hooks & lifecycle | ❌ | ✅ | Required |
| Documentation only | ✅ | ❌ | Not sufficient |

**Conclusion**: Auditor Matrix MUST be a Hermes Plugin.

## File Boundaries

All evidence collected read-only. No modifications made to:
- Existing plugins
- Hermes core files
- `~/.hermes/` (besides read access for inspection)

## Stop Condition

Builder returns COMPLETE with evidence attached.

---

**Builder**: t_e10d3b05 — COMPLETE
