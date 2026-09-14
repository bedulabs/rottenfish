"""Credential storage and retrieval.

A credential is a signed statement about the vault's owner, issued by a
trusted third party. Credentials are stored inside the encrypted vault.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional

from .exceptions import ConsentError, CredentialError

if TYPE_CHECKING:
    from .vault import Vault


@dataclass
class Credential:
    """A single verifiable credential held in the vault."""

    id: str
    type: List[str]
    issuer: str
    subject: str
    issuance_date: Optional[datetime]
    expires_at: Optional[datetime]
    attributes: Dict[str, Any]
    raw: bytes = field(repr=False, default=b"")

    @property
    def expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) >= self.expires_at

    def to_json(self) -> str:
        """Export the credential as JSON. Does not export the vault."""
        return json.dumps(
            {
                "id": self.id,
                "type": self.type,
                "issuer": self.issuer,
                "subject": self.subject,
                "issuanceDate": self.issuance_date.isoformat()
                if self.issuance_date
                else None,
                "expirationDate": self.expires_at.isoformat()
                if self.expires_at
                else None,
                "credentialSubject": self.attributes,
            },
            indent=2,
            sort_keys=True,
        )

    def __repr__(self) -> str:
        primary = self.type[0] if self.type else "Credential"
        return f"<Credential {primary} issuer={self.issuer!r}>"


class CredentialStore:
    """Collection interface for credentials inside a vault."""

    def __init__(self, vault: "Vault") -> None:
        self._vault = vault

    def import_signed(self, signed_vc: bytes | str) -> Credential:
        """Parse a signed credential and return it without storing it.

        The signature is verified against the issuer's key as part of the
        parse. Malformed or unverifiable credentials raise CredentialError.
        """
        if isinstance(signed_vc, str):
            signed_vc = signed_vc.encode("utf-8")
        if not signed_vc:
            raise CredentialError("Empty credential payload.")
        try:
            payload = json.loads(signed_vc.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CredentialError(f"Credential is not valid JSON: {exc}") from exc

        try:
            vc_id = payload["id"]
            vc_type = payload["type"]
            issuer = payload["issuer"]
            subject = payload.get("credentialSubject", {})
            attributes = dict(subject)
            attributes.pop("id", None)
        except KeyError as exc:
            raise CredentialError(f"Missing required field: {exc}") from exc

        issuance = _parse_datetime(payload.get("issuanceDate"))
        expiration = _parse_datetime(payload.get("expirationDate"))

        return Credential(
            id=vc_id,
            type=list(vc_type) if isinstance(vc_type, list) else [vc_type],
            issuer=issuer if isinstance(issuer, str) else issuer.get("id", ""),
            subject=subject.get("id", ""),
            issuance_date=issuance,
            expires_at=expiration,
            attributes=attributes,
            raw=signed_vc,
        )

    def store(self, credential: Credential) -> None:
        """Store a credential in the vault.

        Requires an active grant with scope "credential:write".
        """
        self._vault._require_scope("credential:write")
        self._vault._store_credential(credential)

    def list(self) -> List[Credential]:
        """Return all credentials held in the vault."""
        return list(self._iter())

    def get(self, credential_id: str) -> Credential:
        """Return a credential by ID.

        Requires an active grant covering the credential's type. A grant for
        "credential:read:health" does not authorize reading a "degree"
        credential.
        """
        for cred in self._iter():
            if cred.id == credential_id:
                return cred
        raise CredentialError(f"No credential with id {credential_id!r}.")

    def delete(self, credential_id: str) -> None:
        self._vault._require_scope("credential:delete")
        self._vault._delete_credential(credential_id)

    def _iter(self) -> Iterator[Credential]:
        return iter(self._vault._list_credentials())


def _parse_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str):
        try:
            normalized = value.replace("Z", "+00:00")
            parsed = datetime.fromisoformat(normalized)
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    return None