# Implementation Plan: Production Trust Hardening

**Branch**: `009-production-trust-hardening` | **Date**: 2026-07-16 | **Spec**: [spec.md](spec.md)

## Summary

Replace insecure compatibility behavior with strict cryptographic identity validation, make runtime status evidence-based, fail closed on integrity discrepancies, make recovery explicit and preserved, and add a reproducible release gate that proves public user journeys. The change is intentionally a production-trust boundary: legacy plaintext authorization is not migrated silently.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: `cryptography`, PyYAML, standard library  
**Storage**: Workspace-local JSON and JSONL files; preserved recovery snapshots; generated release evidence  
**Testing**: pytest with unit, integration, CLI, and clean-environment subprocess tests  
**Target Platform**: Windows PowerShell first; Linux/macOS shell installation path remains supported  
**Project Type**: Python package and CLI with Hermes plugin adapter  
**Performance Goals**: Identity and integrity checks complete before a governance mutation; release gate emits a complete result within the CI job timeout  
**Constraints**: No acceptance path may rely on a plaintext signing key; unsupported or unavailable Hermes must never be reported live; recovery must not delete or overwrite evidence without explicit input  
**Scale/Scope**: Local workspaces, three governed roles, one package artifact, and an auditable release bundle per validation run

## Constitution Check

| Principle | Plan response | Status |
|---|---|---|
| I. Separation of Governance and Execution | The adapter reports and enforces governance decisions without treating simulated execution as live control. | PASS |
| II. Role Segregation | Identity and approval rules prohibit role impersonation and self-approval. | PASS |
| III. Immutable Accountability | Every denial, recovery, and release decision receives a verifiable record; local storage limitations are documented truthfully. | PASS |
| IV. Gate-Based Progression | Integrity, identity, runtime attestation, and release checks are mandatory gates. | PASS |
| V. Independent Verification | Approval provenance is tracked so the submitting actor cannot validate their own governed artifact. | PASS |

## Research Decisions

See [research.md](research.md). All implementation unknowns are resolved there: identity migration, audit trust boundary, runtime classification, recovery semantics, and release-environment validation.

## Project Structure

```text
src/digital_state/
├── cli/cli.py                    # public commands, diagnostics, recovery
├── core/
│   ├── audit.py                  # hash-chain and state consistency checks
│   ├── engine.py                 # mutation orchestration and provenance
│   ├── evidence.py               # strict signature verification
│   ├── registry.py               # cryptographic identity lifecycle
│   ├── recovery.py               # explicit preserved recovery workflow
│   └── verifier.py               # supported algorithm/key validation
├── hermes/plugin.py              # hook governance boundary
└── sdk/api.py                    # safe authorization and runtime helpers
integrations/hermes/client.py     # runtime attestation and mode classification
scripts/release_gate.py           # repeatable release evidence generator
tests/unit/                       # identity, integrity, recovery tests
tests/integration/                # CLI, Hermes, and clean-environment journeys
specs/009-production-trust-hardening/
```

**Structure Decision**: Retain the existing single Python package. Add focused core services rather than embedding security policy in CLI handlers or plugin hooks.

## Complexity Tracking

No constitutional violations require justification.
