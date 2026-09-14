# Rotten Fish — Python Binding

[![PyPI version](https://img.shields.io/pypi/v/rottenfish.svg)](https://pypi.org/project/rottenfish/)
[![Python versions](https://img.shields.io/pypi/pyversions/rottenfish.svg)](https://pypi.org/project/rottenfish/)
[![License](https://img.shields.io/pypi/l/rottenfish.svg)](https://github.com/bedulabs/rottenfish/blob/master/LICENSE.txt)
[![Publish](https://github.com/bedulabs/rottenfish/actions/workflows/publish_pip.yml/badge.svg?branch=binding-python)](https://github.com/bedulabs/rottenfish/actions/workflows/publish_pip.yml)
[![Status](https://img.shields.io/badge/status-pre--alpha-orange.svg)](https://github.com/bedulabs/rottenfish)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/bedulabs/rottenfish/pulls)

> The Python binding for Rotten Fish — a universal, decentralized identity and data-ownership layer.

---

## Table of Contents

- [Status](#status)
- [What This Is](#what-this-is)
- [What This Is Not](#what-this-is-not)
- [Why This Exists](#why-this-exists)
- [How It Works](#how-it-works)
  - [The Vault](#the-vault)
  - [Keys](#keys)
  - [Credentials](#credentials)
  - [Selective Disclosure](#selective-disclosure)
  - [Offline Verification](#offline-verification)
  - [Consent and the Audit Log](#consent-and-the-audit-log)
  - [There Is No Server](#there-is-no-server)
- [The Privacy Model in Depth](#the-privacy-model-in-depth)
  - [Deny by Default](#deny-by-default)
  - [No Ambient Authority](#no-ambient-authority)
  - [No Phone Home](#no-phone-home)
  - [Pairwise Identifiers](#pairwise-identifiers)
  - [On Cameras, Microphones, and Hardware](#on-cameras-microphones-and-hardware)
  - [On Background Uploads](#on-background-uploads)
  - [On Network Surveillance](#on-network-surveillance)
- [What Rotten Fish Blocks](#what-rotten-fish-blocks)
- [What Rotten Fish Does Not Block](#what-rotten-fish-does-not-block)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Overview](#api-overview)
- [Cryptographic Primitives](#cryptographic-primitives)
- [Threat Model](#threat-model)
- [Roadmap for This Branch](#roadmap-for-this-branch)
- [Contributing](#contributing)
- [License](#license)

---

## Status

**Pre-alpha.** This branch is a scaffold. The API shown in this document is the design target for `v0.1.0`. `v0.0.1` exists only to prove the publish pipeline works end to end.

If you are reading this to evaluate the project: read the [How It Works](#how-it-works) and [Privacy Model](#the-privacy-model-in-depth) sections. They describe the design, not shipped code. The design is the part worth arguing about right now.

If you want to help build it, see [Contributing](#contributing).

---

## What This Is

`rottenfish` is the Python binding for the Rotten Fish identity kernel. It gives Python programs the ability to:

- Create and hold cryptographic identities that the user controls
- Store verifiable credentials in an encrypted local vault
- Present a proof of a credential to a verifier, disclosing only chosen attributes
- Verify a presented credential offline, with no network call and no central authority
- Log every access to identity data in a tamper-evident audit trail
- Grant and revoke time-scoped, purpose-bound access to vault data

It is a library, not a service. It runs in your process. It has no daemon, no background worker, and no network listener.

---

## What This Is Not

- **Not an app.** There is no UI, no account, no sign-up.
- **Not a blockchain.** No tokens, no consensus, no global ledger.
- **Not a government ID.** It holds credentials issued by whoever you choose to trust.
- **Not a password manager.** It does not store logins for other services.
- **Not a VPN or Tor client.** It does not hide your IP address or your traffic patterns.
- **Not a rootkit.** It cannot control your hardware, your OS, or other applications.

The last point matters enough that it gets its own section: [On Cameras, Microphones, and Hardware](#on-cameras-microphones-and-hardware).

---

## Why This Exists

**2.8 billion people have no recognized digital identity.** They cannot open a bank account, receive aid, enroll in school, or vote in digital elections. Not because they lack an identity in the human sense, but because the systems that gate access to modern life require a document or a database entry they do not have.

**Everyone else has their identity scattered across platforms they do not control.** One study found that 60% of organizations report over 21 separate identities per user. Your birthdate sits in a dozen corporate databases. Your medical records sit in a dozen more. You did not consent to most of those copies, you cannot see them, and you cannot delete them.

The existing answers are all partial:

- **Centralized identity** puts control in institutions, not people.
- **Self-sovereign identity** promised a fix but stalled on fragmented standards and unusable tooling.
- **Biometric systems** create new risks of surveillance and irreversible breach.
- **Blockchain identity** is siloed, expensive, and does not solve the trust problem.

Rotten Fish takes a different position: identity is not a database row. It is a keypair. Data ownership is not a policy. It is a file on your device that no one else can read.

---

## How It Works

### The Vault

The vault is the center of everything. It is a single encrypted file on disk, owned by the user, readable only with the user's passphrase or device-held key.

```python
from rottenfish import Vault

vault = Vault.open("~/.rottenfish/vault.rf", passphrase=os.environ["RF_PASSPHRASE"])
```

`Vault.open` does exactly one thing: it decrypts the vault into memory. It does not connect to a network. It does not check for updates. It does not phone home. There is no code path in the open sequence that touches a socket.

Inside the vault:

- Identity keypairs
- Issued credentials
- Consent grants
- The audit log
- User preferences and metadata

All of it is encrypted at rest. The file on disk is ciphertext. Copying the file gives an attacker nothing without the passphrase or the device key.

### Keys

An identity is a keypair. The private key never leaves the vault, in the same sense that a private key never leaves an HSM: no API returns it, no serialization writes it, no log records it.

```python
identity = vault.create_identity(label="personal")
print(identity.did)          # did:rf:z6Mk...
print(identity.public_key)   # bytes
# identity.private_key does not exist. It is never exposed.
```

Signing happens inside the vault boundary:

```python
signature = identity.sign(b"some message")
```

The binding holds an opaque handle. The kernel performs the operation. The private key exists only in kernel memory, is zeroized after use, and is never serialized into Python objects.

This matters because Python is a garbage-collected language where memory is copied freely. If the private key were a `bytes` object, it would be duplicated by the interpreter, survive in memory after deletion, and potentially leak through a traceback or a debugger. Keeping it inside the kernel eliminates that entire class of bug.

### Credentials

A credential is a signed statement by an issuer about a subject. The W3C Verifiable Credentials data model is the base. A university signs "this person holds a degree in physics." A government signs "this person is a resident." A clinic signs "this person has completed a vaccination course."

The subject of the credential holds it in their vault.

```python
vc = vault.credentials.import_signed(signed_vc_json)
vault.credentials.store(vc)

for cred in vault.credentials.list():
    print(cred.type, cred.issuer, cred.expires_at)
```

The issuer does not keep a copy that can be used to track you. The credential is yours. You present it when you choose.

### Selective Disclosure

This is the part that changes the privacy math.

Traditional verification: a bar checks your ID, learns your name, birthdate, address, and license number, and copies all of it into a database. The bar did not need any of that. It needed one bit: are you over 18?

With selective disclosure, you prove the predicate without revealing the data.

```python
from rottenfish import PresentationRequest

request = PresentationRequest.from_json(verifier_request_json)

for query in request.queries:
    print(query.id, query.purpose, query.required)
# age_over_18  "Entry to licensed premises"  True
# full_name    "Marketing"                    False
# address      "Marketing"                    False

presentation = vault.present(
    request,
    disclose=["age_over_18"],
    withhold=["full_name", "address", "birthdate"],
)
```

The verifier receives a proof that says "the holder of this credential is over 18" and nothing else. No birthdate. No name. No address. No stable identifier that could be used to link this visit to the next one.

The cryptography that makes this possible is BBS+ signatures over the credential's attributes, or SD-JWT with salted disclosures where BBS+ is not available. Either way, the verifier can check the issuer's signature on the full credential without seeing the hidden attributes.

### Offline Verification

The verifier does not call an API. There is no revocation server to be down, no issuer endpoint to be DDoSed, no central authority that must be online for you to prove who you are.

```python
from rottenfish import Presentation

result = Presentation.verify(
    presentation,
    trusted_issuers=[issuer_public_key],
    challenge=verifier_nonce,
)

print(result.valid)        # True
print(result.disclosed)    # {"age_over_18": True}
```

The verifier needs two things: the presentation itself, and the issuer's public key. The public key can be cached, shipped with the verifier's software, or fetched once and pinned. After that, verification works on a plane, in a refugee camp, in a disaster zone with no connectivity.

This is what makes Rotten Fish usable in the places that need it most.

The `challenge` parameter is a nonce from the verifier. It prevents replay: a recorded presentation from yesterday will not validate against today's challenge.

### Consent and the Audit Log

Every read of vault data is a grant. A grant has a scope, a duration, and a stated purpose. There is no such thing as an implicit read.

```python
grant = vault.grant(
    app_id="com.example.clinic",
    scopes=["credential:read:health"],
    purpose="Appointment check-in",
    duration="1h",
)

# Later, or on a schedule
vault.revoke(grant.id)
```

The audit log records every grant, every use, every denial, and every revocation. It is append-only and hash-chained, so tampering with an earlier entry invalidates every entry after it.

```python
for entry in vault.audit.tail(20):
    print(entry.timestamp, entry.actor, entry.action, entry.scope)
# 2026-09-14T10:02:11Z  com.example.clinic  read   credential:health
# 2026-09-14T10:02:11Z  com.example.clinic  read   credential:identity
# 2026-09-14T10:03:47Z  com.example.maps    deny   credential:identity
```

The audit log is local. It is not uploaded anywhere. It is yours to read and yours to delete.

### There Is No Server

There is no `rottenfish.com` that your library talks to. There is no telemetry endpoint, no license check, no update ping, no crash reporter.

This is not a policy. It is an architectural constraint. The library has no network code in the core paths. If you want sync, you opt in to a separate, explicit module. If you want to publish your DID document, you do it through your own hosting.

The consequence: there is no Rotten Fish honeypot. There is nothing to breach. There is no database of 2.8 billion identities waiting to be leaked, because that database does not exist.

---

## The Privacy Model in Depth

### Deny by Default

Nothing is readable until a grant exists. An application that holds a reference to your vault object still cannot read a credential until you have created a grant that covers it.

```python
try:
    vault.credentials.get("health-record")
except PermissionError as e:
    print(e)  # "No active grant covers credential:read:health"
```

Grants expire. A grant created for a one-hour appointment stops working after one hour. There is no "remember this device forever" default.

### No Ambient Authority

Ambient authority is the property of a system where holding a reference is the same as having permission. POSIX file handles have ambient authority. So do most Python objects.

Rotten Fish does not. Holding a handle to a credential gives you nothing. Every operation checks a capability that must have been granted explicitly.

This is the object-capability model applied to identity data. It means that a compromised dependency in your Python process — a malicious library that found its way into your import graph — cannot read the vault just because it has a reference to the vault object. It needs a grant. You did not create one for it. It fails.

### No Phone Home

The library makes no outbound connections unless you explicitly call a function that does.

There is no analytics. There is no usage reporting. There is no "anonymous telemetry to improve the product." The maintainers cannot see how you use the library, because there is nothing that reports back.

Verify this yourself:

```bash
pip install rottenfish
python -c "import rottenfish; print(rottenfish.__file__)"
# Then read every line. It is not large.
```

If a future version ever adds a network call, it will be in a module you must import explicitly, and it will be documented here. This is a commitment that can be checked by anyone at any time.

### Pairwise Identifiers

When you interact with a service, you do not present your global identity. You present a pairwise identifier derived from your root identity and the service's identifier.

The result: Service A and Service B cannot collude to discover that you are the same person. Neither can a data broker that buys from both. The link between your identities at different services exists only inside your vault.

```python
service_did = vault.pairwise_did(service_identifier="did:web:clinic.example")
# A different DID for every service. Unlinkable without your vault.
```

This is the property that makes Rotten Fish different from "log in with X" systems, where a single identifier is handed to every relying party and every party can correlate.

### On Cameras, Microphones, and Hardware

Rotten Fish is a userspace Python library. It runs inside your Python process, with the same permissions as that process. It cannot:

- Turn off a camera or microphone
- Control a camera LED
- Prevent another application from using the camera
- Prevent the operating system from accessing hardware
- Block a kernel-level keylogger
- Detect a compromised OS

Any library that claims to do these things from userspace is either exploiting a vulnerability, relying on privileged OS APIs it does not disclose, or lying. The only real controls over cameras and microphones are:

1. OS-level permission systems (Android, iOS, macOS, Windows, Linux portals)
2. Physical hardware shutters and kill switches
3. A hardened operating system with a minimal attack surface
4. Not installing software you do not trust

What Rotten Fish does instead: it guarantees that **if an application uses Rotten Fish to access your identity or personal data, that access is visible, scoped, time-limited, revocable, and logged.** It makes the access that does happen honest. It does not pretend to control access that happens outside its boundary.

Being clear about this boundary is what makes the rest of the security claims credible. A privacy project that claims to stop your camera is not a privacy project. It is marketing.

### On Background Uploads

What Rotten Fish controls:

- The vault has no network code in its open path. `Vault.open` decrypts a local file and returns.
- Sync is a separate, explicit operation. `vault.enable_sync(...)` is required, and it is end-to-end encrypted. Any relay sees ciphertext and nothing else.
- Every read creates an audit entry. You can inspect the tail at any time.
- Grants expire. An application that had access yesterday does not have access today unless you renewed it.

What Rotten Fish does not control:

- Another application uploading data it collected itself, outside Rotten Fish.
- The operating system uploading telemetry.
- A browser uploading a form you typed into.
- A cloud backup agent copying files off your disk.

Rotten Fish protects the data inside its boundary. It does not protect data outside it. No userspace library can. The honest framing is: Rotten Fish makes your identity and personal data stay inside a boundary you control. Everything outside that boundary is a separate problem, and pretending otherwise would be dishonest.

### On Network Surveillance

Rotten Fish encrypts data at rest and, when sync is enabled, in transit. It does not hide:

- Your IP address
- Your traffic volume
- Your traffic timing
- The fact that you connected to a particular relay

Traffic analysis is outside the scope of this project. If you need network-level anonymity, use Tor. Rotten Fish and Tor are complementary: Rotten Fish keeps your identity data private, Tor keeps your network metadata private.

---

## What Rotten Fish Blocks

| Threat | How |
|---|---|
| Silent reads of your identity data by an app using the vault | Deny-by-default; every read requires an unexpired grant |
| Over-sharing during verification | Selective disclosure; the verifier sees only the predicate you chose |
| Correlation of your identity across services | Pairwise DIDs; different identifier per relationship |
| Central honeypot breach | No server; credentials live only in your encrypted vault |
| Replay of a recorded presentation | Verifier challenge nonce; presentations are not reusable |
| Issuer tracking where you used a credential | BBS+ signatures; the issuer cannot see individual presentations |
| Credential theft via cloud backup | Vault is encrypted at rest; backups are ciphertext |
| Malicious dependency reading the vault | No ambient authority; a reference is not a permission |
| Retroactive tampering with access history | Hash-chained append-only audit log |

---

## What Rotten Fish Does Not Block

| Threat | Why not | What to use instead |
|---|---|---|
| Compromised OS or rootkit | Runs in userspace; cannot see below itself | Hardened OS, verified boot, minimal attack surface |
| Camera or microphone access by another app | Hardware is outside the library boundary | OS permissions, physical shutter, hardware kill switch |
| Keylogger capturing your passphrase | Runs in userspace | OS-level input protection, hardware security keys |
| Network-level surveillance | Encrypts content, not metadata | Tor, VPN, mixnet |
| Coerced disclosure (someone forces you to unlock) | Cannot distinguish coercion from consent | Duress modes are on the roadmap |
| An issuer signing a false credential | The signature is valid; the claim may not be | Trust framework for issuers; a separate problem |
| An app that asks you to type data manually | Outside the vault boundary | Do not type your data into untrusted apps |
| Phishing of your passphrase | Social, not technical | Hardware keys, passphrase managers, education |

The second table is longer than the first on purpose. A security document that only lists what a system stops is advertising. One that lists what it does not stop is engineering.

---

## Installation

```bash
pip install rottenfish
```

For development, from this branch:

```bash
git clone https://github.com/bedulabs/rottenfish.git
cd rottenfish
git checkout binding-python
pip install -e ./python
```

Optional extras:

```bash
pip install "rottenfish[sync]"     # end-to-end encrypted device sync
pip install "rottenfish[wasm]"     # WebAssembly kernel for restricted environments
pip install "rottenfish[dev]"      # test and lint tooling
```

Requires Python 3.9 or newer. Python 3.13 is supported.

The binding ships prebuilt wheels for Linux, macOS, Windows, and Android via Termux. If no wheel exists for your platform, `pip` will build from source and needs a C compiler and the Rust toolchain.

---

## Quick Start

Create a vault, make an identity, store a credential, present a proof, verify it offline.

```python
import os
from rottenfish import Vault, PresentationRequest, Presentation

# 1. Open or create a vault. This touches no network.
vault = Vault.open("~/.rottenfish/vault.rf", passphrase=os.environ["RF_PASSPHRASE"])

# 2. Create an identity. The private key never leaves the kernel.
identity = vault.create_identity(label="personal")
print("Your DID:", identity.did)

# 3. Store a credential you received from an issuer.
signed_vc = open("degree.json", "rb").read()
credential = vault.credentials.import_signed(signed_vc)
vault.credentials.store(credential)
print("Stored:", credential.type, "from", credential.issuer)

# 4. A verifier sends a request.
request = PresentationRequest.from_json(open("request.json", "rb").read())

# 5. Inspect what is being asked before answering.
for q in request.queries:
    print(f"{q.id:20} required={q.required}  purpose={q.purpose}")

# 6. Disclose only what is needed. Withhold the rest.
presentation = vault.present(
    request,
    disclose=["degree_awarded"],
    withhold=["full_name", "student_id", "graduation_date"],
)

# 7. The verifier checks it locally. No server, no call home.
result = Presentation.verify(
    presentation,
    trusted_issuers=[request.issuer_public_key],
    challenge=request.challenge,
)
print("Valid:", result.valid)
print("Learned:", result.disclosed)
# Valid: True
# Learned: {'degree_awarded': True}
```

The verifier learned one bit. Not your name, not your student ID, not when you graduated. One bit.

---

## API Overview

The public surface of this binding, at `v0.1.0`:

**Vault**

- `Vault.open(path, passphrase=None, device_key=None)` — open or create a vault
- `Vault.close()` — zeroize in-memory state
- `Vault.identities` — list, create, and manage identities
- `Vault.credentials` — import, store, list, and delete credentials
- `Vault.audit` — read the hash-chained audit log
- `Vault.grant(...)` / `Vault.revoke(...)` — create and revoke consent grants
- `Vault.present(request, disclose, withhold)` — produce a presentation
- `Vault.pairwise_did(service_identifier)` — derive a per-service DID
- `Vault.enable_sync(...)` — opt in to encrypted device sync (separate module)

**Identity**

- `.did` — the decentralized identifier
- `.public_key` — bytes
- `.sign(message)` — sign inside the kernel boundary
- `.label` — human-readable name

**Credential**

- `.type`, `.issuer`, `.subject`, `.expires_at`, `.attributes`
- `.to_json()` — export the credential, not the vault

**Presentation**

- `Presentation.verify(presentation, trusted_issuers, challenge)` — offline verification

**PresentationRequest**

- `.queries` — what the verifier is asking for
- `.issuer_public_key`, `.challenge`

**AuditEntry**

- `.timestamp`, `.actor`, `.action`, `.scope`, `.hash`, `.prev_hash`

The full API reference lives in the docs branch: `github.com/bedulabs/rottenfish/tree/docs`.

---

## Cryptographic Primitives

The Python binding does not implement cryptography. It binds to the Rust kernel, which implements or wraps audited primitives. This is deliberate: rolling your own crypto in a scripting language is a category error.

| Purpose | Primitive |
|---|---|
| Identity signing | Ed25519 |
| Key agreement | X25519 |
| Vault encryption at rest | XChaCha20-Poly1305 |
| Passphrase KDF | Argon2id |
| Selective disclosure | BBS+ signatures, SD-JWT fallback |
| DID method | `did:rf` (native), `did:key`, `did:web` interop |
| Credential format | W3C Verifiable Credentials, JWT and JSON-LD |
| Audit log integrity | SHA-256 hash chain |

The kernel's primitives are documented in the `kernel` branch README. Security review of the kernel is a prerequisite for `v1.0.0`.

---

## Threat Model

This binding assumes:

- The user's device is not already compromised at the OS level
- The passphrase is not known to the adversary
- The kernel binary and its dependencies have not been tampered with
- The issuer's key has been obtained out of band and is trusted

It does not assume:

- That the network is safe
- That any server is honest
- That the verifier is honest
- That the issuer will not attempt to correlate presentations
- That the Python process is free of malicious dependencies

The last point is why the no-ambient-authority model matters. A malicious dependency in your import graph is a realistic threat, and the capability model is the response to it.

For the full analysis, see the `docs` branch.

---

## Roadmap for This Branch

**v0.0.1** — published. Scaffold only. Proves the pipeline.

**v0.1.0** — first working binding. Vault open and close, identity creation, credential import and storage, offline verification. No sync, no selective disclosure, no audit log yet. The API surface above is frozen at this version.

**v0.2.0** — selective disclosure via BBS+. Pairwise DIDs. The privacy math becomes real.

**v0.3.0** — consent grants, the audit log, and the capability model. Deny by default becomes enforceable.

**v0.4.0** — encrypted device sync as an optional extra. Relay sees ciphertext only.

**v1.0.0** — after external security review of the kernel and this binding.

Nothing in this list is a promise. It is a direction. The project moves at the speed of its contributors.

---

## Contributing

This branch needs:

- Python developers to build the binding
- People who know `ctypes` and `cffi` well enough to argue about the FFI boundary
- People who know `pyo3` and can argue the other side
- Test writers, especially for the capability model
- People who will try to break the deny-by-default guarantee
- Documentation writers who can explain selective disclosure to a non-cryptographer
- Translators

Read [CONTRIBUTING.md](https://github.com/bedulabs/rottenfish/blob/master/CONTRIBUTING.md) first. Then pick an issue labeled `good first issue` on this branch.

Every contribution is licensed under MIT. There is no CLA. There is no corporate gatekeeping.

---

## License

MIT. See [LICENSE](https://github.com/bedulabs/rottenfish/blob/master/LICENSEl).

You can use this commercially, fork it, sell it, embed it, and never speak to us again. That is the point.

---

A rotten fish feeds the whole ocean. Build it with us.

`github.com/bedulabs/rottenfish`
