"""Custom exceptions for the PettingZoo registry."""


class PettingZooRegistryError(Exception):
    """Base exception for PettingZoo registry."""


class NamespaceNotFound(PettingZooRegistryError):
    """Raised when an environment namespace is not found in the registry."""


class NameNotFound(PettingZooRegistryError):
    """Raised when an environment name is not found in the registry."""


class VersionNotFound(PettingZooRegistryError):
    """Raised when an environment version is not found in the registry."""


class FailedToImport(PettingZooRegistryError):
    """Raised when an environment fails to import."""
