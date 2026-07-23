# Digital State Installation Guide

Welcome to **Digital State**, the evidence-gated agentic governance and distributed device runtime system.

This guide provides step-by-step instructions for installing and initializing Digital State using the **User Installation Experience Layer**.

---

## 🚀 One-Command Installation

A new user can install, bootstrap, initialize, and verify Digital State using a single command:

```bash
digitalstate install
```

*(or `digital-state install`)*

---

## 📋 Prerequisites

Before running the installation command, ensure your environment meets the following requirements:

- **Operating System:** Windows 10/11, Windows Server 2019+, or Linux (Ubuntu 20.04+)
- **Python:** Version **3.11** or higher (`python --version`)
- **Pip:** Package installer for Python (`python -m pip --version`)

---

## ⚙️ What the Install Command Orchestrates

When you run `digitalstate install`, the installer automatically coordinates 8 zero-touch steps:

```text
INSTALL COMMAND
      │
      ├── 1. Environment Validation (Python 3.11+ & workspace permissions)
      ├── 2. Dependency Verification (cryptography & PyYAML)
      ├── 3. Runtime Bootstrap (Directories & core config seeding)
      ├── 4. Digital State Initialization (State, agent identity & trust roots)
      ├── 5. Hermes Integration Check (Mock/Live Hermes client readiness)
      ├── 6. Governance Readiness Check (Verifiable state & audit trails)
      ├── 7. Doctor Validation (4-pillar health inspection)
      └── 8. Evidence Report Generation (.specify/installation_report.json)
```

---

## 🖥️ Expected Output

Upon successful execution, `digitalstate install` outputs a clean status report:

```text
====================================================
Digital State Single-Command Installation Experience
====================================================
Environment Validation .. PASS
Dependency Verification . PASS (cryptography v41.0.0+)
Runtime Bootstrap ....... PASS
Digital State Init ...... PASS
Hermes Integration ...... CONNECTED
Governance Readiness .... READY
Doctor Validation ....... PASS
----------------------------------------------------
INSTALLATION STATUS: Digital State READY
Evidence Report: .specify/installation_report.json
====================================================
```

### Generated Evidence Artifact

The installer materializes an installation evidence file at `.specify/installation_report.json`:

```json
{
  "runtime": "READY",
  "governance": "READY",
  "hermes": "CONNECTED",
  "doctor": "PASS",
  "details": {
    "workspace_root": "/path/to/workspace",
    "python_version": "3.11.15",
    "cryptography_version": "41.0.7",
    "environment_validation": "PASS",
    "dependency_verification": "PASS"
  }
}
```

---

## 🔄 Official Lifecycle Commands

Digital State provides 4 core first-class lifecycle CLI commands:

### 1. `digitalstate install`
Executes zero-touch installation, runtime bootstrap, workspace initialization, Hermes integration check, and doctor validation. Generates `.specify/installation_report.json`.

### 2. `digitalstate update`
Executes the Official Update Lifecycle to upgrade an existing installation safely without reinstallation:
```bash
digitalstate update
```
- **Check for available updates without applying:**
  ```bash
  digitalstate update --check
  ```
- **Force re-application of update:**
  ```bash
  digitalstate update --force
  ```
- **Generates evidence report:** `.specify/update_report.json`
- **Safety guarantee:** Non-destructive migration preserving `.specify/` workspace files, `.specify/memory/audit_log.jsonl` evidence, `RuntimeStore` identities, and Hermes configuration. Automatic rollback if migration fails.

### 3. `digitalstate doctor`
Runs the 4-pillar system health inspection (Installation, Configuration, Governance, Hermes):
```bash
digitalstate doctor
```

### 4. `digitalstate version`
Displays current Digital State version information:
```bash
digitalstate version
```

---

## 🔧 Useful Command Options

- **Dry-Run Inspection (no file mutations):**
  ```bash
  digitalstate install --dry-run
  ```

- **JSON Output Format:**
  ```bash
  digitalstate install --format json
  ```

---

## ❓ Troubleshooting

### 1. `Command 'digitalstate' not found`
If the command is not in your system PATH, ensure you have installed the package in editable or standard mode:
```bash
pip install -e .
```
Or execute directly using Python module syntax:
```bash
python -m digital_state.cli.cli install
```

### 2. `Python version < 3.11`
Digital State requires Python 3.11 or higher for cryptography and runtime typing capabilities. Upgrade Python and retry `digitalstate install`.
