"""Enterprise Event Broadcaster Subsystem for Prime Operating Model (v1.17).

Provides pluggable event publication (lifecycle transitions, card dispatch, auditor verification)
with console, webhook, and future NATS transport adapters.
"""

import json
import urllib.request
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


class EventTransport:
    """Base interface for event transport adapters."""

    def emit(self, event_name: str, payload: Dict[str, Any]) -> bool:
        raise NotImplementedError


class ConsoleTransport(EventTransport):
    """Outputs structured event payloads to console stdout."""

    def emit(self, event_name: str, payload: Dict[str, Any]) -> bool:
        timestamp = datetime.now(timezone.utc).isoformat()
        print(f"[EVENT][{timestamp}] {event_name}: {json.dumps(payload)}")
        return True


class WebhookTransport(EventTransport):
    """Posts structured event payloads to an enterprise HTTP webhook endpoint."""

    def __init__(self, endpoint_url: str, headers: Optional[Dict[str, str]] = None):
        self.endpoint_url = endpoint_url
        self.headers = headers or {"Content-Type": "application/json"}

    def emit(self, event_name: str, payload: Dict[str, Any]) -> bool:
        if not self.endpoint_url:
            return False
        data = json.dumps({"event": event_name, "timestamp": datetime.now(timezone.utc).isoformat(), "data": payload}).encode("utf-8")
        req = urllib.request.Request(self.endpoint_url, data=data, headers=self.headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status in (200, 201, 202, 204)
        except Exception:
            return False


class EventBroadcaster:
    """Central event pub/sub broadcaster for Prime lifecycle events."""

    def __init__(self):
        self.transports: List[EventTransport] = [ConsoleTransport()]

    def add_transport(self, transport: EventTransport) -> None:
        self.transports.append(transport)

    def publish(self, event_name: str, payload: Dict[str, Any]) -> None:
        for t in self.transports:
            try:
                t.emit(event_name, payload)
            except Exception:
                pass
