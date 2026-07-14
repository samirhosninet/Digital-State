# Hermes Integration Adapter

## Status: MOCK

The current `HermesClient` implementation is a **mock placeholder**. It does not connect to or communicate with a real Hermes Agent instance.

## Current Behavior

| Method | Behavior |
|:-------|:---------|
| `is_mock()` | Returns `True` |
| `metadata()` | Returns hardcoded static metadata |
| `self_test()` | Checks if `git` is available locally — does NOT test Hermes |
| `execute_command_context()` | Returns a hardcoded mock response — no execution occurs |
| `supports_*()` | Returns hardcoded boolean capabilities |

## Contract for a Real Adapter

A production `HermesClient` must:

1. **Implement** `RuntimeCapability` from `framework/base_runtime.py`.
2. **Connect** to a verified Hermes execution environment.
3. **Return** `is_mock() == False`.
4. **Return** live metadata from the actual Hermes runtime in `metadata()`.
5. **Execute** commands through the real Hermes execution context in `execute_command_context()`.
6. **Test** actual Hermes connectivity in `self_test()`.

## Class Name

The class name `HermesClient` is the stable public interface. Do not rename it — replace the mock internals with real implementations.
