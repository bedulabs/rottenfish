# Rotten Fish

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/bedulabs/rottenfish?style=flat-square)](https://github.com/bedulabs/rottenfish/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/bedulabs/rottenfish?style=flat-square)](https://github.com/bedulabs/rottenfish/network/members)
[![GitHub Issues](https://img.shields.io/github/issues/bedulabs/rottenfish?style=flat-square)](https://github.com/bedulabs/rottenfish/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/bedulabs/rottenfish?style=flat-square)](https://github.com/bedulabs/rottenfish/pulls)
[![GitHub Contributors](https://img.shields.io/github/contributors/bedulabs/rottenfish?style=flat-square)](https://github.com/bedulabs/rottenfish/graphs/contributors)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://github.com/bedulabs/rottenfish/pulls)
[![Open Source Love](https://badges.frapsoft.com/os/v2/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)

> The missing layer of the internet — a universal, decentralized identity and data-ownership foundation for everyone, on every device, in every language.

---

## Table of Contents

- [What Is Rotten Fish?](#what-is-rotten-fish)
- [The Problem](#the-problem)
- [The Solution](#the-solution)
- [Architecture](#architecture)
  - [The Identity Kernel](#the-identity-kernel)
  - [Language Bindings](#language-bindings)
  - [Platform Packages](#platform-packages)
  - [The Personal Data Vault](#the-personal-data-vault)
  - [Governance Model](#governance-model)
- [Repository Structure and Branches](#repository-structure-and-branches)
- [Supported Languages and Platforms](#supported-languages-and-platforms)
- [Roadmap](#roadmap)
- [Getting Started](#getting-started)
- [Contributing](#contributing)
- [Contributors](#contributors)
- [License](#license)
- [Links](#links)

---

## What Is Rotten Fish?

Rotten Fish is not an app. It is not a single file. It is not a startup product.

Rotten Fish is a **system, a framework, a library, a package, and a kernel** — a full-stack foundation for universal digital identity and personal data ownership. It is being built to run on every platform, in every language, for every person on Earth.

The name is a joke with a point: a rotten fish at the bottom of the ocean feeds an entire ecosystem. It is unseen, unglamorous, and essential. That is what infrastructure should be. That is what Rotten Fish aims to become.

This repository is the **main branch** — the canonical home of the project. It contains the vision, the architecture, the documentation, the roadmap, and the coordination layer. It does not contain every framework implementation. Each framework lives on its own dedicated branch, and each language binding, package, and kernel port has its own home. The main branch is the map; the branches are the territory.

---

## The Problem

Modern life requires digital identity. Healthcare, banking, education, voting, humanitarian aid, employment, and civic participation all depend on being able to prove who you are. Yet the systems we rely on are broken in ways that affect everyone.

**2.8 billion people** have no recognized digital identity at all. They are locked out of the digital economy, unable to open accounts, receive aid, or access services that most of us take for granted.

For those who do have an identity, the situation is barely better. Identities are fragmented across dozens of platforms, each with its own login, its own data silo, its own terms of service. One study found that **60% of organizations report over 21 separate identities per user**. Your data is scattered across corporations and governments, and you have almost no control over who sees it, who uses it, or who profits from it.

Existing attempts to fix this have all fallen short:

- **Centralized identity** (government IDs, corporate logins) puts control in the hands of institutions, not people.
- **Self-sovereign identity (SSI)** promised a fix but stalled on fragmented standards and poor usability.
- **Biometric systems** create new risks of surveillance, exclusion, and irreversible data breaches.
- **Blockchain identity projects** exist, but they are siloed, complex, and lack real-world scale.

No one has built the **kernel-level, cross-platform, multi-language foundation** that makes identity and data ownership work universally. That is the gap Rotten Fish exists to fill.

---

## The Solution

Rotten Fish provides a neutral, open, decentralized foundation for identity and data ownership. It is designed around four principles:

1. **User sovereignty** — your identity and data belong to you, not to a platform, corporation, or government.
2. **Universality** — it works on every device, in every language, for every person.
3. **Interoperability** — it speaks to existing systems, not just to itself.
4. **Neutrality** — no single entity owns or controls the protocol.

Rotten Fish is not trying to replace governments, banks, or platforms. It is trying to give every person a portable, verifiable, self-owned identity and a private vault for their data — so that every other system can build on top of it.

---

## Architecture

Rotten Fish is built in layers. Each layer is independent, replaceable, and exposed through stable interfaces.

### The Identity Kernel

The kernel is the smallest, most secure core of the system. It handles:

- Cryptographic key generation, storage, and rotation
- Verifiable credential issuance, storage, and presentation
- Selective disclosure (for example, proving you are over 18 without revealing your birthdate)
- Offline verification — works without internet access
- Cross-device synchronization without a central server

The kernel is written in a memory-safe systems language and compiled to WebAssembly for portability. It exposes a C ABI so every other language can bind to it.

### Language Bindings

Every major language ecosystem gets a first-class binding that exposes the same core API:

- **Java** — for enterprise, Android, and JVM ecosystems
- **Kotlin** — for modern Android and multiplatform projects
- **Python** — for data science, AI, and rapid prototyping
- **JavaScript and TypeScript** — for web, Node.js, and browser extensions
- **Swift** — for iOS, macOS, and Apple platforms
- **Go** — for cloud infrastructure and command-line tools
- **Rust** — for systems programming and embedded devices
- **C and C++** — for maximum portability and legacy integration

Each binding lives on its own branch. Each binding is maintained by its own team.

### Platform Packages

Rotten Fish ships as native packages for every major distribution channel:

- **pip** for Python
- **npm** for JavaScript and TypeScript
- **Maven Central** for Java and Kotlin
- **Cargo** for Rust
- **Go modules** for Go
- **Swift Package Manager** for Swift
- **Termux** for mobile Linux environments
- **Homebrew, apt, dnf, pacman** for desktop Linux and macOS
- **Standalone CLI** for shell scripts, automation, and power users

### The Personal Data Vault

The vault is where your identity and data live. It runs on your device, not on a central server. It gives you:

- Fine-grained access control — who can see what, for how long, and under what conditions
- Data portability — move your identity and data between platforms without losing anything
- Audit trails — a full record of who accessed your data and why
- Optional encrypted synchronization across your own devices

### Governance Model

This is the hardest layer, and the most important. Rotten Fish is governed by:

- Open standards, not proprietary protocols
- Community governance, not corporate control
- Regulatory compliance built in, not bolted on
- Incentives that align with user interests, not institutional ones

The governance model is still being designed. If you care about digital rights, this is where you can have the most impact.

---

## Repository Structure and Branches

The main branch is the coordination hub. It contains documentation, architecture, roadmap, and governance. It does not contain every implementation.

Each implementation lives on its own branch:

- **main** — vision, documentation, roadmap, coordination
- **kernel** — the identity kernel in Rust and WebAssembly
- **binding-java** — Java binding
- **binding-kotlin** — Kotlin binding
- **binding-python** — Python binding
- **binding-javascript** — JavaScript and TypeScript binding
- **binding-swift** — Swift binding
- **binding-go** — Go binding
- **binding-rust** — Rust binding
- **binding-c** — C and C++ binding
- **vault** — the personal data vault
- **cli** — the command-line interface
- **docs** — extended documentation and specifications
- **governance** — governance model, RFCs, and proposals

If you want to work on a specific language or platform, check out that branch and start there.

---

## Supported Languages and Platforms

Rotten Fish is designed to run everywhere. The goal is universal coverage.

**Languages:** Rust, C, C++, Java, Kotlin, Python, JavaScript, TypeScript, Swift, Go, and more as the community grows.

**Platforms:** Linux, macOS, Windows, Android, iOS, WebAssembly, Termux, embedded systems, and any device with a C compiler.

**Environments:** Browsers, servers, mobile devices, desktops, IoT sensors, offline and online, with or without a network connection.

If your language or platform is not listed, that is an invitation, not a limitation. Open an issue and help us add it.

---

## Roadmap

Rotten Fish is being built in phases. Each phase produces something useful and testable.

**Phase 1 — The Kernel Prototype**
Build the identity kernel in Rust with a C ABI. Get it working on Linux. Compile it to WebAssembly. This is the foundation everything else depends on.

**Phase 2 — First Language Binding**
Pick one language with a large developer community and build a complete binding. Prove that a developer can integrate identity into an app in under 10 lines of code.

**Phase 3 — The Personal Data Vault**
Build the vault as a separate module that uses the kernel for identity. Start with local-only storage, then add optional encrypted sync.

**Phase 4 — Multi-Language Expansion**
Once the API is stable, add bindings for every major language. Use automated tooling to generate bindings from the C ABI.

**Phase 5 — Governance and Standards**
Formalize the governance model. Publish open specifications. Begin the work of adoption, interoperability, and real-world deployment.

---

## Getting Started

Rotten Fish is in early development. The kernel is being designed, the first bindings are being planned, and the governance model is being drafted.

If you want to explore what exists today:

1. Read the architecture section above.
2. Browse the branches to find the area that interests you.
3. Open an issue to introduce yourself and ask questions.
4. Pick a small task and submit a pull request.

If you want to run something locally, clone the repository and check out the branch you want to work on:

    git clone https://github.com/bedulabs/rottenfish.git
    cd rottenfish
    git checkout kernel

Each branch has its own setup instructions in its own README.

---

## Contributing

Rotten Fish is a wicked problem. It touches cryptography, distributed systems, law, usability, and governance. No single person or team can build it alone. We need people from every background.

You do not need to be an expert in all of it. Pick a piece. Start small.

We are actively looking for:

- **Systems and kernel developers** — Rust, C, WebAssembly
- **Language binding maintainers** — Java, Kotlin, Python, JavaScript, TypeScript, Swift, Go, and more
- **Security and cryptography reviewers** — formal verification, threat modeling, audit
- **UX and accessibility designers** — identity systems must be usable by everyone
- **Technical writers and documentation folks** — clarity is a feature
- **Digital rights advocates and governance thinkers** — help shape the rules
- **Translators** — the system must speak every language

Ways to contribute:

- Open an issue with a question, idea, or bug report
- Submit a pull request for a small fix or a new feature
- Review an existing pull request
- Improve documentation
- Translate documentation or UI strings
- Share the project with someone who might care

Before contributing, please read the CONTRIBUTING file on the main branch and follow the code of conduct. Be kind, be patient, be curious.

---

## Contributors

Thank you to everyone who has contributed to Rotten Fish. This project exists because of you.

[![Contributors](https://contrib.rocks/image?repo=bedulabs/rottenfish)](https://github.com/bedulabs/rottenfish/graphs/contributors)

Want to see your name here? Open a pull request. Every contribution counts, from a typo fix to a full kernel implementation.

---

## License

Rotten Fish is released under the MIT License. See the LICENSE file on the main branch for details.

The license is intentionally permissive. The goal is adoption, not control. Anyone should be able to use, modify, and build on Rotten Fish without asking permission.

---

## Links

- **Repository:** https://github.com/bedulabs/rottenfish
- **Issues:** https://github.com/bedulabs/rottenfish/issues
- **Pull Requests:** https://github.com/bedulabs/rottenfish/pulls
- **Discussions:** https://github.com/bedulabs/rottenfish/discussions

---

Built with care, by people who believe the internet should belong to everyone.

A rotten fish feeds the whole ocean. Let us build it together.