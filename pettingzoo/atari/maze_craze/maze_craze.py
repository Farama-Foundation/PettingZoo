import os
import warnings
from glob import glob

from ..base_atari_env import BaseAtariEnv, base_env_wrapper_fn, parallel_wrapper_fn

avaliable_versions = {
    "robbers": 2,
    "race": 1,
    "capture": 12,
}


def raw_env(game_version="robbers", visibilty_level=0, **kwargs):
    if game_version == "robbers" and visibilty_level == 0:
        warnings.warn(
            "maze_craze has different versions of the game via the `game_version` argument, consider overriding."
        )
    assert (
        game_version in avaliable_versions
    ), f"`game_version` parameter must be one of {avaliable_versions.keys()}"
    assert (
        0 <= visibilty_level < 4
    ), "visibility level must be between 0 and 4, where 0 is 100% visibility and 3 is 0% visibility"
    base_mode = (avaliable_versions[game_version] - 1) * 4
    mode = base_mode + visibilty_level
    name = os.path.basename(__file__).split(".")[0]
    parent_file = glob(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), name + "*.py")
    )
    version_num = parent_file[0].split("_")[-1].split(".")[0]
    name = name + "_" + version_num
    return BaseAtariEnv(
        game="maze_craze",
        num_players=2,
        mode_num=mode,
        env_name=name,
        **kwargs,
    )


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
