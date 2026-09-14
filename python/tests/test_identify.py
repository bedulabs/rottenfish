import os

import pytest

os.environ.setdefault("ROTTENFISH_DEV_FALLBACK", "1")

from rottenfish import Vault  # noqa: E402
from rottenfish.identity import Identity  # noqa: E402


def test_create_identity_returns_public_did(tmp_path):
    vault = Vault.open(tmp_path / "vault.rf", passphrase="test")
    identity = vault.create_identity(label="personal")
    assert isinstance(identity, Identity)
    assert identity.did.startswith("did:rf:")
    assert len(identity.public_key) == 32
    vault.close()


def test_private_key_is_not_exposed(tmp_path):
    vault = Vault.open(tmp_path / "vault.rf", passphrase="test")
    identity = vault.create_identity(label="personal")
    assert not hasattr(identity, "private_key")
    assert not hasattr(identity, "secret_key")
    vault.close()


def test_sign_and_verify_roundtrip(tmp_path):
    vault = Vault.open(tmp_path / "vault.rf", passphrase="test")
    identity = vault.create_identity(label="personal")
    message = b"hello, rotten fish"
    signature = identity.sign(message)
    assert identity.verify(message, signature)
    assert not identity.verify(b"tampered", signature)
    vault.close()