# Contributing to Rotten Fish

First of all, thank you. Rotten Fish is a wicked problem — it touches cryptography, distributed systems, law, usability, and governance. No single person or team can build it alone. Every contribution matters, from a one-character typo fix to a full kernel implementation.

This document explains how to contribute, what we expect, and where to start.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Ways to Contribute](#ways-to-contribute)
- [Finding Your Place](#finding-your-place)
- [Branch Workflow](#branch-workflow)
- [Development Setup](#development-setup)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Documentation Standards](#documentation-standards)
- [Security](#security)
- [Licensing of Contributions](#licensing-of-contributions)
- [Getting Help](#getting-help)

---

## Code of Conduct

This project is governed by the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold it. Please read it before you contribute. Report unacceptable behavior to the contact listed there.

---

## Ways to Contribute

You do not need to be an expert in all of it. Pick a piece. Start small.

**Code**

- Implement or improve the identity kernel
- Build or maintain a language binding
- Write or refine the personal data vault
- Build command-line tooling
- Write tests, benchmarks, or fuzzers
- Audit and harden cryptography
- Improve build and packaging pipelines

**Not code**

- Report bugs and reproduction cases
- Improve documentation, tutorials, and examples
- Translate documentation and UI strings
- Design UX and accessibility improvements
- Review pull requests
- Answer questions in issues and discussions
- Draft or review specifications and RFCs
- Help shape the governance model
- Share the project with someone who might care

---

## Finding Your Place

Each implementation lives on its own branch. Find the area that interests you, check out that branch, and read its own README first.

- **main** — vision, documentation, roadmap, coordination, governance
- **kernel** — the identity kernel in Rust and WebAssembly
- **vault** — the personal data vault
- **cli** — the command-line interface
- **docs** — extended documentation and specifications
- **governance** — governance model, RFCs, and proposals
- **binding-java** — Java binding
- **binding-kotlin** — Kotlin binding
- **binding-python** — Python binding
- **binding-javascript** — JavaScript and TypeScript binding
- **binding-swift** — Swift binding
- **binding-go** — Go binding
- **binding-rust** — Rust binding
- **binding-c** — C and C++ binding

To switch branches:

    git clone https://github.com/bedulabs/rottenfish.git
    cd rottenfish
    git checkout kernel

If your language or platform is not listed, that is an invitation, not a limitation. Open an issue and help us add it.

Look for issues labeled:

- **good first issue** — small, well-scoped, beginner friendly
- **help wanted** — we need hands on this
- **needs design** — discussion welcome before code
- **needs review** — a pull request is waiting for eyes

---

## Branch Workflow

The main branch is the coordination hub. It contains the vision, documentation, roadmap, and governance. It does not contain every implementation.

Each implementation has its own branch. Each branch has its own maintainers, its own build system, and its own release cadence.

Rules:

1. Work on the branch that owns the code you are changing.
2. Never push directly to **main** or to another implementation branch. Always open a pull request.
3. Keep pull requests scoped to a single concern. One fix, one feature, one doc change.
4. Rebase on the latest upstream commit before requesting review.
5. If your change affects more than one branch — for example, an API change in the kernel that affects a binding — open one pull request per branch and cross-link them.

Branch naming conventions for your own working branches:

- **feat/short-description** — a new feature
- **fix/short-description** — a bug fix
- **docs/short-description** — documentation only
- **refactor/short-description** — no behavior change
- **test/short-description** — tests only
- **chore/short-description** — build, tooling, dependencies

---

## Development Setup

Setup instructions are branch-specific. Check out the branch you want to work on and read its README.

Common requirements across most branches:

- **Git**
- **A recent stable toolchain for the relevant language** — for example Rust, Go, Node.js, Python, JDK, or Swift
- **A C compiler** — GCC or Clang, required by most bindings
- **WebAssembly tooling** — where relevant to the kernel and web bindings

Before opening a pull request, run the branch's full check suite. Most branches expose a single entry point:

    make check

If a branch does not have one, run the language's standard commands — formatter, linter, and test runner — and state in your pull request what you ran.

---

## Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification. This keeps the history readable and makes automated changelogs possible.

Format:

    <type>(<scope>): <short summary>

    <optional body>

    <optional footer>

Allowed types:

- **feat** — a new feature
- **fix** — a bug fix
- **docs** — documentation only
- **style** — formatting, no code meaning change
- **refactor** — neither fixes a bug nor adds a feature
- **perf** — performance improvement
- **test** — adding or fixing tests
- **build** — build system or dependency changes
- **ci** — continuous integration changes
- **chore** — other changes that do not modify source or tests
- **revert** — reverting a previous commit

Examples:

    feat(kernel): add selective disclosure for age credentials

    fix(binding-python): correct key rotation in offline mode

    docs(main): clarify branch workflow for new contributors

Rules:

- Use the imperative mood in the summary: "add", not "added" or "adds".
- Keep the summary under 72 characters.
- Do not end the summary with a period.
- Reference issues in the footer: "Closes #42".
- Explain **why** in the body, not just what.

---

## Pull Request Process

1. **Open an issue first** for anything larger than a small fix. Discuss the design before writing code. This saves everyone time.
2. **Fork the repository** and create your working branch from the correct upstream branch.
3. **Make your changes.** Keep them focused. Add tests. Update documentation.
4. **Run the checks.** Formatter, linter, and tests must pass.
5. **Open the pull request** against the correct branch, not against main unless the change belongs to main.
6. **Fill out the pull request template completely.** Incomplete pull requests will be asked to update before review.
7. **Respond to review comments.** Push fixes as new commits. Do not force-push during active review unless asked.
8. **Squash on merge.** Maintainers will squash your commits into one clean commit unless the branch history is deliberately multi-commit.

What we look for in review:

- Correctness — does it do what it claims?
- Clarity — can a new contributor understand it in six months?
- Tests — is the new behavior covered?
- Security — does it handle keys, secrets, and untrusted input safely?
- Compatibility — does it break the public API? If so, is it justified and documented?
- Accessibility — does any user-facing change work for everyone?

Review timelines vary. This is a volunteer project. If a pull request has been quiet for more than a week, it is fine to leave a polite comment asking for status.

---

## Coding Standards

Standards are branch-specific and enforced by automated tooling. General expectations across the project:

**All languages**

- Prefer clarity over cleverness.
- Handle errors explicitly. Do not swallow them silently.
- Never log secrets, private keys, or personal data.
- Write tests for new behavior and for every bug you fix.
- Keep functions small and single-purpose.
- Document public APIs.

**Security-critical code**

- Kernel and cryptographic code requires review from at least one maintainer with security experience.
- Avoid rolling your own cryptography. Use well-reviewed, audited libraries.
- Assume all input is hostile, including input from other parts of the system.
- Constant-time comparisons for anything secret-related.
- Zeroize sensitive memory where the language allows it.

**Performance**

- Correctness and security come before performance.
- Include a benchmark or measurement when claiming a performance improvement.
- Avoid premature optimization. Measure first.

**Formatting**

- Every branch has a formatter. Run it before committing.
- Do not reformat unrelated code in the same pull request.

---

## Documentation Standards

- Write for someone who is smart but new. Explain jargon on first use.
- Use plain language. Short sentences. Active voice.
- Every public API needs a description, parameters, return values, and at least one example.
- Keep the README of each branch current. If your change invalidates it, update it in the same pull request.
- Use four-space indented blocks for code samples in Markdown files, not triple backticks, so nested rendering never breaks.
- Include a "why", not just a "how".
- Translations are welcome. Place them next to the original with a language suffix.

---

## Security

**Do not open a public issue for security vulnerabilities.**

If you believe you have found a security vulnerability, report it privately using the process described in [SECURITY.md](SECURITY.md). Include a description, reproduction steps, affected versions or branches, and any suggested mitigation.

We will acknowledge your report, investigate, and coordinate disclosure with you. We will credit you in the advisory unless you prefer to remain anonymous.

Security issues in identity systems can harm real people. Please report responsibly.

---

## Licensing of Contributions

Rotten Fish is released under the MIT License. By submitting a contribution, you agree that your contribution is licensed under the same terms.

You confirm that:

- You wrote the contribution, or you have the right to submit it.
- Your contribution does not knowingly infringe anyone else's rights.
- You are not submitting code you do not have the legal right to license.

Do not paste code from sources with incompatible licenses. If you are adapting code from another project, say so in your pull request and confirm the license is compatible.

---

## Getting Help

- **Questions and ideas:** open a discussion or an issue
- **Bugs:** use the bug report template
- **Feature requests:** use the feature request template
- **New language or platform:** use the branch proposal template
- **Security:** follow SECURITY.md, never a public issue
- **Conduct concerns:** follow CODE_OF_CONDUCT.md

Be kind. Be patient. Be curious. Assume good faith. We are all here because we think the internet should belong to everyone.

Thank you for building Rotten Fish with us.