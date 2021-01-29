from .base_atari_env import BaseAtariEnv, base_env_wrapper_fn, parallel_wrapper_fn
import warnings
import os


def raw_env(has_maze=False, is_invisible=False, billiard_hit=False, **kwargs):
    if has_maze is False and is_invisible is False and billiard_hit is False:
        warnings.warn("combat_tank has interesting parameters to consider overriding including is_invisible, billiard_hit and has_maze")
    start_mapping = {
        (False, False): 1,
        (False, True): 8,
        (True, False): 10,
        (True, True): 13,
    }
    mode = start_mapping[(is_invisible, billiard_hit)] + has_maze

    return BaseAtariEnv(game="combat", num_players=2, mode_num=mode, env_name=os.path.basename(__file__)[:-3], **kwargs)


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
