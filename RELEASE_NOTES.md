# Official Release Notes: Digital State v1.3

We are pleased to announce the official release of **Digital State v1.3**. This version establishes a unified user installation journey and resolves security boundaries to deliver a stable, evidence-gated governance framework for the Hermes Agent ecosystem.

---

## 1. Unified User Installation Journey

We have transformed the repository from a developer-only codebase into a package installer.

### Path A: Primary User Installation (GitHub Remote Package)
Installs the dependency directly into any Python project:
```bash
pip install git+https://github.com/samirhosninet/Digital-State.git
```
Users initialize and verify workspaces using:
```bash
digitalstate init
digitalstate doctor
```

### Path B: Developer Repository Installation (Local Clone Helpers)
For developers modifying the codebase or self-hosted environments, we maintain:
- **`install.ps1`** (Windows PowerShell helper)
- **`install.sh`** (Unix shell helper)

---

## 2. Refined Security Claims & Boundaries

Following deep architectural audits, we have refined the core security claim of Digital State:

* **Evidence-Gated Governance:** All feature state transitions, tool outcomes, and cryptographic signatures are verified and appended to the immutable local audit trail.
* **Hermes Hook Enforcement Boundary:** The Hermes client adapter is currently a **mock/simulation compatibility layer**. This version does not claim remote runtime enforcement or synchronous execution blocking.

---

## 3. Scope of Changes

- **Console Script Registry:** Added `digitalstate` entrypoint in `pyproject.toml`.
- **Diagnostics Utility (`digitalstate doctor`):** Added a structured JSON diagnostic checking Python runtimes, workspace configurations, state databases, and mock Hermes status.
- **Idempotent Initialization (`digitalstate init`):** Ensures reinstallation does not modify existing configurations.
- **Dynamic Path Cleaning:** Removed hardcoded drive letters in test suites to support clean system-independent CI validation.

---

## 4. Release Registry Detail
* **Release Version:** `v1.3-release`
* **Release Commit SHA:** `11a858fcc606deca412ef16b0ea5978189689408`
* **Test Success Rate:** 100% (47/47 test cases passing)
