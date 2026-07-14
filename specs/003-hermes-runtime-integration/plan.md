# Implementation Plan: Hermes Runtime Integration

**Branch**: `003-hermes-runtime-integration` | **Date**: 2026-07-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/003-hermes-runtime-integration/spec.md`

## Summary
The goal of this feature is to verify the Digital State framework as a runtime governance layer operating inside a real Hermes Agent environment. The technical approach involves expanding the stateless plugin façade to support the full range of Hermes runtime hooks, upgrading the local client integration mock to run simulated execution loops, and verifying policy checks under simulation.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: `cryptography`

**Storage**: Local files (`state.json`, `audit.jsonl`)

**Testing**: `pytest`

**Target Platform**: Windows, Linux, macOS

**Project Type**: library/cli/plugin

**Performance Goals**: Hook interception latency < 10ms; compatibility checks < 5ms

**Constraints**: Offline-first, stateless plugin bridge

**Scale/Scope**: 6 lifecycle hooks, up to 10 agent profiles

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The design and planning artifacts comply with the **Digital State Constitution v1.2.0**:
* **Separation of Governance and Execution**: The plugin intercepts hooks but delegates all decisions to the SDK. Execution remains strictly within Hermes. (✅ Pass)
* **Role Segregation**: Identity checks in the hook context verify active profile permissions. (✅ Pass)
* **Immutable Accountability**: Every intercepted action and validation decision is recorded in `audit.jsonl`. (✅ Pass)
* **Gate-Based Progression**: Verification checks validate transitions against gate rules. (✅ Pass)
* **Independent Verification**: Validation blocks self-verifications and unauthorized actions. (✅ Pass)
* **Verifiable Identity**: Verification contexts require valid cryptographic agent keys. (✅ Pass)

## Project Structure

### Documentation (this feature)

```text
specs/003-hermes-runtime-integration/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── checklists/          # Verification checklist
    └── requirements.md
```

### Source Code (repository root)

```text
src/
└── digital_state/
    ├── core/            # Core validation engines
    ├── sdk/             # Core SDK interface
    ├── cli/             # CLI Parser
    └── hermes/          # stateless plugin bridge
        ├── __init__.py
        ├── plugin.py    # Expanded plugin lifecycle hooks
        └── skills/
            └── governance.md

integrations/
└── hermes/
    ├── __init__.py
    ├── client.py        # Simulated loop runtime client
    └── README.md

tests/
├── unit/
│   ├── test_sdk.py
│   └── test_plugin.py   # Unit tests for hook handlers
└── integration/
    ├── test_cli_flow.py
    └── test_hermes_flow.py # Simulated session integration loop
```

**Structure Decision**: Option 1 (Single project). Standardized single-package structure ensures version compatibility across Core, SDK, and Plugin.

## Complexity Tracking

No violations of the Constitution exist in this plan; therefore, no complex overrides or justifications are required.
