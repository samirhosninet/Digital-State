# Plugin Hook Interfaces Contract

This document defines the Python callable signatures required by the Hermes Plugin API for the Digital State bridge.

---

## 1. Plugin Registration Entrypoint
Every plugin must export a top-level `register(ctx)` callable:

```python
def register(ctx) -> bool:
    """Invoked on plugin load. Should initialize class and register hooks."""
```

---

## 2. Hook Callable Signatures

### on_session_start_handler
```python
def on_session_start_handler(context: dict) -> bool:
    """Invoked at the beginning of a user session."""
```

### pre_llm_call_handler
```python
def pre_llm_call_handler(prompt: str, context: dict) -> bool:
    """Invoked before routing a prompt to the LLM. Returning False blocks the request."""
```

### post_llm_call_handler
```python
def post_llm_call_handler(response: str, context: dict) -> None:
    """Invoked after receiving the LLM response."""
```

### pre_tool_call_handler
```python
def pre_tool_call_handler(tool_name: str, arguments: dict, context: dict) -> bool:
    """Invoked before executing any tool. Returning False triggers a Fail-Safe Deny."""
```

### post_tool_call_handler
```python
def post_tool_call_handler(tool_name: str, outcome: dict, context: dict) -> None:
    """Invoked after executing a tool to record execution logs as evidence."""
```

### on_session_end_handler
```python
def on_session_end_handler(context: dict) -> None:
    """Invoked at session termination."""
```
