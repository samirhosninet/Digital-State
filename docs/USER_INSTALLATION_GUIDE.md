# Official End-User Installation & Onboarding Guide: Digital State

- **Document ID**: `USER_INSTALLATION_GUIDE.md`
- **Target System**: Digital State Zero-Touch Installation & First-Run Bootstrap Protocol (`v1.14.0-bootstrap`)
- **Supported Operating Systems**: Windows 10/11, macOS 12+, Linux (Ubuntu/Debian/RHEL)

---

## 1. Quick Start: Single-Command Zero-Touch Installation

Digital State provides fully automated single-command installers that bootstrap clean environments, configure Hermes Desktop integration, initialize governance workspaces, generate ECDSA device identity keypairs, and create 4-file evidence bundles without manual configuration.

### On Windows (PowerShell):
```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

### On macOS / Linux (POSIX Shell):
```bash
chmod +x install.sh
./install.sh
```

---

## 2. Pre-Flight Verification (Dry-Run Mode)

To verify system prerequisites (Python 3.11+, pip, platform compatibility) without making any filesystem modifications, run the installer in `--dry-run` mode:

### Windows:
```powershell
powershell -ExecutionPolicy Bypass -File install.ps1 -DryRun
```

### macOS / Linux:
```bash
./install.sh --dry-run
```

---

## 3. Automated First-Run Journey Overview

When the installer runs, it executes the following 8 automated steps:
1. **Prerequisite Check**: Validates Python $\ge 3.11$, pip, and platform architecture.
2. **Directory Bootstrapping**: Idempotently creates `.specify/`, `.specify/memory/`, and `.specify/device/`.
3. **Hermes Integration**: Auto-detects Hermes installation root (`%LOCALAPPDATA%\hermes` or `~/.hermes`), registers `digital_state` plugin in `config.yaml`, and seeds `prime`, `builder`, and `auditor` profile directories.
4. **Workspace Initialization**: Initializes `GovernanceKernel` state, seeding default governance roles and initial checkpoint gates.
5. **Device Keypair Generation**: Generates hardware/OS-bound ECDSA P-256 identity keypair in OS keystore (`DeviceKeystore`).
6. **Device Evidence Bundle Creation**: Writes initial 4-file evidence bundle (`device-status.json`, `identity-proof.json`, `runtime-attestation.json`, `policy-state.json`).
7. **Automated Verification**: Runs `digitalstate doctor` and `digitalstate audit-evidence --check --all` to confirm 100% system health.
8. **Manifest Ledger Recording**: Writes machine-readable `integration.json` manifest.

---

## 4. Post-Installation Health Verification Commands

After running the installer, verify system state using the official CLI commands:

```bash
# 1. Inspect installation state and integration health
digitalstate doctor

# 2. Execute automated evidence audit check across all subsystems
digitalstate audit-evidence --check --all

# 3. Output machine-readable JSON evidence manifest
digitalstate audit-evidence --all --format json
```

---

## 5. Troubleshooting & Support

| Issue | Root Cause | Remediation |
|---|---|---|
| `Python 3.11+ required` | System Python version is $< 3.11$ | Install Python 3.11 or higher from python.org or package manager |
| `Hermes root directory not found` | Hermes Desktop not installed | Install Hermes Desktop or set `HERMES_HOME` environment variable |
| `Permission Denied` | Insufficient file permissions | Run PowerShell as Administrator or execute `chmod +x install.sh` |

---

$$\mathbf{ZERO-TOUCH\ INSTALLATION\ GUIDE\ COMPLETE}$$
