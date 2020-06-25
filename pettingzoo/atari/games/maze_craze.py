from ..base_atari_env import BaseAtariEnv, base_env_wrapper_fn


avaliable_versions = {
    "robbers": 2,
    "race": 1,
    "capture": 12,
}


def raw_env(game_version="robbers", visibilty_level=0, **kwargs):
    if visibilty_level is 0:
        warnings.warn("maze_craze has a visibilty_level that makes the map invisible, may be interesting to set this parameter")
    assert game_version in avaliable_versions, f"`game_version` parameter must be one of {avaliable_versions.keys()}"
    assert 0 <= visibilty_level < 4, "visibility level must be between 0 and 4, where 0 is 100% visiblity and 3 is 0% visibility"
    base_mode = (avaliable_versions[game_version] - 1) * 4
    mode = base_mode + visibilty_level
    return BaseAtariEnv(game="maze_craze", num_players=2, mode_num=mode, **kwargs)


env = base_env_wrapper_fn(raw_env)
