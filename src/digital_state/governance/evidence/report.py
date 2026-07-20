"""Evidence Report & Manifest Generator (v1.12.0-evidence).

Produces reproducible Markdown evidence tables and machine-readable JSON manifests.
"""

import json
from typing import List, Dict, Any
from digital_state.governance.evidence.models import EvidenceRecord
from digital_state.governance.evidence.engine import EvidenceValidationEngine


class EvidenceReportGenerator:
    """Generates dual-format evidence reports (Markdown Audit Table and JSON Manifest)."""

    def __init__(self, validation_engine: EvidenceValidationEngine = None):
        self.engine = validation_engine or EvidenceValidationEngine()

    def render_markdown_table(self, records: List[EvidenceRecord]) -> str:
        """Renders standardized GitHub-flavored Markdown evidence table."""
        validated = self.engine.validate_batch(records)
        lines = [
            "| Statement | Evidence Type | Boundary | Source | Classification | Justification |",
            "|---|---|---|---|:---:|---|",
        ]
        for rec in validated:
            ref_str = f" (`{rec.repo_path}`)" if rec.repo_path else f" ({rec.doc_ref})" if rec.doc_ref else ""
            source_cell = f"{rec.source}{ref_str}"
            lines.append(
                f"| **{rec.statement}** | {rec.evidence_type.value} | {rec.boundary.value} | {source_cell} | **{rec.classification.value}** | {rec.justification} |"
            )
        return "\n".join(lines)

    def render_json_manifest(self, records: List[EvidenceRecord]) -> str:
        """Renders structured machine-readable JSON evidence manifest."""
        validated = self.engine.validate_batch(records)
        manifest_data: Dict[str, Any] = {
            "schema_version": "v1.0",
            "total_records": len(validated),
            "records": [rec.to_dict() for rec in validated]
        }
        return json.dumps(manifest_data, indent=2)
