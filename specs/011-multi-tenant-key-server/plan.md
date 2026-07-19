# Implementation Plan: Multi-Tenant Key Server Authentication

**Branch**: `011-multi-tenant-key-server` | **Date**: 2026-07-19 | **Spec**: [spec.md](spec.md)

## Summary

Extend Digital State key management and runtime context resolution to support multi-tenant cryptographic identity validation. The architecture introduces tenant namespace scoping (`tenant_id`) in key storage queries, signature validation, and audit logging while maintaining full backward compatibility for single-tenant local operations via `default_tenant`. Preserves `RuntimeStore` as canonical identity authority and `GovernanceKernel` for transition authorization.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: `cryptography`, PyYAML, standard library  
**Storage**: `RuntimeStore` (SQLite / local storage), `.specify/state.json`, audit JSONL logs  
**Testing**: pytest (unit, integration, CLI)  
**Target Platform**: Windows PowerShell, Linux, macOS  
**Project Type**: Python package and CLI with Hermes plugin adapter  
**Performance Goals**: Tenant key lookup completes in < 5ms; verification overhead is negligible  
**Constraints**: No tenant key or signature may authorize actions in another tenant domain; Fail-Safe Default-Deny must block missing/invalid tenant context  

## Constitution Check

| Principle | Plan response | Status |
|---|---|---|
| I. Separation of Governance and Execution | Tenant identity resolution acts strictly within the governance plane without altering Hermes runtime execution logic. | PASS |
| II. Role Segregation | Multi-tenant identities enforce role boundaries per tenant without cross-tenant impersonation. | PASS |
| III. Immutable Accountability | All multi-tenant key authentication results and denials are logged with tenant ID and timestamp. | PASS |
| IV. Gate-Based Progression | Missing or mismatched tenant identity triggers Fail-Safe Deny at the pre-tool-call gate. | PASS |
| V. Independent Verification | Key verification checks signature provenance against tenant public keys in `RuntimeStore`. | PASS |

## Research Decisions

See [research.md](research.md). All technical decisions (tenant namespace isolation, key lookup pipeline, single-tenant fallback, and storage schema) are documented and resolved.

## Project Structure

```text
src/digital_state/
├── core/
├── runtime/
│   ├── adapter.py               # 3-tier lookup pipeline extended for tenant_id
│   └── store.py                 # RuntimeStore identity authority with tenant domain support
├── hermes/plugin.py             # hook governance boundary with tenant context passing
specs/011-multi-tenant-key-server/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── contracts/
│   └── key-server-contract.md
├── quickstart.md
└── tasks.md
```
