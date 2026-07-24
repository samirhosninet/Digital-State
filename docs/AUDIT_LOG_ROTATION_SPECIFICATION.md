# Digital State v1.17 — Audit Log Rotation & Merkle Root Snapshot Specification

## 1. Overview
Upgrades `AuditLogger` with automatic log archiving and Merkle tree root snapshot verification.

## 2. Log Archiving Protocol
- Active Log: `.specify/memory/audit_log.jsonl`
- Archive Pattern: `.specify/memory/audit_log.<timestamp>.archive`
- Threshold: Rotates when file size exceeds `max_bytes` (default 1 MB).

## 3. Merkle Root Snapshotting
- Computes SHA-256 binary Merkle tree over line hashes.
- Guaranteed immutable snapshot verification for enterprise compliance.
