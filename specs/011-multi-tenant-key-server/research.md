# Research & Architectural Decisions: Multi-Tenant Key Server Authentication

## Decision 1: Tenant Key Storage & Isolation

- **Decision**: Extend `RuntimeStore` identity query schema to support an optional `tenant_id` namespace column/attribute, defaulting to `"default_tenant"` when unspecified.
- **Rationale**: `RuntimeStore` is the canonical identity authority (ADR-011). Adding tenant scoping directly in `RuntimeStore` guarantees that identity records are stored and queried within explicit tenant boundaries without introducing secondary identity stores.
- **Alternatives Considered**:
  - *Separate SQLite database file per tenant*: Adds high file-handle management complexity and deployment overhead for local development.
  - *In-memory tenant cache*: Violates persistent accountability principles.

---

## Decision 2: Context Adapter Tenant Resolution Pipeline

- **Decision**: Extend `resolve_governance_context` in `digital_state.runtime.adapter` to extract `tenant_id` across the 3-tier lookup pipeline:
  - **Tier 1**: `context.get("tenant_id")`
  - **Tier 2**: `os.environ.get("DS_TENANT_ID")`
  - **Tier 3**: Workspace state `.specify/state.json` -> `tenant_id` property, or default to `"default_tenant"`.
- **Rationale**: Reuses the proven Option E Dual-Boundary Hybrid Architecture (ADR-013) without introducing new trust boundaries or architecture layers.
- **Alternatives Considered**:
  - *Dedicated MultiTenantAdapter class*: Violates anti-duplication rule and creates unnecessary abstraction layers.

---

## Decision 3: Backward Compatibility Guarantee

- **Decision**: Requests omitting `tenant_id` resolve to `tenant_id = "default_tenant"`. Existing key storage records without explicit tenant IDs are automatically mapped to `"default_tenant"`.
- **Rationale**: Ensures 100% backward compatibility for single-tenant local operation, existing unit test suites, and CLI invocations.
