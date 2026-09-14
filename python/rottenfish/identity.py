"""Identity objects.

An identity is an Ed25519 keypair. The private key never leaves the vault.
This class holds only the public half and a handle to the vault, and it asks
the vault to perform signing operations on its behalf.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from . import _kernel

if TYPE_CHECKING:
    from .vault import Vault


_DID_PREFIX = "did:rf:"


@dataclass
class Identity:
    """A public-facing identity handle.

    Attributes:
        did: The decentralized identifier, e.g. "did:rf:z6Mk...".
        label: Human-readable name for the identity.
        public_key: The raw Ed25519 public key.
    """

    did: str
    label: str
    public_key: bytes
    _vault: Optional["Vault"] = None
    _internal_id: Optional[str] = None

    def sign(self, message: bytes) -> bytes:
        """Sign a message with this identity's private key.

        The private key is not exposed to Python. The signing operation is
        performed inside the vault, and only the signature is returned.
        """
        if self._vault is None or self._internal_id is None:
            raise ValueError("This identity is not attached to an open vault.")
        return self._vault._sign_with(self._internal_id, message)

    def verify(self, message: bytes, signature: bytes) -> bool:
        """Verify a signature against this identity's public key."""
        return _kernel.ed25519_verify(self.public_key, message, signature)

    def __repr__(self) -> str:
        return f"<Identity {self.label!r} {self.did}>"