from __future__ import annotations

from types import ModuleType

from pettingzoo.utils.deprecated_module import DeprecatedModule, deprecated_handler


def __getattr__(env_name: str) -> DeprecatedModule | ModuleType:
    return deprecated_handler(env_name, __path__, __name__)
