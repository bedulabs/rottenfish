"""Audit log entries.

Every read, write, grant, revocation, and denied operation produces an entry
in the vault's append-only, hash-chained audit log. The log lives inside the
encrypted vault. It is never transmitted anywhere.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class AuditEntry:
    """A single immutable audit record."""

    timestamp: datetime
    actor: str
    action: str
    scope: Optional[str]
    granted: bool
    hash: str
    prev_hash: str

    def __repr__(self) -> str:
        outcome = "allow" if self.granted else "deny"
        return (
            f"<AuditEntry {self.timestamp.isoformat()} "
            f"{self.actor} {self.action} {self.scope or '-'} {outcome}>"
        )


class AuditLog:
    """Read-only view of the vault's audit log."""

    def __init__(self, vault) -> None:
        self._vault = vault

    def tail(self, n: int = 20) -> list[AuditEntry]:
        """Return the most recent n entries, newest last."""
        entries = self._vault._list_audit()
        return entries[-n:]

    def all(self) -> list[AuditEntry]:
        return list(self._vault._list_audit())

    def verify_chain(self) -> bool:
        """Recompute the hash chain and confirm no entry was altered."""
        return self._vault._verify_audit_chain()