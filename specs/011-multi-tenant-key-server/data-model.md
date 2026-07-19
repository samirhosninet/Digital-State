# Data Model: Multi-Tenant Key Server Authentication

## Entities & Data Structures

### 1. Tenant Cryptographic Identity Record (`TenantIdentityRecord`)

Represented in `RuntimeStore` identity storage:

```json
{
  "tenant_id": "tenant-alpha",
  "identity_id": "builder-agent-01",
  "role": "builder",
  "public_key": {
    "key_id": "key-ecdsa-p256-001",
    "algorithm": "ECDSA_P256",
    "value": "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE...",
    "status": "ACTIVE",
    "created_at": "2026-07-19T14:00:00Z"
  }
}
```

### 2. Governed Tenant Context (`GovernedTenantContext`)

Resolved by `digital_state.runtime.adapter.resolve_governance_context`:

```python
{
  "tenant_id": "tenant-alpha",
  "feature_id": "011-multi-tenant-key-server",
  "agent_key": {
    "key_id": "key-ecdsa-p256-001",
    "signature": "MEUCIQD...",
    "role": "builder",
    "public_key": {...}
  }
}
```

### 3. Tenant Authentication Audit Event (`TenantAuditEvent`)

Logged into `ledger.jsonl`:

```json
{
  "event": "TENANT_AUTH_EVALUATION",
  "actor": "builder-agent",
  "tenant_id": "tenant-alpha",
  "outcome": "ALLOWED",  // "ALLOWED" or "DENIED"
  "reason": "Valid signature and role authorization for tenant domain",
  "timestamp": "2026-07-19T14:05:00Z"
}
```

---

## State Transition & Validation Rules

1. **Tenant Domain Match Rule**: `context.tenant_id == target_resource.tenant_id`. If mismatched, authentication returns Fail-Safe Default-Deny.
2. **Key Authority Rule**: Key lookup MUST query `RuntimeStore` with `(tenant_id, profile/role)`.
3. **Single-Tenant Fallback Rule**: If `tenant_id` is null or empty, `tenant_id` defaults to `"default_tenant"`.
