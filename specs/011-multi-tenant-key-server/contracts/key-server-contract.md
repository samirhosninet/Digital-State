# Contract Specification: Multi-Tenant Key Server Interface

## Overview
Defines the contract schema for tenant-aware key authentication requests and governance hook context resolution.

---

## Hook Context Contract Extension

Every Hermes lifecycle hook context dictionary passed into `DigitalStatePlugin` supports the following schema:

```json
{
  "tenant_id": "string (optional, defaults to 'default_tenant')",
  "feature_id": "string (required for pre_tool_call enforcement)",
  "agent_key": {
    "key_id": "string (required)",
    "signature": "string (required)",
    "role": "string (required)",
    "public_key": "object (required)"
  }
}
```

---

## Response Contract

### Success Authorization Response

```json
{
  "action": "allow",
  "tenant_id": "tenant-alpha",
  "feature_id": "011-multi-tenant-key-server",
  "message": "Authorized for tenant tenant-alpha"
}
```

### Fail-Safe Deny Response (Tenant Mismatch or Invalid Identity)

```json
{
  "action": "block",
  "message": "Tenant identity mismatch or missing signed metadata. Fail-Safe Deny triggered."
}
```
