class GovernanceError(Exception):
    """Base exception for all Digital State governance kernel errors."""
    pass


class RegistryError(GovernanceError):
    """Raised when registry-related operations fail (e.g., registration conflicts)."""
    pass


class IdentityError(RegistryError):
    """Raised when verification of an agent profile's identity fails."""
    pass


class LifecycleError(GovernanceError):
    """Raised when an invalid transition is attempted in the state machine."""
    pass


class EvidenceError(GovernanceError):
    """Raised when evidence verification fails or evidence integrity is compromised."""
    pass
