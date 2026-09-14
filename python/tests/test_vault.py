import os

import pytest

os.environ.setdefault("ROTTENFISH_DEV_FALLBACK", "1")

from rottenfish import Vault  # noqa: E402
from rottenfish.exceptions import ConsentError, VaultLockedError  # noqa: E402


def test_audit_log_is_hash_chained(tmp_path):
    vault = Vault.open(tmp_path / "vault.rf", passphrase="test")
    vault.create_identity(label="personal")
    vault.grant("app.example", ["credential:read:health"], "check-in", "1h")
    assert vault.audit.verify_chain()
    assert len(vault.audit.all()) >= 2
    vault.close()


def test_deny_by_default_blocks_unscoped_read(tmp_path):
    vault = Vault.open(tmp_path / "vault.rf", passphrase="test")
    vault.create_identity(label="personal")
    with pytest.raises(ConsentError):
        vault._require_scope("credential:read:health")
    vault.close()


def test_grant_allows_scoped_operation(tmp_path):
    vault = Vault.open(tmp_path / "vault.rf", passphrase="test")
    vault.grant("app.example", ["credential:read:health"], "check-in", "1h")
    assert vault.has_scope("credential:read:health")
    assert not vault.has_scope("credential:write")
    vault.close()


def test_close_locks_the_vault(tmp_path):
    vault = Vault.open(tmp_path / "vault.rf", passphrase="test")
    vault.close()
    with pytest.raises(VaultLockedError):
        vault.create_identity(label="personal")


def test_pairwise_dids_differ_per_service(tmp_path):
    vault = Vault.open(tmp_path / "vault.rf", passphrase="test")
    vault.create_identity(label="personal")
    a = vault.pairwise_did("did:web:clinic.example")
    b = vault.pairwise_did("did:web:library.example")
    assert a != b
    assert a.startswith("did:rf:pairwise:")
    vault.close()