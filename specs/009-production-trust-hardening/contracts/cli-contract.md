# CLI Contract: Production Trust Hardening

## `digitalstate doctor`

Returns JSON with `overall_status`, `identity`, `integrity`, and `hermes` sections. `hermes.mode` is one of `unavailable`, `simulated`, `incompatible`, or `live_verified`. Only `live_verified` can satisfy a live-runtime gate.

## `digitalstate register`

Accepts a supported cryptographic public key and identity metadata. Plaintext signing values are rejected. Success output includes the identity fingerprint, not secret material.

## `digitalstate repair`

Requires an explicit recovery source and confirmation flag. It preserves current state before replacement, validates the candidate before activation, and outputs the recovery bundle location and decision. It never creates an empty state as silent recovery.

## Release gate

Outputs a JSON release evidence bundle. A non-zero exit means `NOT_READY`; a zero exit means every required check was executed and passed. The command never publishes artifacts.
