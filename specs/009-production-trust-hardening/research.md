# Research: Production Trust Hardening

## Decision: Remove plaintext authorization rather than keep a compatibility switch

**Rationale**: A switch invites accidental production bypass and conflicts with verifiable identity. Migrations must be explicit and fail when existing plaintext registrations are encountered.  
**Alternatives considered**: Warn-only fallback; environment flag; automatic conversion. Rejected because none proves key ownership or prevents a known-value forgery.

## Decision: Treat the local hash chain as tamper-evident, not immutable

**Rationale**: A writer with filesystem access can recreate a local hash chain. The product will detect inconsistency and record a signed/anchored release or recovery attestation where available, while documenting that remote append-only storage is outside this release.  
**Alternatives considered**: Claim immutable logs; build a remote service. Rejected respectively as inaccurate and beyond the local-product scope.

## Decision: Classify Hermes in four states

**Rationale**: `unavailable`, `simulated`, `incompatible`, and `live_verified` prevent a boolean “live” claim from conflating binary discovery with usable enforcement.  
**Alternatives considered**: mock/live boolean. Rejected because it cannot express an unsupported version or missing handshake evidence.

## Decision: Recovery is an operator action with source validation and preservation

**Rationale**: Recreating empty files destroys the distinction between repair and data loss. Recovery must use a named source, archive current material, validate the candidate, then record the result.  
**Alternatives considered**: automatic empty-state rebuilding. Rejected because it violates trace-complete accountability.

## Decision: Release readiness is generated from executed commands

**Rationale**: Static Markdown reports go stale. A release gate should reject dirty source, scan material in scope, run build/test journeys, and emit machine-readable evidence keyed to the source revision and artifact.  
**Alternatives considered**: manually maintained release reports. Rejected because they do not prove current state.
