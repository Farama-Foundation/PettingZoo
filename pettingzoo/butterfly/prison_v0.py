from pettingzoo.utils.error import DeprecatedEnv


def env(*args, **kwargs):
    raise DeprecatedEnv("prison_v0 is now depreciated, use prison_v1 instead")


def raw_env(*args, **kwargs):
    raise DeprecatedEnv("prison_v0 is now depreciated, use prison_v1 instead")
