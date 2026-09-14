"""Rotten Fish — Python binding.

Universal, decentralized identity and data ownership.
See https://github.com/bedulabs/rottenfish for details.
"""
from .audit import AuditEntry
from .credentials import Credential
from .exceptions import (
    ConsentError,
    CredentialError,
    KernelError,
    KernelNotFoundError,
    PresentationError,
    RottenFishError,
    VaultError,
    VaultLockedError,
)
from .identity import Identity
from .presentation import (
    Presentation,
    PresentationRequest,
    Query,
    VerificationResult,
)
from .vault import Grant, Vault

__version__ = "0.0.1"

__all__ = [
    "__version__",
    "AuditEntry",
    "ConsentError",
    "Credential",
    "CredentialError",
    "Grant",
    "Identity",
    "KernelError",
    "KernelNotFoundError",
    "Presentation",
    "PresentationError",
    "PresentationRequest",
    "Query",
    "RottenFishError",
    "Vault",
    "VaultError",
    "VaultLockedError",
    "VerificationResult",
]