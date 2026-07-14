import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, Any

from kernel.exceptions import EvidenceError


class Evidence:
    """Represents a verifiable piece of evidence submitted at a lifecycle gate."""

    def __init__(
        self,
        evidence_id: str,
        owner: str,
        evidence_type: str,
        content: Dict[str, Any],
        signature: str,
        timestamp: str = "",
        status: str = "Pending",
    ):
        self.evidence_id = evidence_id
        self.owner = owner
        self.evidence_type = evidence_type
        self.content = content
        self.signature = signature
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        self.status = status
        self.hash = self._calculate_content_hash()

    def _calculate_content_hash(self) -> str:
        """Calculate SHA-256 hash of the content dictionary."""
        serialized = json.dumps(self.content, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def verify_signature(self, public_key: Any) -> bool:
        """Verifies the owner's signature against the calculated content hash using public key."""
        if isinstance(public_key, dict):
            from kernel.verifier import CryptoVerifier
            return CryptoVerifier.verify(public_key, self.content, self.signature)
        else:
            expected_sig = f"{public_key}-signed-{self.hash}"
            if self.signature != expected_sig:
                raise EvidenceError("Invalid signature on evidence: verification failed.")
            return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "owner": self.owner,
            "evidence_type": self.evidence_type,
            "content": self.content,
            "hash": self.hash,
            "signature": self.signature,
            "timestamp": self.timestamp,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Evidence":
        return cls(
            evidence_id=data["evidence_id"],
            owner=data["owner"],
            evidence_type=data["evidence_type"],
            content=data["content"],
            signature=data["signature"],
            timestamp=data.get("timestamp", ""),
            status=data.get("status", "Pending"),
        )
