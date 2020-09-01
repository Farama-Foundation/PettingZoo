from pettingzoo.utils.error import DeprecatedEnv


def env(*args, **kwargs):
    raise DeprecatedEnv("double_dunk_v0 is now depreciated, use double_dunk_v1 instead")


raw_env = env
parallel_env = env
manual_control = env
