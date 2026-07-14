# Research: Hermes Runtime Integration

## Decision 1: Stateless Hook Interception & Delegation
* **Decision**: Implement all six hooks in `digital_state.hermes.plugin` as stateless pass-through functions that query the SDK.
* **Rationale**: Keeps the plugin footprint extremely light and ensures all policy enforcement logic is centralized in the core SDK.
* **Alternatives Considered**:
  - Local caching in the plugin: Rejected because it violates the statelessness invariant and risks stale policy data.

## Decision 2: Simulated Integration Test Harness
* **Decision**: Upgrade `HermesClient` in `integrations/hermes/client.py` to act as an in-memory test harness running a simulated event loop.
* **Rationale**: Allows full integration testing of the plugin hooks, session starts, and SDK compliance checks without a live external server.
* **Alternatives Considered**:
  - Socket-based server mock: Rejected as overly complex and error-prone for local CI environments.

## Decision 3: Event Context Mapping
* **Decision**: Map session context inputs (such as agent key metadata and workspace paths) to the standard payload maps accepted by `validate_gate_approval`.
* **Rationale**: Direct parameter mapping avoids dependencies on complex serialization classes.
