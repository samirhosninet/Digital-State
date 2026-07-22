# Feature Specification: Event 014 — Adapter Fix Verification under ADR-0001

**ID**: `014-adapter-fix-verification`  
**Governing Architecture**: ADR-0001  
**Status**: OPEN  

## Functional Requirements
1. `src/digital_state/runtime/adapter.py` must instantiate `RuntimeStore()` using default `resolve_runtime_root()`, ensuring identity lookup targets `DIGITAL_STATE_HOME` / `%LOCALAPPDATA%\digital-state`.
2. `.specify/state.json` must be queried for `feature_id` from `feature_states` per canonical schema.
3. Fail-closed security in `hermes/plugin.py` must remain uncompromised.
4. Independent verification by the Auditor profile must be executable against an authorized Runtime Context.
