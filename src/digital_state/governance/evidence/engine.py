"""Evidence Validation Engine (v1.12.0-evidence).

Programmatically validates evidence records against mandatory governance rules:
    - Rule 1: VERIFIED_ABSENCE requires spec/code proof; doc silence downgrades to NOT_FOUND...
    - Rule 2: External platform behavior without direct evidence becomes UNVERIFIED.
    - Rule 3: REPOSITORY_IMPLEMENTATION evidence validates path existence in workspace or installed package.
    - Rule 4: Mandatory non-empty record fields.
"""

from pathlib import Path
from typing import List, Tuple, Optional
from digital_state.governance.evidence.models import (
    EvidenceRecord,
    EvidenceType,
    EvidenceBoundary,
    EvidenceClassification,
)
from digital_state.governance.evidence.boundary import resolve_repository_root


class EvidenceValidationError(ValueError):
    """Raised when evidence record violates governance invariants."""
    pass


class EvidenceValidationEngine:
    """Enforces evidence governance invariants on evidence records."""

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or resolve_repository_root()

    def validate_record(self, record: EvidenceRecord) -> EvidenceRecord:
        """Validates record fields and enforces classification rules, returning normalized record."""
        # Rule 4: Mandatory non-empty fields
        if not record.statement or not record.statement.strip():
            raise EvidenceValidationError("EvidenceRecord statement cannot be empty.")
        if not record.source or not record.source.strip():
            raise EvidenceValidationError(f"EvidenceRecord ({record.statement}) source cannot be empty.")
        if not record.justification or not record.justification.strip():
            raise EvidenceValidationError(f"EvidenceRecord ({record.statement}) justification cannot be empty.")

        final_classification = record.classification

        # Rule 1: VERIFIED_ABSENCE validation
        if record.classification == EvidenceClassification.VERIFIED_ABSENCE:
            # Requires AUTHORITATIVE_SPECIFICATION or REPOSITORY_IMPLEMENTATION with valid path
            is_valid_spec = record.evidence_type == EvidenceType.AUTHORITATIVE_SPECIFICATION
            is_valid_code = (
                record.evidence_type == EvidenceType.REPOSITORY_IMPLEMENTATION
                and record.repo_path is not None
                and (self.workspace_root / record.repo_path).exists()
            )
            if not (is_valid_spec or is_valid_code):
                # Downgrade doc silence to NOT_FOUND_IN_CURRENT_OFFICIAL_DOCUMENTATION
                final_classification = EvidenceClassification.NOT_FOUND_IN_CURRENT_OFFICIAL_DOCUMENTATION

        # Rule 2: External Boundary Rule
        elif record.boundary in (EvidenceBoundary.HERMES_AGENT_FRAMEWORK, EvidenceBoundary.EXTERNAL_PLATFORM):
            if record.evidence_type == EvidenceType.EXTERNAL_RUNTIME and not record.doc_ref and not record.repo_path:
                final_classification = EvidenceClassification.UNVERIFIED

        # Rule 3: Repository Path Validation
        if record.evidence_type == EvidenceType.REPOSITORY_IMPLEMENTATION and record.repo_path:
            target_path = self.workspace_root / record.repo_path
            if not target_path.exists():
                # Check installed package location fallback for clean machines without repository checkout
                pkg_path = None
                try:
                    import digital_state
                    pkg_root = Path(digital_state.__file__).resolve().parent
                    rel_parts = Path(record.repo_path).parts
                    if "digital_state" in rel_parts:
                        idx = rel_parts.index("digital_state")
                        sub_path = Path(*rel_parts[idx+1:])
                        pkg_path = pkg_root / sub_path
                except Exception:
                    pkg_path = None

                if not (pkg_path and pkg_path.exists()):
                    raise EvidenceValidationError(
                        f"Repository implementation path '{record.repo_path}' does not exist in workspace '{self.workspace_root}'."
                    )

        # Return validated normalized record
        if final_classification != record.classification:
            return EvidenceRecord(
                statement=record.statement,
                evidence_type=record.evidence_type,
                boundary=record.boundary,
                source=record.source,
                classification=final_classification,
                justification=f"[Rule Downgrade] {record.justification}",
                record_id=record.record_id,
                schema_version=record.schema_version,
                repo_path=record.repo_path,
                doc_ref=record.doc_ref,
                commit_sha=record.commit_sha,
                provenance_timestamp=record.provenance_timestamp,
            )

        return record

    def validate_batch(self, records: List[EvidenceRecord]) -> List[EvidenceRecord]:
        """Validates a batch of evidence records, returning normalized records."""
        validated = []
        for rec in records:
            validated.append(self.validate_record(rec))
        return validated
