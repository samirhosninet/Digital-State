"""Phase 1 Runtime & Kernel Evidence Binding Bridge (v1.13.0-platform).

Provides additive evidence binding infrastructure for integrating Evidence Governance Engine
with WorkflowKernel and Runtime provisioning without modifying baseline core stores.
"""

from typing import List, Dict, Any, Optional
from digital_state.governance.evidence.models import (
    EvidenceRecord,
    EvidenceType,
    EvidenceBoundary,
    EvidenceClassification,
)
from digital_state.governance.evidence.engine import EvidenceValidationEngine
from digital_state.governance.evidence.report import EvidenceReportGenerator


class KernelEvidenceBridge:
    """Additive bridge connecting Evidence Validation Engine with WorkflowKernel gate decisions."""

    def __init__(self, validation_engine: Optional[EvidenceValidationEngine] = None):
        self.engine = validation_engine or EvidenceValidationEngine()
        self.report_generator = EvidenceReportGenerator(validation_engine=self.engine)

    def create_and_validate_record(
        self,
        statement: str,
        evidence_type: EvidenceType,
        boundary: EvidenceBoundary,
        source: str,
        classification: EvidenceClassification,
        justification: str,
        repo_path: Optional[str] = None,
        doc_ref: Optional[str] = None,
        commit_sha: Optional[str] = None,
    ) -> EvidenceRecord:
        """Instantiates and programmatically validates an EvidenceRecord using engine rules."""
        raw_record = EvidenceRecord(
            statement=statement,
            evidence_type=evidence_type,
            boundary=boundary,
            source=source,
            classification=classification,
            justification=justification,
            repo_path=repo_path,
            doc_ref=doc_ref,
            commit_sha=commit_sha,
        )
        return self.engine.validate_record(raw_record)

    def evaluate_gate_evidence(
        self,
        gate_id: str,
        feature_id: str,
        evidence_records: List[EvidenceRecord],
    ) -> Dict[str, Any]:
        """Evaluates evidence manifest for a WorkflowKernel gate transition.

        Returns structured evaluation payload:
            - gate_id, feature_id
            - is_evidence_satisfied: True if all records are VERIFIED / VERIFIED ABSENCE
            - unverified_count, total_count
            - manifest_json: Machine-readable JSON manifest
            - report_markdown: Human-readable Markdown audit table
        """
        validated_records = self.engine.validate_batch(evidence_records)
        unverified_records = [
            r for r in validated_records
            if r.classification in (EvidenceClassification.UNVERIFIED, EvidenceClassification.NOT_FOUND_IN_CURRENT_OFFICIAL_DOCUMENTATION)
        ]
        is_satisfied = len(unverified_records) == 0

        return {
            "gate_id": gate_id,
            "feature_id": feature_id,
            "is_evidence_satisfied": is_satisfied,
            "total_records": len(validated_records),
            "unverified_count": len(unverified_records),
            "unverified_statements": [r.statement for r in unverified_records],
            "manifest_json": self.report_generator.render_json_manifest(validated_records),
            "report_markdown": self.report_generator.render_markdown_table(validated_records),
        }
