"""Hermes Dispatcher for Digital State Hermes Interceptor (ORCHESTRATION-003).

Dispatches task assignments to Builder after verifying validate_builder_execution_gate().
"""

import os
from typing import Dict, Any

from digital_state.sdk import validate_builder_execution_gate, validate_gate_approval


class HermesDispatcher:
    """Dispatches execution contexts to Builder after validate_builder_execution_gate verification."""

    def __init__(self, workspace_root: str = None):
        self.workspace_root = workspace_root or os.getcwd()

    def dispatch_builder(
        self,
        feature_id: str,
        builder_key: Any,
        workspace_root: str = None,
    ) -> Dict[str, Any]:
        """Evaluates validate_builder_execution_gate() before dispatching Builder execution context."""
        root = workspace_root or self.workspace_root
        gate_passed, gate_reason = validate_builder_execution_gate(
            feature_id, builder_key, workspace_root=root
        )

        if not gate_passed:
            return {
                "status": "BLOCKED",
                "authorized": False,
                "feature_id": feature_id,
                "reason": gate_reason,
            }

        return {
            "status": "DISPATCHED",
            "authorized": True,
            "feature_id": feature_id,
            "reason": gate_reason,
        }
