"""Registry lookup and version resolution helpers."""

from functools import lru_cache

from pettingzoo.env_registry.exceptions import (
    NameNotFound,
    NamespaceNotFound,
    VersionNotFound,
)
from pettingzoo.env_registry.spec import EnvSpec, _normalize_env_id, _parse_env_id


def find_spec(registry: dict[str, "EnvSpec"], env_id: str) -> "EnvSpec":
    """Look up an EnvSpec in a registry, resolving unversioned IDs to the latest version."""
    env_id = _normalize_env_id(env_id)
    if env_id in registry:
        return registry[env_id]

    namespace, name, version = _parse_env_id(env_id)

    if version is not None:
        # Check if the env name exists at all
        highest = _find_highest_version(registry, namespace, name)
        if highest is not None:
            raise VersionNotFound(
                f"Environment version v{version} for {_get_env_id(namespace, name, None)!r} "
                f"not found. Available version: v{highest}"
            )
        # Check namespace
        if namespace is not None:
            ns_exists = any(s.namespace == namespace for s in registry.values())
            if not ns_exists:
                raise NamespaceNotFound(
                    f"Namespace {namespace!r} not found in registry."
                )
        raise NameNotFound(
            f"Environment {env_id!r} not found in registry. "
            f"Available environments: {list(registry.keys())}"
        )

    # No version specified — resolve to highest
    highest = _find_highest_version(registry, namespace, name)
    if highest is not None:
        full_id = _get_env_id(namespace, name, highest)
        return registry[full_id]

    if namespace is not None:
        ns_exists = any(s.namespace == namespace for s in registry.values())
        if not ns_exists:
            raise NamespaceNotFound(f"Namespace {namespace!r} not found in registry.")
    raise NameNotFound(
        f"Environment {env_id!r} not found in registry. "
        f"Available environments: {list(registry.keys())}"
    )


@lru_cache
def _get_env_id(namespace: str | None, name: str, version: int | None) -> str:
    """Reconstruct a full environment ID from its components."""
    env_id = namespace + "/" if namespace else ""
    env_id += name
    if version is not None:
        env_id += f"-v{version}"
    return env_id


def _find_highest_version(
    registry: dict[str, "EnvSpec"], namespace: str | None, name: str
) -> int | None:
    """Find the highest registered version for a given env name in a registry."""
    highest: int | None = None
    for spec in registry.values():
        if (
            spec.namespace == namespace
            and spec.name == name
            and spec.version is not None
        ):
            if highest is None or spec.version > highest:
                highest = spec.version
    return highest
