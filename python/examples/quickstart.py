"""Quickstart for the Rotten Fish Python binding.

Run with ROTTENFISH_DEV_FALLBACK=1 until the native kernel is available.
"""
import os

os.environ.setdefault("ROTTENFISH_DEV_FALLBACK", "1")

from rottenfish import Presentation, PresentationRequest, Vault  # noqa: E402


def main() -> None:
    with Vault.open("~/.rottenfish/vault.rf", passphrase="demo") as vault:
        identity = vault.create_identity(label="personal")
        print("Identity DID:", identity.did)

        vault.grant(
            app_id="com.example.clinic",
            scopes=["credential:read:health"],
            purpose="Appointment check-in",
            duration="1h",
        )

        request = PresentationRequest.from_json(
            {
                "challenge": "nonce-from-verifier",
                "issuerPublicKey": identity.public_key.hex(),
                "queries": [
                    {
                        "id": "age_over_18",
                        "purpose": "Entry to licensed premises",
                        "required": True,
                    },
                    {
                        "id": "full_name",
                        "purpose": "Marketing",
                        "required": False,
                    },
                ],
            }
        )

        presentation = vault.present(
            request,
            disclose=["age_over_18"],
            withhold=["full_name"],
        )

        result = Presentation.verify(
            presentation,
            trusted_issuers=[identity.public_key],
            challenge="nonce-from-verifier",
        )
        print("Valid:", result.valid)
        print("Disclosed:", result.disclosed)

        print("Audit tail:")
        for entry in vault.audit.tail(5):
            print(" ", entry)


if __name__ == "__main__":
    main()