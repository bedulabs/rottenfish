"""FFI boundary to the native Rotten Fish kernel.

The native kernel is a shared library written in Rust. This module is the
single place in the binding where that library is called. Everything else in
the package goes through these functions.

For development before the kernel is built, set ROTTENFISH_DEV_FALLBACK=1 in
the environment. This enables a pure-Python reference implementation that uses
the `cryptography` package. The fallback is not audited, does not zeroize
memory, and does not provide constant-time guarantees. It exists so the Python
side of the project can be developed and tested independently.

To point at a native kernel build, set ROTTENFISH_KERNEL_PATH to the shared
library file.
"""
from __future__ import annotations

import ctypes
import ctypes.util
import hashlib
import os
import secrets
from typing import Optional

from .exceptions import KernelNotFoundError

_FALLBACK_ENV = "ROTTENFISH_DEV_FALLBACK"
_KERNEL_PATH_ENV = "ROTTENFISH_KERNEL_PATH"


def _load_native() -> Optional[ctypes.CDLL]:
    candidates = []
    env_path = os.environ.get(_KERNEL_PATH_ENV)
    if env_path:
        candidates.append(env_path)
    found = ctypes.util.find_library("rottenfish_kernel")
    if found:
        candidates.append(found)
    candidates.extend(
        [
            "librottenfish_kernel.so",
            "librottenfish_kernel.dylib",
            "rottenfish_kernel.dll",
        ]
    )
    for candidate in candidates:
        try:
            return ctypes.CDLL(candidate)
        except OSError:
            continue
    return None


_NATIVE: Optional[ctypes.CDLL] = _load_native()


def _using_fallback() -> bool:
    return _NATIVE is None and os.environ.get(_FALLBACK_ENV) == "1"


def _require_backend() -> None:
    if _NATIVE is not None or _using_fallback():
        return
    raise KernelNotFoundError(
        "Native Rotten Fish kernel not found. Set ROTTENFISH_KERNEL_PATH to "
        "the shared library, or set ROTTENFISH_DEV_FALLBACK=1 for "
        "development-only pure-Python mode. The fallback is not audited and "
        "must never be used in production."
    )


def _crypto():
    """Lazy import of the `cryptography` package, used only by the fallback."""
    try:
        from cryptography.hazmat.primitives.asymmetric import ed25519
        from cryptography.hazmat.primitives import serialization
        return ed25519, serialization
    except ImportError as exc:
        raise KernelNotFoundError(
            "The development fallback requires the `cryptography` package. "
            "Install it with: pip install 'rottenfish[dev]'"
        ) from exc


# ---------------------------------------------------------------------------
# Randomness
# ---------------------------------------------------------------------------

def random_bytes(n: int) -> bytes:
    """Return n cryptographically secure random bytes."""
    _require_backend()
    if _NATIVE is not None:
        buf = ctypes.create_string_buffer(n)
        _NATIVE.rf_random_bytes(buf, ctypes.c_size_t(n))
        return bytes(buf.raw)
    return secrets.token_bytes(n)


# ---------------------------------------------------------------------------
# Ed25519
# ---------------------------------------------------------------------------

def ed25519_keypair_from_seed(seed: bytes) -> tuple[bytes, bytes]:
    """Derive an Ed25519 keypair from a 32-byte seed.

    Returns (secret_key, public_key) as raw bytes.
    """
    _require_backend()
    if len(seed) != 32:
        raise ValueError("seed must be exactly 32 bytes")
    if _NATIVE is not None:
        secret = ctypes.create_string_buffer(32)
        public = ctypes.create_string_buffer(32)
        _NATIVE.rf_ed25519_keypair_from_seed(
            seed, ctypes.c_size_t(32), secret, public
        )
        return secret.raw, public.raw
    ed25519, serialization = _crypto()
    private = ed25519.Ed25519PrivateKey.from_private_bytes(seed)
    public = private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return seed, public


def ed25519_sign(secret_key: bytes, message: bytes) -> bytes:
    """Sign a message with an Ed25519 secret key. Returns 64 raw bytes."""
    _require_backend()
    if _NATIVE is not None:
        sig = ctypes.create_string_buffer(64)
        _NATIVE.rf_ed25519_sign(
            secret_key, ctypes.c_size_t(len(secret_key)),
            message, ctypes.c_size_t(len(message)),
            sig,
        )
        return sig.raw
    ed25519, _ = _crypto()
    private = ed25519.Ed25519PrivateKey.from_private_bytes(secret_key)
    return private.sign(message)


def ed25519_verify(public_key: bytes, message: bytes, signature: bytes) -> bool:
    """Verify an Ed25519 signature. Returns True or False, never raises."""
    _require_backend()
    if _NATIVE is not None:
        result = _NATIVE.rf_ed25519_verify(
            public_key, ctypes.c_size_t(len(public_key)),
            message, ctypes.c_size_t(len(message)),
            signature, ctypes.c_size_t(len(signature)),
        )
        return bool(result)
    ed25519, _ = _crypto()
    try:
        ed25519.Ed25519PublicKey.from_public_bytes(public_key).verify(
            signature, message
        )
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------

def sha256(*chunks: bytes) -> bytes:
    """SHA-256 over the concatenation of all chunks."""
    _require_backend()
    h = hashlib.sha256()
    for chunk in chunks:
        h.update(chunk)
    return h.digest()


def sha256_hex(*chunks: bytes) -> str:
    return sha256(*chunks).hex()


# ---------------------------------------------------------------------------
# Symmetric encryption (used by the vault)
# ---------------------------------------------------------------------------

def aead_encrypt(key: bytes, nonce: bytes, plaintext: bytes, aad: bytes) -> bytes:
    """AEAD encryption.

    The native kernel uses XChaCha20-Poly1305. The fallback uses IETF
    ChaCha20-Poly1305 with the same 32-byte key and a 12-byte nonce, which
    is compatible in shape but not in nonce width. Do not mix ciphertexts
    between the two backends.
    """
    _require_backend()
    if _NATIVE is not None:
        raise NotImplementedError("native AEAD path not yet wired")
    try:
        from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
    except ImportError as exc:
        raise KernelNotFoundError(
            "AEAD requires the `cryptography` package in fallback mode."
        ) from exc
    return ChaCha20Poly1305(key).encrypt(nonce, plaintext, aad)


def aead_decrypt(key: bytes, nonce: bytes, ciphertext: bytes, aad: bytes) -> bytes:
    _require_backend()
    if _NATIVE is not None:
        raise NotImplementedError("native AEAD path not yet wired")
    try:
        from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
    except ImportError as exc:
        raise KernelNotFoundError(
            "AEAD requires the `cryptography` package in fallback mode."
        ) from exc
    return ChaCha20Poly1305(key).decrypt(nonce, ciphertext, aad)


def is_fallback() -> bool:
    """True when the pure-Python development fallback is in use."""
    return _using_fallback()


def backend_name() -> str:
    """Return a short identifier for the active backend."""
    if _NATIVE is not None:
        return "native"
    if _using_fallback():
        return "fallback"
    return "unavailable"