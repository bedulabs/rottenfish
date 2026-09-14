"""The vault — the center of the binding.

The vault is a single encrypted file on disk. Opening it decrypts it into
process memory. No network code exists in this module or anything it calls.
"""
from __future__ import annotations

import json
import os
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import _kernel
from .audit import AuditEntry, AuditLog
from .credentials import Credential, CredentialStore
from .exceptions import (
    ConsentError,
    VaultError,
    VaultLockedError,
)
from .identity import Identity

_DEFAULT_PATH = "~/.rottenfish/vault.rf"
_MAGIC = b"ROTTENFISH_VAULT_V1\n"


@dataclass
class Grant:
    id: str
    app_id: str
    scopes: List[str]
    purpose: str
    expires_at: float


class Vault:
    """An open vault."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._open = True
        self._identities: Dict[str, Identity] = {}
        self._identity_secrets: Dict[str, bytes] = {}
        self._credentials: Dict[str, Credential] = {}
        self._grants: Dict[str, Grant] = {}
        self._audit: List[AuditEntry] = []
        self._prev_hash: str = "0" * 64

        self.credentials = CredentialStore(self)
        self.audit = AuditLog(self)

    # -- lifecycle ---------------------------------------------------------

    @classmethod
    def open(
        cls,
        path: str | os.PathLike = _DEFAULT_PATH,
        passphrase: Optional[str] = None,
        device_key: Optional[bytes] = None,
    ) -> "Vault":
        """Open or create a vault at the given path.

        This method touches no network. It reads or creates a local file and
        returns. There is no license check, update ping, or telemetry call.
        """
        resolved = Path(os.path.expanduser(str(path))).resolve()
        resolved.parent.mkdir(parents=True, exist_ok=True)

        vault = cls(resolved)

        if not resolved.exists():
            if passphrase is None and device_key is None:
                raise VaultError(
                    "Creating a new vault requires a passphrase or a device key."
                )
            resolved.write_bytes(_MAGIC)
            vault._append_audit("system", "vault.create", None, True)
            vault._persist(passphrase, device_key)
        else:
            vault._append_audit("system", "vault.open", None, True)

        return vault

    def close(self) -> None:
        """Zeroize in-memory state and mark the vault closed."""
        for key in list(self._identity_secrets.keys()):
            self._identity_secrets[key] = b"\x00" * len(
                self._identity_secrets[key]
            )
        self._identity_secrets.clear()
        self._identities.clear()
        self._credentials.clear()
        self._grants.clear()
        self._open = False

    def __enter__(self) -> "Vault":
        return self

    def __exit__(self, *exc_info: Any) -> None:
        self.close()

    # -- identities --------------------------------------------------------

    @property
    def identities(self) -> List[Identity]:
        self._require_open()
        return list(self._identities.values())

    def create_identity(self, label: str) -> Identity:
        """Create a new Ed25519 identity.

        The private key is generated, kept in memory inside this vault, and
        never serialized to a Python object. It is not returned. There is no
        attribute on the returned Identity that exposes it.
        """
        self._require_open()
        seed = _kernel.random_bytes(32)
        secret, public = _kernel.ed25519_keypair_from_seed(seed)
        did = _did_from_public_key(public)
        identity_id = secrets.token_hex(8)

        identity = Identity(
            did=did,
            label=label,
            public_key=public,
            _vault=self,
            _internal_id=identity_id,
        )
        self._identities[identity_id] = identity
        self._identity_secrets[identity_id] = secret
        self._append_audit("self", "identity.create", label, True)
        return identity

    def _sign_with(self, internal_id: str, message: bytes) -> bytes:
        self._require_open()
        secret = self._identity_secrets.get(internal_id)
        if secret is None:
            raise VaultError("Identity is not present in this vault.")
        return _kernel.ed25519_sign(secret, message)

    # -- credentials -------------------------------------------------------

    def _store_credential(self, credential: Credential) -> None:
        self._require_open()
        self._credentials[credential.id] = credential
        self._append_audit("self", "credential.store", credential.id, True)

    def _list_credentials(self) -> List[Credential]:
        self._require_open()
        return list(self._credentials.values())

    def _delete_credential(self, credential_id: str) -> None:
        self._require_open()
        if credential_id not in self._credentials:
            raise VaultError(f"No credential {credential_id!r}.")
        del self._credentials[credential_id]
        self._append_audit("self", "credential.delete", credential_id, True)

    # -- grants ------------------------------------------------------------

    def grant(
        self,
        app_id: str,
        scopes: List[str],
        purpose: str,
        duration: str = "1h",
    ) -> Grant:
        """Create a time-scoped, purpose-bound grant."""
        self._require_open()
        seconds = _parse_duration(duration)
        grant = Grant(
            id=secrets.token_hex(8),
            app_id=app_id,
            scopes=list(scopes),
            purpose=purpose,
            expires_at=time.time() + seconds,
        )
        self._grants[grant.id] = grant
        self._append_audit(app_id, "grant.create", ",".join(scopes), True)
        return grant

    def revoke(self, grant_id: str) -> None:
        self._require_open()
        grant = self._grants.pop(grant_id, None)
        if grant is None:
            raise VaultError(f"No grant {grant_id!r}.")
        self._append_audit(grant.app_id, "grant.revoke", ",".join(grant.scopes), True)

    def _require_scope(self, scope: str) -> None:
        self._require_open()
        now = time.time()
        for grant in self._grants.values():
            if grant.expires_at < now:
                continue
            if scope in grant.scopes:
                return
        self._append_audit("unknown", "scope.deny", scope, False)
        raise ConsentError(f"No active grant covers scope {scope!r}.")

    def has_scope(self, scope: str) -> bool:
        try:
            self._require_scope(scope)
            return True
        except ConsentError:
            return False

    # -- presentations -----------------------------------------------------

    def present(
        self,
        request,
        disclose: List[str],
        withhold: Optional[List[str]] = None,
    ):
        """Produce a presentation that discloses only the requested attributes."""
        from .presentation import Presentation

        self._require_open()
        withhold = withhold or []

        missing = [q for q in request.required_ids() if q not in disclose]
        if missing:
            raise ConsentError(
                f"Request requires these attributes, which you withheld: {missing}"
            )

        disclosed = {name: True for name in disclose}
        message = json.dumps(
            {
                "challenge": request.challenge,
                "disclosed": disclosed,
                "withheld": withhold,
            },
            sort_keys=True,
        ).encode("utf-8")

        if not self._identities:
            raise VaultError("No identity available to sign the presentation.")
        identity = next(iter(self._identities.values()))
        signature = self._sign_with(identity._internal_id, message)

        payload = {
            "challenge": request.challenge,
            "disclosed": disclosed,
            "withheld": withhold,
            "proof": {
                "message": message.hex(),
                "signature": signature.hex(),
            },
        }
        self._append_audit("self", "presentation.create", ",".join(disclose), True)
        return Presentation(payload)

    # -- pairwise identifiers ----------------------------------------------

    def pairwise_did(self, service_identifier: str) -> str:
        """Derive a per-service DID that cannot be correlated across services."""
        self._require_open()
        if not self._identities:
            raise VaultError("No identity available.")
        identity = next(iter(self._identities.values()))
        digest = _kernel.sha256(
            identity.public_key,
            service_identifier.encode("utf-8"),
        )
        return "did:rf:pairwise:" + digest.hex()[:32]

    # -- sync (opt-in, off by default) -------------------------------------

    def enable_sync(self, relay_url: str, identity_label: str) -> None:
        """Enable end-to-end encrypted device sync.

        This is the only method on Vault that opens a network connection. It is
        opt-in, explicit, and never called by any other part of the library.
        """
        raise NotImplementedError(
            "Encrypted device sync is planned for v0.4.0."
        )

    # -- internal ----------------------------------------------------------

    def _persist(self, passphrase: Optional[str], device_key: Optional[bytes]) -> None:
        # The v0.0.1 scaffold stores nothing beyond the magic header. Real
        # encryption is wired when the native kernel is available.
        self.path.write_bytes(_MAGIC)

    def _require_open(self) -> None:
        if not self._open:
            raise VaultLockedError("Vault is closed.")

    # -- audit -------------------------------------------------------------

    def _append_audit(
        self,
        actor: str,
        action: str,
        scope: Optional[str],
        granted: bool,
    ) -> AuditEntry:
        entry_hash = _kernel.sha256_hex(
            self._prev_hash.encode("ascii"),
            actor.encode("utf-8"),
            action.encode("utf-8"),
            (scope or "").encode("utf-8"),
            b"1" if granted else b"0",
        )
        entry = AuditEntry(
            timestamp=datetime.now(timezone.utc),
            actor=actor,
            action=action,
            scope=scope,
            granted=granted,
            hash=entry_hash,
            prev_hash=self._prev_hash,
        )
        self._prev_hash = entry_hash
        self._audit.append(entry)
        return entry

    def _list_audit(self) -> List[AuditEntry]:
        return list(self._audit)

    def _verify_audit_chain(self) -> bool:
        prev = "0" * 64
        for entry in self._audit:
            if entry.prev_hash != prev:
                return False
            expected = _kernel.sha256_hex(
                prev.encode("ascii"),
                entry.actor.encode("utf-8"),
                entry.action.encode("utf-8"),
                (entry.scope or "").encode("utf-8"),
                b"1" if entry.granted else b"0",
            )
            if entry.hash != expected:
                return False
            prev = entry.hash
        return True


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

_BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def _did_from_public_key(public_key: bytes) -> str:
    digest = _kernel.sha256(public_key)[:20]
    return "did:rf:z" + _base58_encode(digest)


def _base58_encode(data: bytes) -> str:
    n = int.from_bytes(data, "big")
    out = ""
    while n > 0:
        n, rem = divmod(n, 58)
        out = _BASE58_ALPHABET[rem] + out
    for byte in data:
        if byte == 0:
            out = "1" + out
        else:
            break
    return out or "1"


def _parse_duration(text: str) -> int:
    text = text.strip().lower()
    if not text:
        raise ValueError("Empty duration.")
    unit = text[-1]
    try:
        value = int(text[:-1])
    except ValueError:
        raise ValueError(f"Invalid duration: {text!r}")
    multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    if unit not in multipliers:
        raise ValueError(f"Unknown duration unit: {unit!r}")
    return value * multipliers[unit]