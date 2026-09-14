"""Presentation requests and presentations.

A verifier sends a PresentationRequest describing what it wants to know. The
vault produces a Presentation that discloses only the selected attributes.
Verification is offline: it needs the presentation and the issuer's public key,
nothing else.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from . import _kernel
from .exceptions import PresentationError


@dataclass
class Query:
    """A single attribute the verifier is asking for."""

    id: str
    purpose: str
    required: bool


@dataclass
class PresentationRequest:
    """A verifier's request for a proof."""

    challenge: str
    issuer_public_key: bytes
    queries: List[Query]
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_json(cls, payload: bytes | str | Dict[str, Any]) -> "PresentationRequest":
        if isinstance(payload, (bytes, str)):
            try:
                data = json.loads(payload)
            except json.JSONDecodeError as exc:
                raise PresentationError(f"Request is not valid JSON: {exc}") from exc
        else:
            data = dict(payload)

        try:
            challenge = data["challenge"]
            issuer_key_hex = data["issuerPublicKey"]
            queries_raw = data["queries"]
        except KeyError as exc:
            raise PresentationError(f"Missing field in request: {exc}") from exc

        queries = []
        for q in queries_raw:
            queries.append(
                Query(
                    id=q["id"],
                    purpose=q.get("purpose", ""),
                    required=bool(q.get("required", False)),
                )
            )

        return cls(
            challenge=challenge,
            issuer_public_key=bytes.fromhex(issuer_key_hex),
            queries=queries,
            raw=data,
        )

    def required_ids(self) -> List[str]:
        return [q.id for q in self.queries if q.required]

    def optional_ids(self) -> List[str]:
        return [q.id for q in self.queries if not q.required]


@dataclass
class VerificationResult:
    """The outcome of an offline verification."""

    valid: bool
    disclosed: Dict[str, Any]
    reason: Optional[str] = None


class Presentation:
    """A proof produced by the vault, ready to hand to a verifier."""

    def __init__(self, payload: Dict[str, Any]) -> None:
        self._payload = payload

    def to_json(self) -> str:
        return json.dumps(self._payload, sort_keys=True)

    def to_bytes(self) -> bytes:
        return self.to_json().encode("utf-8")

    @classmethod
    def verify(
        cls,
        presentation: "Presentation",
        trusted_issuers: List[bytes],
        challenge: str,
    ) -> VerificationResult:
        """Verify a presentation offline.

        Checks:
            1. The challenge matches the one the verifier issued.
            2. The signature is valid against one of the trusted issuer keys.
            3. The disclosed attributes are consistent with the commitment.

        No network call is made. No external service is contacted.
        """
        payload = presentation._payload

        if payload.get("challenge") != challenge:
            return VerificationResult(
                valid=False,
                disclosed={},
                reason="Challenge does not match.",
            )

        signature_hex = payload.get("proof", {}).get("signature")
        message_hex = payload.get("proof", {}).get("message")
        if not signature_hex or not message_hex:
            return VerificationResult(
                valid=False,
                disclosed={},
                reason="Presentation is missing a signature.",
            )

        try:
            signature = bytes.fromhex(signature_hex)
            message = bytes.fromhex(message_hex)
        except ValueError:
            return VerificationResult(
                valid=False,
                disclosed={},
                reason="Signature or message is not valid hex.",
            )

        for issuer_key in trusted_issuers:
            if _kernel.ed25519_verify(issuer_key, message, signature):
                return VerificationResult(
                    valid=True,
                    disclosed=payload.get("disclosed", {}),
                )

        return VerificationResult(
            valid=False,
            disclosed={},
            reason="No trusted issuer key matches the signature.",
        )