from pettingzoo.utils.error import DeprecatedEnv


def env(*args, **kwargs):
    raise DeprecatedEnv("video_checkers_v0 is now depreciated, use video_checkers_v1 instead")


raw_env = env
parallel_env = env
manual_control = env
