# Auditor Handoff — DS-GOV-BOOTSTRAP-001 Implementation

**Status**: Implementation Complete — Pending Independent Auditor Verification
**Author**: prime profile (implementation phase)
**ADR**: DS-GOV-BOOTSTRAP-001 (accepted architectural decision: Option C)
**Scope**: Runtime Context / Workspace Context separation in `runtime/adapter.py`

---

## 1. Files Modified

| File | Change | ADR / Evidence |
|------|--------|----------------|
| `src/digital_state/runtime/adapter.py` | Change 1: `RuntimeStore(root=ws_root)` → `RuntimeStore()` (uses `resolve_runtime_root()`). Change 2: `feature_id` extracted from inside `feature_states` per `lifecycle.py:55,69-72` schema. | ADR-011-01, ADR-011-04, ADR-013 / Option E; DS-GOV-BOOTSTRAP-001 investigation |
| `tests/integration/test_tenant_isolation.py` | Change 3: `test_tenant_context_resolution_isolation` rewritten to provision the authoritative Runtime at `DIGITAL_STATE_HOME` (independent of workspace) and assert the separation instead of masking the coupling defect. | DS-GOV-BOOTSTRAP-001 Investigation Objective 5 (R1) |

**Not modified** (explicitly out of scope): `hermes/plugin.py`, `runtime/store.py`, `runtime/manifest.py`, `runtime/provision.py`, `runtime/stores.py`, `core/registry.py`, `bootstrap/`, `installer.py`, Hermes integration, all other tests.

> Note: `git status` also shows 5 pre-existing modifications unrelated to this event
> (`.specify/integration.json`, `install.ps1`, `bootstrap/engine/speckit_provisioner.py`,
> `bootstrap/installer.py`, `tests/unit/test_bootstrap.py`). These predate this event
> (bootstrap commits) and are NOT part of this change set.

---

## 2. Repository Diff Summary

```diff
 src/digital_state/runtime/adapter.py:
   # Tier 3a (Workspace Context) — feature_id from .specify/state.json schema
-  feature_id = next(iter(state_data.keys()))
+  feature_states = state_data.get("feature_states", {})
+  if isinstance(feature_states, dict) and feature_states:
+      feature_id = next(iter(feature_states.keys()))

   # Tier 3b (Runtime Context) — identity from authoritative Runtime root
-  store = RuntimeStore(root=ws_root)
+  store = RuntimeStore()   # resolve_runtime_root() => DIGITAL_STATE_HOME / LOCALAPPDATA/digital-state
```

Two lines of behavioral change in `adapter.py` + clarifying comments. One test rewritten to
assert the architectural contract (no behavior change to production code).

---

## 3. Architectural Rationale

The investigation (DS-GOV-BOOTSTRAP-001) proved the Builder bootstrap deadlock was NOT a
plugin defect. The Governance Plugin (`hermes/plugin.py`) correctly denies when handed an
unresolved `(feature_id, agent_key)`. The real defect was in the **Runtime Adapter**
(`runtime/adapter.py`):

- `ws_root` (Workspace Context root) was passed into `RuntimeStore(root=ws_root)`.
- `RuntimeStore` expects its root to be the **Runtime Context root** (`resolve_runtime_root()`
  → `DIGITAL_STATE_HOME` or `LOCALAPPDATA/digital-state`), which is a DIFFERENT, independent
  location from the workspace.
- Because the workspace root does not contain `manifest.json` + `registry/agents.json`,
  `store.exists()` returned `False`, the identity block was skipped, `agent_key` stayed `None`,
  and the plugin correctly denied every tool.

The fix restores the three independent contexts:
- **Workspace Context** (`ws_root`): source of `.specify/state.json` (Tier 3a) and `feature_id`.
- **Runtime Context** (`resolve_runtime_root()`): source of authoritative identity
  (`registry/agents.json`, Tier 3b).
- **Governance Context** (3-tier output): consumed by the plugin unchanged.

This matches the load-bearing separation already required by `tests/conftest.py:75-96`
(autouse `isolate_runtime_home` points `DIGITAL_STATE_HOME` at a private temp dir, independent
of the workspace) and `tests/unit/test_runtime_identity_resolution.py:38-44`.

---

## 4. Test Results (actual captured output)

Command (run against the modified `src/` via `PYTHONPATH`, NOT the stale site-packages copy):
```
cd D:/Digital-State
$env:PYTHONPATH="D:/Digital-State/src"
.venv/Scripts/python.exe -m pytest tests/ -v --tb=short -p no:cacheprovider
```

Result:
```
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\Digital-State
configfile: pyproject.toml
collected 130 items

tests/integration/test_cli_flow.py .                                     [  0%]
tests/integration/test_concurrency.py ...                                [  3%]
tests/integration/test_e2e_release_bootstrap.py .                        [  3%]
tests/integration/test_governance_flow.py .                              [  4%]
tests/integration/test_hermes_flow.py ..                                 [  6%]
tests/integration/test_installation.py .                                 [  6%]
tests/integration/test_story1.py ..                                      [  8%]
tests/integration/test_story2.py ...                                     [ 10%]
tests/integration/test_tenant_isolation.py ..                            [ 12%]   <- new test passes
tests/unit/test_adapter_tenant.py ....                                   [ 15%]
tests/unit/test_bootstrap.py ........                                    [ 21%]
tests/unit/test_bug_val_regressions.py ...                               [ 23%]
tests/unit/test_cli_commands.py .......                                  [ 29%]
tests/unit/test_cryptography.py .....                                    [ 33%]
tests/unit/test_device_cli.py ...                                        [ 35%]
tests/unit/test_device_daemon.py ..                                      [ 36%]
tests/unit/test_device_enrollment.py ....                                [ 40%]
tests/unit/test_device_ledger.py ..                                      [ 41%]
tests/unit/test_device_policy_engine.py ..                               [ 43%]
tests/unit/test_device_sync_client.py .....                              [ 46%]
tests/unit/test_evidence_cli.py ....                                     [ 50%]
tests/unit/test_evidence_device_validator.py ..                          [ 51%]
tests/unit/test_evidence_federation.py ..                                [ 53%]
tests/unit/test_evidence_governance.py .......                           [ 57%]
tests/unit/test_evidence_kernel_bridge.py ...                            [ 60%]
tests/unit/test_foundational.py .....                                    [ 64%]
tests/unit/test_integrity.py ..                                          [ 66%]
tests/unit/test_kernel.py .......                                        [ 71%]
tests/unit/test_layer1_stub.py .                                         [ 72%]
tests/unit/test_layer2_engine_subsystems.py .....                        [ 76%]
tests/unit/test_layer2_lifecycle_commands.py .....                       [ 80%]
tests/unit/test_layer2_manifest_and_lock.py ..                           [ 81%]
tests/unit/test_layer3_runtime_isolation.py ..                            [ 83%]
tests/unit/test_ledger_chaining.py ...                                   [ 85%]
tests/unit/test_negative_crypto.py .....                                 [ 89%]
tests/unit/test_planning.py .                                            [ 90%]
tests/unit/test_plugin.py ....                                           [ 93%]   <- fail-closed preserved
tests/unit/test_recovery.py ..                                           [ 94%]
tests/unit/test_registry.py ..                                           [ 96%]
tests/unit/test_runtime_identity_resolution.py ..                        [ 97%]   <- separation contract
tests/unit/test_sdk.py ..                                                [ 99%]
tests/unit/test_verification.py .                                        [100%]

======================= 130 passed in 156.81s =======================
```

Category coverage achieved:
- Unit tests: PASS (lifecycle, kernel, registry, adapter tenant, plugin, sdk, runtime identity, layer3 isolation, etc.)
- Integration tests: PASS (cli_flow, concurrency, e2e_release_bootstrap, governance_flow, hermes_flow, installation, story1/2, tenant_isolation)
- Bootstrap tests: PASS (`test_bootstrap.py`, `test_installation.py`, `test_e2e_release_bootstrap.py`)
- Governance tests: PASS (`test_governance_flow.py`, `test_plugin.py`, `test_evidence_governance.py`)
- Runtime identity tests: PASS (`test_runtime_identity_resolution.py`, `test_tenant_isolation.py`)
- Repository regression tests: PASS (full suite, no pre-existing test broken)

---

## 5. Regression Analysis

- Full suite 130 → 130 passed (0 regression).
- `test_plugin.py::test_plugin_hooks_fail_safe_deny` still asserts DENY on unresolved context — plugin
  fail-closed path unchanged.
- `test_runtime_identity_resolution.py` (authority-divergence + workspace-fallback) still passes —
  Runtime-first identity authority preserved.
- `test_adapter_tenant.py` (Tier 1/2 resolution) still passes — 3-tier pipeline intact.
- No change to `RuntimeStore`, `manifest.py`, `provision.py`, `stores.py`, `registry.py`, `plugin.py`.

---

## 6. Security Analysis

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Fail-Closed | PRESERVED | Simulated empty Runtime → `resolve_governance_context` returns `(None, None)` → plugin `pre_tool_call_handler` returns `block`. |
| No identity spoofing | PRESERVED | Identity sourced from authoritative Runtime `IdentityStore` (`registry/agents.json`), never from workspace. |
| No governance bypass | PRESERVED | Plugin enforcement path (`plugin.py:163-202`) untouched; still queries `validate_gate_approval`. |
| No temporary disabling | PRESERVED | No "bootstrap allow" switch introduced. |
| No hardcoded keys | PRESERVED | No key material added to code. |
| No plugin removal | PRESERVED | `digital_state` plugin remains enabled in builder profile. |

Runtime-resolution simulation (real `LOCALAPPDATA/digital-state` containing `builder-agent`):
```
feature_id = feat-009
agent_key.role = Builder
agent_key.key_id = key-builder
RESOLUTION SUCCESS
```
→ Builder now resolves identity + feature from the authoritative, independent Runtime, then the
plugin runs normal `validate_gate_approval`. No lingering permissive mode.

---

## 7. Backward Compatibility Analysis

- **Runtime provisioned at `DIGITAL_STATE_HOME`** (existing installs): unchanged — the fix reads
  the same canonical root `resolve_runtime_root()` already used by `provision.py:105`,
  `cli.py:222`, `registry.py:96`.
- **Workspace `.specify/state.json`**: now read per the EXISTING canonical schema
  (`lifecycle.py:55,69-72`). Any state file written by `LifecycleEngine` (the only writer) is
  already in this shape; no migration needed.
- **Legacy `.specify/agents.json` / `.specify/keys/`**: still only consulted as secondary/legacy
  fallback per `registry.py:85-94` — unaffected.
- **Env-var driven resolution (DS_FEATURE_ID / DS_AGENT_KEY / HERMES_KANBAN_TASK)**: Tier 1/2
  unchanged.
- **CI** (`governance-ci.yml` runs `pip install -e .` then `pytest`): the editable install will
  pick up `src/` automatically; no CI change required.

---

## 8. Remaining Risks

| # | Risk | Likelihood | Mitigation / Auditor action |
|---|------|-----------|------------------------------|
| R1 | A session runs with `DIGITAL_STATE_HOME` pointed at a path whose Runtime was never provisioned (no `registry/agents.json`). | Low (default `LOCALAPPDATA/digital-state` is provisioned) | Verify provisioning in target environment; fail-closed still protects. |
| R2 | If a future change re-couples `ws_root` into `RuntimeStore`, the defect returns silently. | Low | `test_tenant_context_resolution_isolation` now asserts the independent roots; add a CI guard if desired. |
| R3 | `site-packages` copy of `digital_state` (stale, `RuntimeStore(root=ws_root)`) is what some environments import. | Medium | Ensure deployment uses `pip install -e .` (src) or reinstalls from the fixed `src/`. The fix is verified only against `src/`. |
| R4 | Builder's `pre_tool_call_handler` now resolves identity → it will call `validate_gate_approval`. If the builder profile's gate policy denies a tool, that is correct governance, not a regression. | N/A (expected) | Auditor should confirm policy allows builder's legitimate read-only repo inspection. |

---

## 9. Auditor Verification Checklist

- [ ] `git diff` shows only `adapter.py` + `test_tenant_isolation.py` changed by this event.
- [ ] `adapter.py:84` is `RuntimeStore()` (no `root=ws_root`).
- [ ] `adapter.py:70` reads `feature_states` (not top-level key).
- [ ] Full suite: `pytest tests/` → 130 passed.
- [ ] `test_plugin_hooks_fail_safe_deny` still passes (fail-closed intact).
- [ ] Run against `src/` (editable install), not stale `site-packages`.
- [ ] On target host: `DIGITAL_STATE_HOME` Runtime contains `builder-agent` (Active).
- [ ] Builder session can now `read_file` / `search_files` / `terminal` (exit criteria met) while
      mutating tools remain gated by `validate_gate_approval`.

**Declaratory close**: Implementation Complete — Pending Independent Auditor Verification.
No code is considered production-ready until the Auditor independently verifies conformance to
ADR DS-GOV-BOOTSTRAP-001 and absence of governance regressions.
