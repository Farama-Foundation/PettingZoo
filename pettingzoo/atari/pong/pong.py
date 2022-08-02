import os
from glob import glob

from ..base_atari_env import BaseAtariEnv, base_env_wrapper_fn, parallel_wrapper_fn

avaliable_2p_versions = {
    "classic": 4,
    "two_paddles": 10,
    "soccer": 14,
    "foozpong": 19,
    "hockey": 27,
    "handball": 35,
    "volleyball": 39,
    "basketball": 45,
}
avaliable_4p_versions = {
    "classic": 6,
    "two_paddles": 11,
    "soccer": 16,
    "foozpong": 21,
    "hockey": 29,
    "quadrapong": 33,
    "handball": 37,
    "volleyball": 41,
    "basketball": 49,
}


def raw_env(num_players=2, game_version="classic", **kwargs):
    assert num_players == 2 or num_players == 4, "pong only supports 2 or 4 players"
    versions = avaliable_2p_versions if num_players == 2 else avaliable_4p_versions
    assert (
        game_version in versions
    ), f"pong version {game_version} not supported for number of players {num_players}. Available options are {list(versions)}"
    mode = versions[game_version]
    name = os.path.basename(__file__).split(".")[0]
    parent_file = glob(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), name + "*.py")
    )
    version_num = parent_file[0].split("_")[-1].split(".")[0]
    name = name + "_" + version_num
    return BaseAtariEnv(
        game="pong",
        num_players=num_players,
        mode_num=mode,
        env_name=name,
        **kwargs,
    )


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
