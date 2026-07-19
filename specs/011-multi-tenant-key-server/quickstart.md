# Quickstart & Validation Guide: Multi-Tenant Key Server Authentication

## Overview
This document describes how to execute local validation scenarios proving multi-tenant key server authentication and isolation.

---

## Scenario 1: Tenant Key Isolation Validation

1. **Set Tenant Environment Variables**:
   ```bash
   $env:DS_TENANT_ID="tenant-alpha"
   $env:DS_FEATURE_ID="FEAT-TENANT-001"
   $env:HERMES_PROFILE="builder"
   ```

2. **Execute Hook Enforcement Check**:
   ```bash
   python scripts/verify_hook_contract.py
   ```
   **Expected Outcome**: System validates tenant identity against `RuntimeStore` and outputs `HOOK_ENFORCEMENT_VERIFIED`.

3. **Verify Cross-Tenant Denial**:
   ```bash
   $env:DS_TENANT_ID="tenant-beta"
   # Present Tenant A key signature for Tenant B feature
   python scripts/verify_hook_contract.py
   ```
   **Expected Outcome**: Authentication is denied with Fail-Safe Deny error: `Tenant identity mismatch or missing signed metadata. Fail-Safe Deny triggered.`

---

## Scenario 2: Single-Tenant Backward Compatibility Test

1. **Clear Explicit Tenant Variables**:
   ```bash
   Remove-Item Env:\DS_TENANT_ID -ErrorAction SilentlyContinue
   ```

2. **Run Pytest Suite**:
   ```bash
   pytest tests/unit/test_plugin.py tests/integration/test_hermes_flow.py
   ```
   **Expected Outcome**: All existing single-tenant unit and integration tests pass without error (100% pass rate).
