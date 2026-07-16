import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict

from digital_state.core.exceptions import EvidenceError


class Evidence:
    """A signed, verifiable piece of lifecycle-gate evidence."""

    def __init__(self, evidence_id: str, owner: str, evidence_type: str,
                 content: Dict[str, Any], signature: str, timestamp: str = "",
                 status: str = "Pending"):
        self.evidence_id = evidence_id
        self.owner = owner
        self.evidence_type = evidence_type
        self.content = content
        self.signature = signature
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        self.status = status
        self.hash = self._calculate_content_hash()

    def _calculate_content_hash(self) -> str:
        serialized = json.dumps(self.content, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def verify_signature(self, public_key: Any) -> bool:
        """Verify with a supported ECDSA P-256 identity; plaintext keys are forbidden."""
        if not isinstance(public_key, dict):
            raise EvidenceError(
                "Legacy plaintext-key verification is disabled; register an ECDSA P-256 public-key identity."
            )
        from digital_state.core.verifier import CryptoVerifier
        return CryptoVerifier.verify(public_key, self.content, self.signature)

    def to_dict(self) -> Dict[str, Any]:
        return {"evidence_id": self.evidence_id, "owner": self.owner,
                "evidence_type": self.evidence_type, "content": self.content,
                "hash": self.hash, "signature": self.signature,
                "timestamp": self.timestamp, "status": self.status}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Evidence":
        return cls(data["evidence_id"], data["owner"], data["evidence_type"],
                   data["content"], data["signature"], data.get("timestamp", ""),
                   data.get("status", "Pending"))
