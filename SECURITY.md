# Security Policy

Rotten Fish is infrastructure for digital identity and personal data ownership.
Security is not a feature of this project. It is the foundation. A flaw in this
code can expose real people to surveillance, impersonation, identity theft,
financial loss, or physical harm. We take every report seriously and we ask
that you do the same.

This document explains which versions we support, how to report a vulnerability,
what to expect from us, and what we expect from you.

---

## Table of Contents

- [Supported Versions](#supported-versions)
- [Reporting a Vulnerability](#reporting-a-vulnerability)
- [What to Include in Your Report](#what-to-include-in-your-report)
- [What to Expect From Us](#what-to-expect-from-us)
- [Disclosure Policy](#disclosure-policy)
- [Scope](#scope)
- [Out of Scope](#out-of-scope)
- [Severity Guidelines](#severity-guidelines)
- [Safe Harbor](#safe-harbor)
- [Recognition](#recognition)
- [Security Advisories](#security-advisories)
- [Hardening Guidance for Users](#hardening-guidance-for-users)

---

## Supported Versions

Rotten Fish is in early development. Until the project reaches a stable 1.0
release, only the latest commit on each active branch receives security fixes.

| Branch           | Supported          |
| ---------------- | ------------------ |
| main             | Yes                |
| kernel           | Yes                |
| vault            | Yes                |
| cli              | Yes                |
| binding-python   | Yes                |
| binding-rust     | Yes                |
| binding-java     | Yes                |
| binding-kotlin   | Yes                |
| binding-javascript | Yes              |
| binding-go       | Yes                |
| binding-swift    | Yes                |
| binding-c        | Yes                |
| docs             | Not applicable     |
| governance       | Not applicable     |

Older commits, tagged pre-releases, and archived branches are not supported.
If you are running an older version, upgrade to the latest commit on the
relevant branch before reporting.

---

## Reporting a Vulnerability

Do not open a public issue, pull request, discussion, or social media post.
Public disclosure before a fix is available puts every user of Rotten Fish at
risk.

Report privately using one of these channels:

1. GitHub Private Security Advisory (preferred)
   Go to:
   https://github.com/bedulabs/rottenfish/security/advisories/new

2. Email
   security.bedusec@gmail.com

Replace the placeholder email with a real, monitored address before publishing
this file. If you do not have a dedicated security inbox, use a private address
that at least two maintainers can access.

If you are unsure whether something is a vulnerability, report it anyway. We
would rather receive a false positive than miss a real issue.

---

## What to Include in Your Report

A good report lets us reproduce and understand the issue quickly. Please
include as much of the following as you can:

- A clear summary of the vulnerability
- The affected branch, file, function, or component
- The affected version or commit hash
- The platform, language runtime, and environment where you reproduced it
- Step-by-step reproduction instructions
- A proof of concept, if you have one
- The impact you believe this has: what can an attacker do
- The threat model you are assuming: who is the attacker, what do they control
- Any suggested fix or mitigation
- Whether you have disclosed this to anyone else
- How you would like to be credited, or whether you prefer to remain anonymous

Do not include real user data, real private keys, or real credentials in your
report. Use test data.

---

## What to Expect From Us

We are a volunteer project, but we treat security reports as the highest
priority. Our target timelines are:

| Stage                                | Target          |
| ------------------------------------ | --------------- |
| Acknowledge receipt                  | 72 hours        |
| Initial triage and severity rating   | 7 days          |
| Status update to reporter            | Every 7 days    |
| Fix for critical issues              | 30 days         |
| Fix for high issues                  | 60 days         |
| Fix for medium and low issues        | 90 days         |
| Public advisory after fix            | Within 7 days   |

If we cannot meet a timeline, we will tell you why and give you a new estimate.

If we determine that a report is not a vulnerability, we will explain our
reasoning. If you disagree, we welcome a respectful follow-up.

---

## Disclosure Policy

We follow coordinated disclosure.

1. You report privately.
2. We acknowledge and triage.
3. We develop and test a fix.
4. We prepare a GitHub Security Advisory.
5. We release the fix and publish the advisory at the same time.
6. We credit you in the advisory, unless you ask us not to.

We ask that you give us up to 90 days from the initial report before public
disclosure. If a fix is taking longer, we will work with you on a reasonable
extension. If we are unresponsive, you are free to disclose after 90 days of
silence from us. We will never threaten or pressure a reporter who follows
this policy.

Please do not disclose the issue publicly before a fix is available, and
please do not disclose it to third parties without telling us first.

---

## Scope

The following are in scope for security reports:

- The identity kernel: key generation, storage, rotation, cryptographic
  operations, verifiable credential issuance and verification, selective
  disclosure, and offline verification
- The personal data vault: local storage, encryption at rest, access control,
  audit logging, and encrypted synchronization
- All language bindings: memory safety at the FFI boundary, input validation,
  and any deviation from the kernel's security guarantees
- The command line interface: argument parsing, file handling, secret handling,
  and shell interaction
- Packaging and distribution: tampered artifacts, dependency confusion,
  unsigned releases, and supply chain risks
- Cryptographic protocol design: weaknesses in how we combine primitives, not
  in the primitives themselves
- Governance and specification documents, if they lead to insecure
  implementations
- Documentation that instructs users to do something insecure

---

## Out of Scope

The following are generally out of scope. Report them, but expect a lower
priority or a polite decline:

- Vulnerabilities in third-party dependencies that are already publicly known
  and have an upstream fix. Report those upstream, then tell us so we can bump
  the version.
- Vulnerabilities that require a fully compromised device, rooted OS, or
  physical access to an unlocked, running system, unless the attack escalates
  beyond what that access already grants.
- Social engineering of maintainers, contributors, or users
- Denial of service through trivial resource exhaustion without a realistic
  attacker model
- Missing security headers on GitHub Pages or documentation sites
- Reports generated entirely by automated scanners with no manual analysis or
  proof of impact
- Theoretical attacks against primitives that are considered secure by the
  wider cryptographic community
- Issues in examples or test fixtures that are clearly marked as insecure and
  not intended for production use

If you are unsure, report it. We will tell you if it is out of scope and why.

---

## Severity Guidelines

We use a simplified version of CVSS to rate severity. Use these as a guide
when describing impact:

**Critical**
- Remote code execution without authentication
- Private key extraction from the kernel or vault
- Silent bypass of verifiable credential verification
- Ability to forge credentials that pass verification
- Mass deanonymization of users

**High**
- Authentication bypass in a binding or the CLI
- Local privilege escalation within the Rotten Fish process
- Data exfiltration from the vault without user consent
- Denial of service that permanently corrupts identity or credential data

**Medium**
- Information disclosure of non-secret metadata
- Denial of service that requires restart or reinstall
- Weaknesses that require significant user interaction to exploit
- Timing side channels with a realistic attacker model

**Low**
- Hardening gaps with no demonstrated exploit
- Information leaks in error messages that reveal non-sensitive internals
- Insecure defaults that are documented but easy to miss

Severity is determined by impact and exploitability together, not by the
category alone.

---

## Safe Harbor

We will not pursue or support legal action against anyone who:

- Reports a vulnerability in good faith following this policy
- Avoids privacy violations, data destruction, and service interruption
  during their research
- Only interacts with accounts and data they own or have explicit permission
  to test
- Gives us reasonable time to fix the issue before public disclosure

If legal action is taken against you by a third party for research conducted
under this policy, we will make it clear that your actions were authorized and
consistent with our intent.

If you are uncertain whether your planned research falls under safe harbor,
contact us first at security.bedusec@gmail.com and we will tell you in writing.

---

## Recognition

We credit every reporter in the published advisory, unless you ask to remain
anonymous. With your permission, we will also list you in the project's
security acknowledgements page.

We do not currently offer monetary bounties. We offer:

- Public credit in the advisory and in the repository
- A direct line to the maintainers
- Our genuine gratitude for helping protect real people

If the project becomes funded in the future, we will revisit this and consider
a bounty program.

---

## Security Advisories

Published advisories live here:

https://github.com/bedulabs/rottenfish/security/advisories

Subscribe to repository releases and watch the repository's security alerts if
you deploy Rotten Fish in a production or high-risk environment.

---

## Hardening Guidance for Users

Rotten Fish is designed to be secure by default, but some practices are the
responsibility of the user or the integrator.

- Always run the latest commit on the branch you depend on.
- Pin dependencies and verify checksums in your build pipeline.
- Store kernel keys in the platform's secure element or keystore when
  available.
- Never log private keys, seed phrases, or decrypted credentials.
- Encrypt backups. An unencrypted identity backup is an identity theft kit.
- Use the personal data vault's audit log. Review it regularly.
- Treat any binding that deviates from the kernel's behavior as untrusted.
- If you build a downstream product on Rotten Fish, document your threat model
  and pass this document along to your users.

Security is a shared responsibility. We build the foundation. You build on it
carefully.

---

Thank you for helping keep Rotten Fish and its users safe.
