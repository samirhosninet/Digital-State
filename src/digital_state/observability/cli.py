"""CLI Search Interface for Digital State Observability (ORCHESTRATION-004).

Provides query primitives for searching projected audit log events.
"""

from typing import List, Dict, Any, Optional
from digital_state.observability.projector import AuditLogProjector


class CLISearch:
    """CLI Search wrapper over AuditLogProjector."""

    def __init__(self, workspace_root: str = None):
        self.projector = AuditLogProjector(workspace_root)

    def query(
        self,
        event_type: Optional[str] = None,
        agent_id: Optional[str] = None,
        feature_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Executes read-only query over audit history."""
        return self.projector.search_events(
            event_type=event_type,
            agent_id=agent_id,
            feature_id=feature_id,
        )
