# Rotten Fish — Python Binding

[![PyPI version](https://img.shields.io/pypi/v/rottenfish.svg)](https://pypi.org/project/rottenfish/)
[![Python versions](https://img.shields.io/pypi/pyversions/rottenfish.svg)](https://pypi.org/project/rottenfish/)
[![License](https://img.shields.io/pypi/l/rottenfish.svg)](https://github.com/bedulabs/rottenfish/blob/master/LICENSE.txt)
[![Status](https://img.shields.io/badge/status-pre--alpha-orange.svg)](https://github.com/bedulabs/rottenfish)

> Universal, decentralized identity and data ownership for Python.

This is the Python binding for the Rotten Fish identity kernel. It lets any
Python program create user-controlled cryptographic identities, store verifiable
credentials in an encrypted local vault, present proofs that disclose only
chosen attributes, and verify those proofs offline with no central server.

Full project: https://github.com/bedulabs/rottenfish

---

## Status

**Pre-alpha.** Version `0.0.1` is a scaffold published to prove the release
pipeline. The API below is the design target for `v0.1.0`. Do not use this in
production yet.

If you want to help build it, see the contributing section at the end.

---

## Why This Exists

2.8 billion people have no recognized digital identity. Everyone else has their
identity fragmented across dozens of platforms they do not control. Existing
answers — centralized IDs, biometric databases, self-sovereign identity
projects — are all partial.

Rotten Fish takes a different position: identity is a keypair, not a database
row. Data ownership is a file on your device that no one else can read.

This package brings that foundation to Python.

---

## Installation

```bash
pip install rottenfish
```

Requires Python 3.9 or newer. Prebuilt wheels are provided for Linux, macOS,
Windows, and Android via Termux. If no wheel exists for your platform, `pip`
will build from source and needs a C compiler and the Rust toolchain.

Optional extras:

```bash
pip install "rottenfish[dev]"     # pytest, cryptography, linting tools
pip install "rottenfish[sync]"    # end-to-end encrypted device sync
pip install "rottenfish[wasm]"    # WebAssembly kernel for restricted environments
```

---

## Quick Start

Create a vault, make an identity, grant scoped access, and verify a proof
offline.

```python
import os
from rottenfish import Vault, PresentationRequest, Presentation

# 1. Open or create a vault. This touches no network.
vault = Vault.open("~/.rottenfish/vault.rf", passphrase=os.environ["RF_PASSPHRASE"])

# 2. Create an identity. The private key never leaves the kernel boundary.
identity = vault.create_identity(label="personal")
print("Your DID:", identity.did)

# 3. Grant an application time-scoped access to a specific scope.
vault.grant(
    app_id="com.example.clinic",
    scopes=["credential:read:health"],
    purpose="Appointment check-in",
    duration="1h",
)

# 4. A verifier sends a request describing what it wants to know.
request = PresentationRequest.from_json({
    "challenge": "nonce-from-verifier",
    "issuerPublicKey": identity.public_key.hex(),
    "queries": [
        {"id": "age_over_18", "purpose": "Entry", "required": True},
        {"id": "full_name",   "purpose": "Marketing", "required": False},
    ],
})

# 5. Disclose only what is needed. Withhold everything else.
presentation = vault.present(
    request,
    disclose=["age_over_18"],
    withhold=["full_name"],
)

# 6. The verifier checks it locally. No server, no call home.
result = Presentation.verify(
    presentation,
    trusted_issuers=[identity.public_key],
    challenge="nonce-from-verifier",
)
print("Valid:", result.valid)
print("Learned:", result.disclosed)
```

The verifier learned one bit. Not your name, not your birthdate, not a stable
identifier that could be used to link this visit to the next one.

---

## How It Works

### The Vault

The vault is a single encrypted file on disk, owned by the user, readable only
with the user's passphrase or device key. `Vault.open` decrypts it into memory.
It does not connect to a network. It does not check for updates. It does not
phone home. There is no code path in the open sequence that touches a socket.

### Deny by Default

Every read of vault data is a grant. A grant has a scope, a duration, and a
stated purpose. There is no such thing as an implicit read. An application that
holds a reference to your vault object still cannot read a credential until you
have created a grant that covers it.

```python
try:
    vault.credentials.get("health-record")
except PermissionError as e:
    print(e)  # "No active grant covers credential:read:health"
```

Grants expire. A grant created for a one-hour appointment stops working after
one hour. There is no "remember this device forever" default.

### No Ambient Authority

Holding a handle to a credential gives you nothing. Every operation checks a
capability that must have been granted explicitly. A malicious dependency in
your Python process — a library that found its way into your import graph —
cannot read the vault just because it has a reference to the vault object. It
needs a grant. You did not create one for it. It fails.

### Pairwise Identifiers

When you interact with a service, you do not present your global identity. You
present a pairwise identifier derived from your root identity and the service's
identifier. Service A and Service B cannot collude to discover that you are the
same person. The link exists only inside your vault.

```python
service_did = vault.pairwise_did(service_identifier="did:web:clinic.example")
# A different DID for every service. Unlinkable without your vault.
```

### Offline Verification

The verifier does not call an API. There is no revocation server to be down, no
issuer endpoint to be DDoSed, no central authority that must be online for you
to prove who you are. The verifier needs the presentation and the issuer's
public key. After that, verification works on a plane, in a refugee camp, in a
disaster zone with no connectivity.

### The Audit Log

Every read of vault data is recorded. Every grant, every use, every denial, and
every revocation is appended to a hash-chained audit log inside the vault.

```python
for entry in vault.audit.tail(20):
    print(entry.timestamp, entry.actor, entry.action, entry.scope)
```

The log is local. It is not uploaded anywhere. It is yours to read and yours to
delete.

---

## What This Package Blocks

- Silent reads of identity data by an app using the vault — deny by default
- Over-sharing during verification — selective disclosure
- Correlation of your identity across services — pairwise DIDs
- Central honeypot breach — no server, credentials live only in your vault
- Replay of a recorded presentation — verifier challenge nonce
- Malicious dependency reading the vault — no ambient authority
- Retroactive tampering with access history — hash-chained audit log

## What This Package Does Not Block

- A compromised operating system or rootkit
- Camera or microphone access by other applications
- Kernel-level keyloggers capturing your passphrase
- Network-level surveillance of IP addresses or traffic patterns
- Coercion to unlock the vault (duress modes are on the roadmap)

Rotten Fish is a userspace library. It runs inside your Python process, with
the same permissions as that process. It guarantees that access which happens
*through Rotten Fish* is visible, scoped, time-limited, revocable, and logged.
It does not pretend to control access outside its boundary.

---

## API Overview

The public surface at `v0.1.0`:

**Vault**

- `Vault.open(path, passphrase=None, device_key=None)` — open or create a vault
- `Vault.close()` — zeroize in-memory state
- `Vault.identities` — list, create, and manage identities
- `Vault.credentials` — import, store, list, and delete credentials
- `Vault.audit` — read the hash-chained audit log
- `Vault.grant(...)` / `Vault.revoke(...)` — create and revoke consent grants
- `Vault.present(request, disclose, withhold)` — produce a presentation
- `Vault.pairwise_did(service_identifier)` — derive a per-service DID

**Identity**

- `.did` — the decentralized identifier
- `.public_key` — raw Ed25519 public key bytes
- `.sign(message)` — sign inside the kernel boundary
- `.verify(message, signature)` — verify against this identity's public key

**Credential**

- `.type`, `.issuer`, `.subject`, `.expires_at`, `.attributes`
- `.to_json()` — export the credential, not the vault

**Presentation**

- `Presentation.verify(presentation, trusted_issuers, challenge)` — offline

**PresentationRequest**

- `.queries` — what the verifier is asking for
- `.issuer_public_key`, `.challenge`

**AuditEntry**

- `.timestamp`, `.actor`, `.action`, `.scope`, `.hash`, `.prev_hash`

---

## Cryptographic Primitives

The Python binding does not implement cryptography. It binds to the Rust
kernel, which wraps audited primitives.

| Purpose | Primitive |
|---|---|
| Identity signing | Ed25519 |
| Key agreement | X25519 |
| Vault encryption at rest | XChaCha20-Poly1305 |
| Passphrase KDF | Argon2id |
| Selective disclosure | BBS+ signatures, SD-JWT fallback |
| Credential format | W3C Verifiable Credentials, JWT and JSON-LD |
| Audit log integrity | SHA-256 hash chain |

---

## Roadmap

- **v0.0.1** — published. Scaffold only. Proves the pipeline.
- **v0.1.0** — first working binding. Vault, identity, credential storage, offline verification.
- **v0.2.0** — selective disclosure via BBS+. Pairwise DIDs.
- **v0.3.0** — consent grants, audit log, capability model.
- **v0.4.0** — end-to-end encrypted device sync as an optional extra.
- **v1.0.0** — after external security review of the kernel and this binding.

---

## Contributing

Rotten Fish is a wicked problem. It touches cryptography, distributed systems,
law, usability, and governance. This branch needs Python developers, people who
know `ctypes` and `cffi` well enough to argue about the FFI boundary, test
writers, documentation writers, and translators.

Read the contributing guide:
https://github.com/bedulabs/rottenfish/blob/master/CONTRIBUTING.md

Then pick an issue labeled `good first issue` on the `binding-python` branch.

Every contribution is licensed under MIT. There is no CLA. There is no
corporate gatekeeping.

---

## License

MIT. See https://github.com/bedulabs/rottenfish/blob/master/LICENSE.txt

You can use this commercially, fork it, sell it, embed it, and never speak to
us again. That is the point.

---

A rotten fish feeds the whole ocean. Build it with us.

`github.com/bedulabs/rottenfish`