# Security Policy — Digital State Governance Framework

## Known Security Boundary: Legacy Signature Verification Bypass

### Status: DEPRECATED — Scheduled for removal

### Description

The `Evidence.verify_signature()` method in `src/kernel/evidence.py` supports two verification paths:

1. **Cryptographic (recommended)**: When `public_key` is a `dict` containing key metadata (algorithm, key value), verification delegates to `CryptoVerifier` which performs ECDSA P-256 (SHA-256) signature validation.

2. **Legacy mock (deprecated)**: When `public_key` is a plain `str`, the method falls back to trivial string-match verification using the pattern `"{key}-signed-{hash}"`. This path provides **no cryptographic security** and exists solely for backward compatibility with the initial development baseline.

### Risk

Any caller passing a string key bypasses the entire cryptographic verification system. An attacker who knows the key string and content hash can forge a valid signature trivially.

### Current Mitigation

- The legacy path emits a `DeprecationWarning` on every invocation.
- The legacy path logs a `LEGACY_VERIFICATION_USED` warning with the evidence ID and owner.
- Both signals make legacy usage auditable and traceable.

### Migration Path

To migrate from legacy string-key verification to cryptographic verification:

1. Generate an ECDSA P-256 key pair.
2. Register the agent with a dict-based `public_key`:
   ```python
   registry.register_agent(
       agent_id="agent-name",
       role="Role",
       permissions=[...],
       public_key={
           "algorithm": "ECDSA_P256_SHA256",
           "key": "<PEM-encoded public key string>"
       }
   )
   ```
3. Sign evidence content using the corresponding private key.
4. Submit the base64-encoded DER signature as the `signature` parameter.

### Removal Timeline

The legacy string-key path will be removed in a future governance event after all default agent registrations and test fixtures have been migrated to dict-based key metadata.

## Reporting Vulnerabilities

Report security vulnerabilities by opening a private security advisory in this repository or by contacting the repository owner directly.
