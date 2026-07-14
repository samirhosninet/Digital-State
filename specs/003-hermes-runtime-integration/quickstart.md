# Quickstart & Verification Guide: Hermes Runtime Integration

This guide provides instructions on running simulated runtime validations of the Hermes integration.

---

## 1. Setup & Environment
Ensure the local python virtual environment is initialized:
```bash
uv sync --dev
```

---

## 2. Running Verification Loop
To run the simulated session validation flow:
```bash
$env:PYTHONPATH="D:\Digital-State\src;D:\Digital-State"; uv run python -m pytest tests/integration/test_hermes_flow.py -v
```

This checks:
- Proper loading of the plugin bridge facade.
- Invocation of all six lifecycle hooks in sequence.
- Writing of corresponding events to the audit lines ledger.
