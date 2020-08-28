from pettingzoo.utils.error import DeprecatedEnv


def env(*args, **kwargs):
    raise DeprecatedEnv("pong_quadrapong_v0 is now depreciated, use pong_quadrapong_v1 instead")


raw_env = env
parallel_env = env
manual_control = env
