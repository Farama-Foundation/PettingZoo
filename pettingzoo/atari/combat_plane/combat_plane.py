import os
from glob import glob

from ..base_atari_env import BaseAtariEnv, base_env_wrapper_fn, parallel_wrapper_fn

avaliable_versions = {
    "bi-plane": 15,
    "jet": 21,
}


def raw_env(game_version="bi-plane", guided_missile=True, **kwargs):
    assert (
        game_version in avaliable_versions
    ), "game_version must be either 'jet' or 'bi-plane'"
    mode = avaliable_versions[game_version] + (0 if guided_missile else 1)
    name = os.path.basename(__file__).split(".")[0]
    parent_file = glob(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), name + "*.py")
    )
    version_num = parent_file[0].split("_")[-1].split(".")[0]
    name = name + "_" + version_num
    return BaseAtariEnv(
        game="combat", num_players=2, mode_num=mode, env_name=name, **kwargs
    )


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
