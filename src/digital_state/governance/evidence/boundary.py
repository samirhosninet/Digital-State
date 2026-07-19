"""Boundary Taxonomy & Dynamic Workspace Resolution (v1.12.0-evidence).

Provides repository-independent root resolution and boundary taxonomy classification.
"""

from pathlib import Path
from typing import Optional
from digital_state.governance.evidence.models import EvidenceBoundary


def resolve_repository_root(start_path: Optional[Path] = None) -> Path:
    """Dynamically resolves root of active workspace repository without hardcoded paths."""
    curr = (start_path or Path.cwd()).resolve()
    for parent in [curr] + list(curr.parents):
        if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
            return parent.resolve()
    return curr.resolve()


def classify_boundary(path_or_ref: str) -> EvidenceBoundary:
    """Classifies source path or reference into canonical EvidenceBoundary."""
    ref_lower = path_or_ref.lower()
    if "pep " in ref_lower or "pypa" in ref_lower or "wheel" in ref_lower or "setuptools" in ref_lower:
        return EvidenceBoundary.PYTHON_PACKAGING_SPEC
    elif "hermes" in ref_lower or "nousresearch" in ref_lower:
        return EvidenceBoundary.HERMES_AGENT_FRAMEWORK
    elif "desktop" in ref_lower or "electron" in ref_lower or "os " in ref_lower:
        return EvidenceBoundary.EXTERNAL_PLATFORM
    else:
        return EvidenceBoundary.DIGITAL_STATE_REPOSITORY
