"""EnvSpec dataclass and environment ID parsing utilities."""

import importlib
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

from pettingzoo.env_registry.exceptions import PettingZooRegistryError
from pettingzoo.env_registry.types import _AECEnv, _ParallelEnv

ENV_ID_PARSING = re.compile(
    r"^(?:(?P<namespace>[\w.-]+)\/)?(?P<name>[\w:.-]+?)(?:-v(?P<version>\d+))?$"
)
UNDERSCORE_NORMALIZATION = re.compile(r"_v(?=\d+$)")


@lru_cache
def _normalize_env_id(env_id: str) -> str:
    """Normalize PettingZoo-style version suffixes to Gymnasium-style IDs."""
    return UNDERSCORE_NORMALIZATION.sub("-v", env_id.strip(), count=1)


@dataclass(frozen=True, slots=True)
class EnvSpec:
    """Specification for a registered environment, immutable after creation."""

    id: str
    entry_point: Callable[..., Any] | str | None = None
    kwargs: dict[str, Any] = field(default_factory=dict)
    max_cycles: int | None = field(default=None)

    namespace: str | None = field(init=False)
    name: str = field(init=False)
    version: int | None = field(init=False)

    def __post_init__(self):
        force_setattr = object.__setattr__  # we need to overwrite frozen fields
        force_setattr(self, "id", _normalize_env_id(self.id))
        ns, name, ver = _parse_env_id(self.id)
        force_setattr(self, "namespace", ns)
        force_setattr(self, "name", name)
        force_setattr(self, "version", ver)

    def make(self, **kwargs: Any) -> _AECEnv | _ParallelEnv:
        """Create an environment instance from this spec."""
        merged_kwargs = {**self.kwargs, **kwargs}
        if self.max_cycles is not None and "max_cycles" not in merged_kwargs:
            merged_kwargs["max_cycles"] = self.max_cycles
        creator = _load_env_creator(self.entry_point)
        return creator(**merged_kwargs)


@lru_cache
def _parse_env_id(env_id: str) -> tuple[str | None, str, int | None]:
    """Parse an environment ID into (namespace, name, version).

    Format: ``[namespace/]EnvName[-vN]``
    """
    env_id_parsed = None
    if isinstance(env_id, str):
        env_id_parsed = ENV_ID_PARSING.fullmatch(_normalize_env_id(env_id))
    if not env_id_parsed:
        raise PettingZooRegistryError(
            f"Malformed environment ID: {env_id!r}. "
            f"Expected a str with format: [namespace/]EnvName[-vN]"
        )
    namespace = env_id_parsed.group("namespace")
    name = env_id_parsed.group("name")
    version_str = env_id_parsed.group("version")
    version = int(version_str) if version_str is not None else None
    return namespace, name, version


@lru_cache
def _load_env_creator(
    entry_point: Callable[..., Any] | str | None,
) -> Callable[..., Any]:
    """Load an environment creator from a string or callable entry point."""
    if entry_point is None:
        raise PettingZooRegistryError(
            "entry_point must not be None when creating an environment."
        )
    if callable(entry_point):
        return entry_point
    mod_name, attr_name = entry_point.split(":")
    module = importlib.import_module(mod_name)
    creator = getattr(module, attr_name)
    if not callable(creator):
        raise PettingZooRegistryError(
            f"Entry point {entry_point!r} resolved to a non-callable: {type(creator)}"
        )
    return creator
