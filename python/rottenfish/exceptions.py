"""Exception hierarchy for the Rotten Fish Python binding."""


class RottenFishError(Exception):
    """Base class for every error raised by this package."""


class VaultError(RottenFishError):
    """A vault operation failed."""


class VaultLockedError(VaultError):
    """The vault is closed and the operation requires it to be open."""


class KernelError(RottenFishError):
    """The native kernel failed or is unavailable."""


class KernelNotFoundError(KernelError):
    """The native kernel shared library could not be located."""


class ConsentError(RottenFishError):
    """An operation was attempted without an active grant."""


class CredentialError(RottenFishError):
    """A credential is malformed, expired, or cannot be processed."""


class PresentationError(RottenFishError):
    """A presentation could not be produced or verified."""