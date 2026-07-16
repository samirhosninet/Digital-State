# Data Model: Production Trust Hardening

## Cryptographic Identity

| Field | Rules |
|---|---|
| agent_id | Unique and immutable after registration |
| role | Prime, Builder, or Auditor; policy-authorized |
| public_key | PEM public key with supported algorithm |
| algorithm | Exactly the supported signing algorithm |
| key_id | Stable fingerprint used for audit correlation |
| status | Active, Revoked, or Suspended |
| created_at / revoked_at | UTC lifecycle timestamps |

## Authorization Decision

Records an attempted action: feature ID, action, requesting agent, required role, decision, reason, evidence ID, and UTC timestamp. It is appended for both allow and deny outcomes.

## Runtime Attestation

Records mode (`unavailable`, `simulated`, `incompatible`, `live_verified`), executable path, reported version, compatibility outcome, handshake evidence, and UTC timestamp.

## Recovery Package

Contains the named candidate input, preserved pre-recovery snapshot location and checksum, validation outcome, operator identity, and recovery audit event.

## Release Evidence Bundle

Contains source revision and cleanliness, artifact checksums, environment details, runtime attestation, each command result, required-check coverage, and final readiness decision.
