# Quickstart & Verification Guide: Governance Kernel

This guide outlines the validation scenarios to verify the functionality of the Digital State governance kernel.

## Prerequisites
* Python 3.11+
* CLI commands configured as per [cli-contract.md](file:///d:/Digital-State/specs/001-governance-kernel/contracts/cli-contract.md).

## End-to-End Validation Scenario

### Step 1: Agent Registration
Register the three primary profiles.
```bash
# Register Prime
digitalstate register --id prime-agent --role Prime --key "key-prime"

# Register Builder
digitalstate register --id builder-agent --role Builder --key "key-builder"

# Register Auditor
digitalstate register --id auditor-agent --role Auditor --key "key-auditor"
```
* **Expected Outcome**: Agents successfully registered. Registry log contains 3 entries.

### Step 2: Establish Specification Gate
The Prime submits specification requirements and signs off.
```bash
digitalstate submit --feature feature-001 --gate SPECIFICATION --evidence "spec-complete-v1.0" --agent prime-agent
digitalstate approve --feature feature-001 --gate SPECIFICATION --agent prime-agent
```
* **Expected Outcome**: State transitions to `PLANNING`.

### Step 3: Planning Gate Verification (Auditor approval)
Builder submits a plan; Auditor approves.
```bash
# Builder submits plan
digitalstate submit --feature feature-001 --gate PLANNING --evidence "plan-draft-v1.0" --agent builder-agent

# Auditor approves
digitalstate approve --feature feature-001 --gate PLANNING --agent auditor-agent
```
* **Expected Outcome**: State transitions to `IMPLEMENTATION`.

### Step 4: Verification Gate (Auditor review & Prime final sign-off)
Builder completes implementation tasks and submits evidence; Auditor verifies, and Prime closes.
```bash
# Builder submits implementation logs
digitalstate submit --feature feature-001 --gate IMPLEMENTATION --evidence "test-logs-pass" --agent builder-agent

# Auditor verifies and approves
digitalstate approve --feature feature-001 --gate IMPLEMENTATION --agent auditor-agent

# Prime accepts and completes
digitalstate approve --feature feature-001 --gate VERIFICATION --agent prime-agent
```
* **Expected Outcome**: Lifecycle state transitions to `COMPLETED`. Immutable log records the sequence.
