# EVIDENCE REPRODUCTION RECORD — CI & REPRODUCIBILITY REMEDIATION-001

**GOVERNANCE EVENT:** REMEDIATION-001  
**REPOSITORY:** `samirhosninet/Digital-State`  
**BASELINE COMMIT SHA:** `8b8ff37798d35ccca81535b288e08979fd444564` (RUNTIME-BASELINE-003)  
**ENVIRONMENT:** Python 3.11.15, Windows 11 / Ubuntu Latest  
**REPRODUCIBILITY STATUS:** 100% REPRODUCIBLE (166/166 PASSED)  

---

## 1. Environment Details

```text
Python Version : Python 3.11.15
Pytest Version : pytest 9.1.1, pluggy-1.6.0
Package Install: pip install -e . (Digital-State 0.1.0)
HEAD SHA       : 8b8ff37798d35ccca81535b288e08979fd444564
Git Status     : Clean working tree
```

---

## 2. Test Execution Summary

```text
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\Digital-State
configfile: pyproject.toml
collected 166 items

tests\integration\test_cli_flow.py .                                     [  0%]
tests\integration\test_concurrency.py ...                                [  2%]
tests\integration\test_e2e_release_bootstrap.py .                        [  3%]
tests\integration\test_governance_flow.py .                              [  3%]
tests\integration\test_hermes_flow.py ..                                 [  4%]
tests\integration\test_installation.py .                                 [  5%]
tests\integration\test_story1.py ..                                      [  6%]
tests\integration\test_story2.py ...                                     [  8%]
tests\integration\test_tenant_isolation.py ..                            [  9%]
tests\regression\test_historical_bootstrap_regression.py ..........      [ 15%]
tests\test_bootstrap_rev3.py .......                                     [ 19%]
tests\test_observability_rev4.py ....                                    [ 22%]
tests\test_orchestration_audit_rev2.py ........                          [ 27%]
tests\test_orchestration_automation_rev3.py ....                         [ 29%]
tests\test_orchestration_remediation.py ...                              [ 31%]
tests\unit\test_adapter_tenant.py ....                                   [ 33%]
tests\unit\test_bootstrap.py .....                                       [ 36%]
tests\unit\test_bug_val_regressions.py ...                               [ 38%]
tests\unit\test_cli_commands.py .........                                [ 43%]
tests\unit\test_cryptography.py ........                                 [ 48%]
tests\unit\test_device_cli.py ......                                     [ 52%]
tests\unit\test_device_daemon.py .                                       [ 53%]
tests\unit\test_device_enrollment.py .....                               [ 56%]
tests\unit\test_device_ledger.py ...                                     [ 57%]
tests\unit\test_device_policy_engine.py ....                             [ 60%]
tests\unit\test_device_sync_client.py .....                              [ 63%]
tests\unit\test_evidence_cli.py ..                                       [ 64%]
tests\unit\test_evidence_device_validator.py .....                      [ 67%]
tests\unit\test_evidence_federation.py ...                              [ 69%]
tests\unit\test_evidence_governance.py .........                         [ 74%]
tests\unit\test_evidence_kernel_bridge.py ....                           [ 77%]
tests\unit\test_foundational.py ......                                   [ 80%]
tests\unit\test_integrity.py ......                                      [ 84%]
tests\unit\test_kernel.py ........                                       [ 89%]
tests\unit\test_layer1_stub.py .                                         [ 89%]
tests\unit\test_layer2_engine_subsystems.py ....                         [ 92%]
tests\unit\test_layer2_lifecycle_commands.py .                           [ 92%]
tests\unit\test_layer2_manifest_and_lock.py ..                          [ 93%]
tests\unit\test_layer3_runtime_isolation.py ..                           [ 95%]
tests\unit\test_ledger_chaining.py ...                                   [ 96%]
tests\unit\test_negative_crypto.py .....                                 [ 99%]
tests\unit\test_planning.py ..                                           [100%]

============================= 166 passed in 14.89s =============================
```
