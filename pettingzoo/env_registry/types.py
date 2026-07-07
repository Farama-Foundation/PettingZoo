"""Type aliases for generic environment base classes."""

from typing import Any, Literal, TypeAlias

from pettingzoo.utils.env import AECEnv, ParallelEnv

_AECEnv: TypeAlias = AECEnv[Any, Any, Any]
_ParallelEnv: TypeAlias = ParallelEnv[Any, Any, Any]

EnvType = Literal["aec", "parallel"]
