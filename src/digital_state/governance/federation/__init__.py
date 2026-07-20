"""Digital State Evidence Federation Subsystem (v1.15.0).

Provides multi-tenant evidence manifest aggregation and remote attestation verification.
"""

from digital_state.governance.federation.manager import FederatedEvidenceManager
from digital_state.governance.federation.attestation import RemoteAttestationVerifier

__all__ = [
    "FederatedEvidenceManager",
    "RemoteAttestationVerifier",
]
