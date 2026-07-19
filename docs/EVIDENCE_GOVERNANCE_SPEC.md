# Specification: Evidence Governance Framework (v1.12.0-evidence)

- **Document ID**: `EVIDENCE_GOVERNANCE_SPEC.md`
- **Package**: `digital_state.governance.evidence`
- **Target Release**: `v1.12.0-evidence`
- **Status**: OFFICIAL SPECIFICATION

---

## 1. Overview

The **Evidence Governance Framework** is a reusable infrastructure component inside Digital State. It establishes canonical evidence taxonomies, rules-based validation engines, and dual-format report generators to ensure that all architectural claims, security reviews, and release certifications remain 100% evidence-backed, reproducible, and machine-verifiable.

---

## 2. Canonical Evidence Classifications

All evidence records must be classified as exactly one of the following:

1. **`VERIFIED`**: Positive evidence directly demonstrates the statement via implementation code, official documentation, or specifications.
2. **`VERIFIED ABSENCE`**: An authoritative specification (e.g. PyPA PEP 427) or negative code check explicitly proves non-existence. (Documentation silence is **prohibited** from being classified as `VERIFIED ABSENCE`).
3. **`NOT FOUND IN CURRENT OFFICIAL DOCUMENTATION`**: Inspected official documentation does not describe the feature or capability. (This represents absence of documentation, not proof of impossibility).
4. **`UNVERIFIED`**: Insufficient evidence is available to reach a definitive conclusion.

---

## 3. Boundary Taxonomies

1. **`Digital State Repository`**: Features and code implemented within `D:\Digital-State`.
2. **`Hermes Agent Framework`**: Framework hooks, plugins, and CLI interfaces documented by upstream Hermes Agent (`https://github.com/nousresearch/hermes-agent`).
3. **`Python Packaging Specification`**: Python packaging standards (e.g. PEP 427 Wheel Binary Format).
4. **`External Platform Behavior`**: Host OS or Desktop runtime behaviors outside local repository scope.

---

## 4. Mandatory Invariant Rules

- **Rule 1 (Absence Spec Guard)**: `VERIFIED_ABSENCE` requires `AUTHORITATIVE_SPECIFICATION` or `REPOSITORY_IMPLEMENTATION`. Silence in documentation automatically degrades to `NOT_FOUND_IN_CURRENT_OFFICIAL_DOCUMENTATION`.
- **Rule 2 (External Boundary Isolation)**: External platform claims lacking direct documentation/code evidence default to `UNVERIFIED`.
- **Rule 3 (Repository Path Verification)**: `REPOSITORY_IMPLEMENTATION` claims must validate that `repo_path` exists relative to the workspace root.
- **Rule 4 (Traceability Invariant)**: Every record requires non-empty `statement`, `source`, `justification`, `classification`, and `boundary`.

---

## 5. Machine-Readable & Human Output Formats

- **Markdown Audit Table**: Formatted as GitHub Flavored Markdown for human review.
- **JSON Evidence Manifest**: Machine-readable JSON manifest (`schema_version: "v1.0"`) for automated CI/CD pipeline verification.
