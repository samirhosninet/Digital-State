# Hermes Integration Adapter

## Status: LIVE

The `HermesClient` is a native integration that communicates directly with the real Hermes Agent CLI runtime.

## Current Behavior

| Method | Behavior |
|:-------|:---------|
| `is_mock()` | Returns `False` |
| `metadata()` | Returns dynamic metadata queried from the active profile's configuration |
| `self_test()` | Verifies that the real `hermes` CLI binary is available and operational |
| `execute_command_context()` | Routes command execution directly to the native `builder` profile of Hermes Agent |
| `supports_*()` | Returns accurate boolean capabilities supported by the active environment |

## Integration Specification

The `HermesClient` implements `RuntimeCapability` from `framework/base_runtime.py` and coordinates with the global Hermes CLI executable to bootstrap, register, and run Digital State governance workflows natively.
