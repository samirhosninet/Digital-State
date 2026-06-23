# Clean Room Install Guide

> This guide tests the Digital State universal overlay contract (Constitution Article XI). It verifies that the installer and governance files work on a brand-new target workspace with no historical awareness of any prior target.

## Prerequisites

- Hermes Agent >=0.14.0 installed and `hermes` CLI accessible in PATH.
- PowerShell 5.1+ (for Windows) or bash (for POSIX targets).
- Python 3.11+ (for plugin execution and validation).

## Quick Clean Room Test

1. Clone or extract the Digital State package to a temporary directory:
```bash
   mkdir /tmp/ds-clean-room
   cd /tmp/ds-clean-room
   # Extract or clone Digital State
```

2. Run the structural validator (no Hermes needed):
```powershell
   cd /tmp/ds-clean-room
   powershell -File scripts/validate-final.ps1
   # Expected: 126+ checks, 0 errors, 0 warnings
```

3. Run the behavioral pytest suite:
```bash
   python -m pytest tests/ -v
   # Expected: 59 passed
```

4. Run the installer (requires Hermes):
```powershell
   powershell -File scripts/install.ps1
   # Expected: All 3 profiles installed, config.yaml verified, backups created
```

5. Verify installed profiles:
```bash
   hermes -p prime kanban list
   hermes -p auditor plugins list
   # Expected: prime kanban list works, auditor sees audit-matrix
```

6. Run a test governance cycle:
```bash
   hermes -p prime kanban create "Test governance cycle"
   # Follow the Builder → review-required → promote to review → Auditor flow
```

## Success Criteria

- `validate-final.ps1` exits 0.
- `pytest tests/ -v` exits with all tests passed.
- All 3 profiles spawn successfully.
- Kanban board is accessible and cards can be created.

## Failure Recovery

If any step fails, check:
- `risk-ledger.md` for known issues.
- `scripts/validate-final.ps1` for structural errors.
- `kanban.db` permissions and location.
