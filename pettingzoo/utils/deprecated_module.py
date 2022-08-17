import importlib.util
import pkgutil
import re


class DeprecatedEnv(ImportError):
    pass


class DeprecatedModule:
    def __init__(self, name, old_version, new_version):
        def env(*args, **kwargs):
            raise DeprecatedEnv(
                f"{name}_v{old_version} is now deprecated, use {name}_v{new_version} instead"
            )

        self.env = env
        self.raw_env = env
        self.parallel_env = env
        self.manual_control = env


def is_env(env_name):
    return bool(re.fullmatch("[a-zA-Z_]+_v[0-9]+", env_name))


def deprecated_handler(env_name, module_path, module_name):
    spec = importlib.util.find_spec(f"{module_name}.{env_name}")

    if spec is None:
        # It wasn't able to find this module
        # You should do your deprecation notice here.
        if not is_env(env_name):
            raise ImportError(f"cannot import name '{env_name}' from '{module_name}'")
        name, version = env_name.rsplit("_v")

        for loader, alt_env_name, is_pkg in pkgutil.iter_modules(module_path):
            if is_env(alt_env_name):
                alt_name, alt_version = alt_env_name.rsplit("_v")
                if alt_name == name:
                    if int(alt_version) > int(version):
                        return DeprecatedModule(name, version, alt_version)
                    else:
                        raise ImportError(
                            f"cannot import name '{env_name}' from '{module_name}'"
                        )

    # This constructs the module but doesn't execute its code
    assert spec
    module = importlib.util.module_from_spec(spec)
    # This executes the module and will raise any exceptions
    # that would typically be raised by just `import blah`
    assert spec.loader
    spec.loader.exec_module(module)
    return module
