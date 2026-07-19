# Tasks: 012 Cryptographic Audit Log Signature Chaining

**Input**: Design documents from `/specs/012-audit-log-signature-chaining/`

---

## Phase 1: Setup

- [x] T001 Initialize spec directory and checklist for 012-audit-log-signature-chaining

---

## Phase 2: Foundational Ledger Engine Modifications

- [x] T002 Update `Ledger.append()` in `governance/self-governance/_lib/ledger.py` to calculate SHA-256 of preceding entry and inject `prev_entry_hash`
- [x] T003 Implement `Ledger.verify_chain()` in `governance/self-governance/_lib/ledger.py` for sequential hash-chain verification

---

## Phase 3: CLI Utility & Verification

- [x] T004 Add `digitalstate verify-ledger` subcommand to `src/digital_state/cli/cli.py`
- [x] T005 Create unit test suite `tests/unit/test_ledger_chaining.py` covering valid chains, line tampering detection, and legacy fallback

---

## Phase 4: Verification & Polish

- [x] T006 Run `python scripts/verify_hook_contract.py`
- [x] T007 Run `pytest tests/`
- [x] T008 Run `python -m digital_state.cli.cli doctor`

