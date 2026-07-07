"""Functions for registering environments within PettingZoo: ``make``, ``register`` and ``spec``."""

import warnings
from collections.abc import Callable
from copy import deepcopy
from typing import Any, Literal, overload

from pettingzoo.env_registry.exceptions import FailedToImport
from pettingzoo.env_registry.helpers import find_spec
from pettingzoo.env_registry.spec import EnvSpec, _load_env_creator
from pettingzoo.env_registry.types import EnvType, _AECEnv, _ParallelEnv
from pettingzoo.utils.env import AECEnv, ParallelEnv

# Two separate registries for AEC and Parallel
aec_registry: dict[str, EnvSpec] = {}
parallel_registry: dict[str, EnvSpec] = {}


def _get_registry(env_type: EnvType) -> dict[str, EnvSpec]:
    if env_type == "aec":
        return aec_registry
    if env_type == "parallel":
        return parallel_registry
    raise ValueError(f"Invalid env_type: {env_type!r}. Must be 'aec' or 'parallel'.")


@overload
def register(
    env_type: Literal["aec"],
    id: str,
    entry_point: Callable[..., _AECEnv] | str | None = ...,
    *,
    max_cycles: int | None = ...,
    kwargs: dict[str, Any] | None = ...,
) -> None: ...


@overload
def register(
    env_type: Literal["parallel"],
    id: str,
    entry_point: Callable[..., _ParallelEnv] | str | None = ...,
    *,
    max_cycles: int | None = ...,
    kwargs: dict[str, Any] | None = ...,
) -> None: ...


def register(
    env_type: EnvType,
    id: str,
    entry_point: Callable[..., Any] | str | None = None,
    *,
    max_cycles: int | None = None,
    kwargs: dict[str, Any] | None = None,
) -> None:
    """Register an environment in the appropriate registry.

    Args:
        env_type: Either ``"aec"`` or ``"parallel"``.
        id: The environment ID in format ``[namespace/]EnvName[-vN]``.
        entry_point: A callable or ``"module:attr"`` string that creates the env.
        max_cycles: Default maximum number of cycles before the environment truncates.
            Passed as ``max_cycles`` kwarg to the entry point if the environment
            supports it.
        kwargs: Default keyword arguments passed to the entry point.
    """
    registry = _get_registry(env_type)
    new_spec = EnvSpec(
        id=id,
        entry_point=entry_point,
        kwargs=kwargs if kwargs is not None else {},
        max_cycles=max_cycles,
    )
    if new_spec.id in registry:
        warnings.warn(
            f"Overriding environment {new_spec.id!r} in the {env_type} registry.",
            stacklevel=2,
        )
    registry[new_spec.id] = new_spec


@overload
def make(
    env_type: Literal["aec"],
    id: str | EnvSpec,
    *,
    max_cycles: int | None = ...,
    **kwargs: Any,
) -> _AECEnv: ...


@overload
def make(
    env_type: Literal["parallel"],
    id: str | EnvSpec,
    *,
    max_cycles: int | None = ...,
    **kwargs: Any,
) -> _ParallelEnv: ...


def make(
    env_type: EnvType,
    id: str | EnvSpec,
    *,
    max_cycles: int | None = None,
    **kwargs: Any,
) -> _AECEnv | _ParallelEnv:
    """Create an environment from the registry.

    Args:
        env_type: Either ``"aec"`` or ``"parallel"``.
        id: The environment ID string or an ``EnvSpec`` instance.
        max_cycles: Maximum number of cycles before truncation. Overrides the
            value stored in the ``EnvSpec``. Pass ``-1`` to disable.
        **kwargs: Additional keyword arguments passed to the entry point
            (overrides defaults in the spec).

    Returns:
        An environment instance (``AECEnv`` for ``"aec"``, ``ParallelEnv`` for ``"parallel"``).
    """
    if isinstance(id, EnvSpec):
        env_spec = id
    else:
        registry = _get_registry(env_type)
        env_spec = find_spec(registry, id)

    merged_kwargs = deepcopy(env_spec.kwargs)
    merged_kwargs.update(kwargs)

    # Resolve max_cycles: explicit arg > spec default; -1 means don't pass it
    effective_max_cycles = max_cycles if max_cycles is not None else env_spec.max_cycles
    if effective_max_cycles is not None and effective_max_cycles != -1:
        merged_kwargs.setdefault("max_cycles", effective_max_cycles)

    # Entry point import may fail if optional dependencies are missing
    try:
        creator = _load_env_creator(env_spec.entry_point)
    except ImportError as import_error:
        raise FailedToImport(
            f"Failed to import entry point {env_spec.entry_point!r} for "
            f"environment {env_spec.id!r}. You may need to install additional "
            f"dependencies (e.g. pip install 'pettingzoo[{env_spec.namespace}]')."
        ) from import_error

    env = creator(**merged_kwargs)

    expected_type = AECEnv if env_type == "aec" else ParallelEnv
    if not isinstance(env, expected_type):
        warnings.warn(
            f"Environment {env_spec.id!r} was expected to be an instance of "
            f"{expected_type.__name__}, but got {type(env).__name__}.",
            stacklevel=2,
        )

    return env


def spec(env_type: EnvType, id: str) -> EnvSpec:
    """Look up the EnvSpec for a registered environment.

    Args:
        env_type: Either ``"aec"`` or ``"parallel"``.
        id: The environment ID string.

    Returns:
        The ``EnvSpec`` for the environment.
    """
    registry = _get_registry(env_type)
    return find_spec(registry, id)


def pprint_registry() -> None:
    """Pretty-print all registered environments."""
    print("AEC environments:")
    for env_id in sorted(aec_registry.keys()):
        print(f"  {env_id}")
    print("\nParallel environments:")
    for env_id in sorted(parallel_registry.keys()):
        print(f"  {env_id}")
