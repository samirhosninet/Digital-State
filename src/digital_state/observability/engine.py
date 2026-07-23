"""Projection Engine for Digital State Observability (ORCHESTRATION-004).

Filters and queries audit projections by event_type, agent_id, or feature_id.
"""

from typing import List, Dict, Any, Optional
from digital_state.observability.serializer import EventSerializer


class ProjectionEngine:
    """Queries and filters projected audit event streams."""

    def __init__(self):
        self.serializer = EventSerializer()

    def filter_events(
        self,
        events: List[Dict[str, Any]],
        event_type: Optional[str] = None,
        agent_id: Optional[str] = None,
        feature_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Filters event list based on query criteria."""
        filtered = []
        for raw in events:
            serialized = self.serializer.serialize_entry(raw)
            if not serialized:
                continue

            if event_type and serialized["event_type"] != event_type:
                continue
            if agent_id and serialized["agent_id"] != agent_id:
                continue
            if feature_id:
                details = serialized.get("details", {})
                feat = details.get("feature_id")
                if feat != feature_id:
                    continue

            filtered.append(serialized)
        return filtered
