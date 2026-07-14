from __future__ import annotations

import importlib.util
import pkgutil
import re
from collections.abc import Iterable
from types import ModuleType


class DeprecatedEnv(ImportError):
    pass


# Environments removed from PettingZoo entirely, mapped to the reason why. These
# raise on attribute access rather than falling through as a missing module, so
# that users upgrading from an older release get an actionable message.
REMOVED_ENVS: dict[str, str] = {
    "gin_rummy": (
        "gin_rummy was removed from PettingZoo, see "
        "https://github.com/Farama-Foundation/PettingZoo/issues/1383. The "
        "underlying implementation remains available in RLCard: "
        "https://github.com/datamllab/rlcard"
    ),
}


# Must subclass AttributeError: this is raised from a __getattr__(), and raising
# anything else breaks the default handling in getattr(obj, "key", "default").
class RemovedEnv(AttributeError):
    pass


class DeprecatedModule:
    def __init__(self, name: str, old_version: str | int, new_version: str | int):
        def env(*args, **kwargs):
            raise DeprecatedEnv(
                f"{name}_v{old_version} is now deprecated, use {name}_v{new_version} instead"
            )

        self.env = env
        self.raw_env = env
        self.parallel_env = env
        self.manual_control = env


def is_env(env_name: str) -> bool:
    return bool(re.fullmatch("[a-zA-Z_]+_v[0-9]+", env_name))


def deprecated_handler(
    env_name: str, module_path: Iterable[str], module_name: str
) -> DeprecatedModule | ModuleType:
    spec = importlib.util.find_spec(f"{module_name}.{env_name}")

    if spec is None:
        # It wasn't able to find this module
        # You should do your deprecation notice here.
        if not is_env(env_name):
            # Although this seems like an import error, it needs to be an
            # AttributeError because it is the failure to find the
            # 'env_name' attribute in module_name.
            # The distinction is important because this function is used in
            # a __getattr__() function to get modules. Raising an error
            # other than AttributeError will break the default value handling
            # in a call like: getattr(obj, "key", default="value")
            # Pytest uses that and will fail if this isn't an AttributeError
            raise AttributeError(
                f"cannot import name '{env_name}' from '{module_name}'"
            )
        name, version = env_name.rsplit("_v")

        if name in REMOVED_ENVS:
            raise RemovedEnv(REMOVED_ENVS[name])

        for _loader, alt_env_name, _is_pkg in pkgutil.iter_modules(module_path):
            if is_env(alt_env_name):
                alt_name, alt_version = alt_env_name.rsplit("_v")
                if alt_name == name:
                    if int(alt_version) > int(version):
                        return DeprecatedModule(name, version, alt_version)
                    raise AttributeError(
                        f"cannot import name '{env_name}' from '{module_name}'"
                    )

        # No module of this name exists at any version.
        raise AttributeError(f"cannot import name '{env_name}' from '{module_name}'")

    # This constructs the module but doesn't execute its code
    module = importlib.util.module_from_spec(spec)
    # This executes the module and will raise any exceptions
    # that would typically be raised by just `import blah`
    assert spec.loader
    spec.loader.exec_module(module)
    return module
