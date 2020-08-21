from pettingzoo.utils.error import DeprecatedEnv


def env(*args, **kwargs):
    raise DeprecatedEnv("entombed_competitive_v0 is now depreciated, use entombed_competitive_v1 instead")


raw_env = env
parallel_env = env
manual_control = env
