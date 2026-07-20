"""Evidence Governance Data Models (v1.12.0-evidence).

Defines canonical evidence classifications, boundary taxonomies, evidence types,
and traceable evidence records.
"""

import time
import uuid
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


class EvidenceType(str, Enum):
    """Canonical classification of evidence source type."""
    REPOSITORY_IMPLEMENTATION = "Repository Implementation Evidence"
    OFFICIAL_DOCUMENTATION = "Official Documentation Evidence"
    AUTHORITATIVE_SPECIFICATION = "Authoritative Specification Evidence"
    EXTERNAL_RUNTIME = "External Runtime Evidence"


class EvidenceBoundary(str, Enum):
    """Canonical architectural boundaries."""
    DIGITAL_STATE_REPOSITORY = "Digital State Repository"
    HERMES_AGENT_FRAMEWORK = "Hermes Agent Framework"
    PYTHON_PACKAGING_SPEC = "Python Packaging Specification"
    EXTERNAL_PLATFORM = "External Platform Behavior"


class EvidenceClassification(str, Enum):
    """Canonical evidence classifications."""
    VERIFIED = "VERIFIED"
    VERIFIED_ABSENCE = "VERIFIED ABSENCE"
    NOT_FOUND_IN_CURRENT_OFFICIAL_DOCUMENTATION = "NOT FOUND IN CURRENT OFFICIAL DOCUMENTATION"
    UNVERIFIED = "UNVERIFIED"


@dataclass(frozen=True)
class EvidenceRecord:
    """Traceable, machine-verifiable evidence record."""
    statement: str
    evidence_type: EvidenceType
    boundary: EvidenceBoundary
    source: str
    classification: EvidenceClassification
    justification: str

    record_id: str = field(default_factory=lambda: f"ev-{uuid.uuid4().hex[:8]}")
    schema_version: str = "v1.0"
    repo_path: Optional[str] = None
    doc_ref: Optional[str] = None
    commit_sha: Optional[str] = None
    provenance_timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes evidence record to structured dictionary."""
        return {
            "record_id": self.record_id,
            "schema_version": self.schema_version,
            "statement": self.statement,
            "evidence_type": self.evidence_type.value,
            "boundary": self.boundary.value,
            "source": self.source,
            "repo_path": self.repo_path,
            "doc_ref": self.doc_ref,
            "commit_sha": self.commit_sha,
            "classification": self.classification.value,
            "justification": self.justification,
            "provenance_timestamp": self.provenance_timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvidenceRecord":
        """Instantiates EvidenceRecord from dictionary with type conversions."""
        return cls(
            statement=data["statement"],
            evidence_type=EvidenceType(data["evidence_type"]),
            boundary=EvidenceBoundary(data["boundary"]),
            source=data["source"],
            classification=EvidenceClassification(data["classification"]),
            justification=data["justification"],
            record_id=data.get("record_id", f"ev-{uuid.uuid4().hex[:8]}"),
            schema_version=data.get("schema_version", "v1.0"),
            repo_path=data.get("repo_path"),
            doc_ref=data.get("doc_ref"),
            commit_sha=data.get("commit_sha"),
            provenance_timestamp=data.get("provenance_timestamp", time.time()),
        )
