"""Digital State Evidence Governance Subsystem (v1.12.0-evidence).

Provides reusable infrastructure for evidence classification, boundary resolution,
negative-evidence rule validation, and dual-format report generation.
"""

from digital_state.governance.evidence.models import (
    EvidenceType,
    EvidenceBoundary,
    EvidenceClassification,
    EvidenceRecord,
)
from digital_state.governance.evidence.boundary import resolve_repository_root
from digital_state.governance.evidence.engine import EvidenceValidationEngine
from digital_state.governance.evidence.report import EvidenceReportGenerator
from digital_state.governance.evidence.kernel_bridge import KernelEvidenceBridge

__version__ = "1.13.0"

__all__ = [
    "EvidenceType",
    "EvidenceBoundary",
    "EvidenceClassification",
    "EvidenceRecord",
    "resolve_repository_root",
    "EvidenceValidationEngine",
    "EvidenceReportGenerator",
    "KernelEvidenceBridge",
]

