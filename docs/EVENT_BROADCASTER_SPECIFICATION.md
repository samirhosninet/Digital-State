# Digital State v1.17 — Enterprise Event Broadcaster Specification

## 1. Overview
The `EventBroadcaster` subsystem provides pub/sub event broadcasting for Prime Operating Model state machine transitions.

## 2. Transports
- **`ConsoleTransport`:** Outputs JSON-formatted events to stdout.
- **`WebhookTransport`:** Posts POST payloads to enterprise HTTP webhook endpoints.
- **Future NATS Transport Adapter:** Standardized interface for NATS/Kafka integration.

## 3. Published Event Types
- `PHASE_STARTED`
- `CARD_DISPATCHED`
- `AUDITOR_VERIFICATION_PASS`
- `PROJECT_COMPLETED`
