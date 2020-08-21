from pettingzoo.utils.error import DeprecatedEnv


def env(*args, **kwargs):
    raise DeprecatedEnv("prospector_v0 is now depreciated, use prospector_v1 instead")


raw_env = env
parallel_env = env
manual_control = env
