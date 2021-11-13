import os
import warnings

from .base_atari_env import BaseAtariEnv, base_env_wrapper_fn, parallel_wrapper_fn

"""
A competitive game of memory and planning!

Its a race to leave the maze. There are 3 main versions of the game.

1. **Race**: A basic version of the game. First to leave the maze wins
2. **Robbers**: There are 2 robbers randomly traversing the maze. If you are captured by the robbers, you lose the game, and receive -1 reward, and will be done. The player that has not been captured will not receive any reward, but they can still exit the maze and win, scoring +1 reward.
3. **Capture**: Each player have to capture all 3 robbers before you are able to exit the maze. Additionally, you can confuse your opponent (and yourself, if you are not careful!) by creating a block that looks identical to a wall in the maze, but all players can pass through it. You can only create one wall at a time, when you create a new one, the old one disappears.

The first player to leave the maze scores +1, the other player scores -1 (unless that other player has already been captured in Robbers mode).

[Official Maze craze manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=295). Note that the table of modes has some inaccuracies. In particular, game mode 12 has Blockade enabled, not mode 11.

#### Environment parameters

Some environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari).

Parameters specific to Maze Craze are

`game_version`:  Possibilities are "robbers", "race", "capture", corresponding to the 3 game versions described above

`visibilty_level`:  A number from 0-3. Set to 0 for 100% visible map, and 3 for 0% visibility map.
"""

avaliable_versions = {
    "robbers": 2,
    "race": 1,
    "capture": 12,
}


def raw_env(game_version="robbers", visibilty_level=0, **kwargs):
    if game_version == "robbers" and visibilty_level == 0:
        warnings.warn("maze_craze has different versions of the game via the `game_version` argument, consider overriding.")
    assert game_version in avaliable_versions, f"`game_version` parameter must be one of {avaliable_versions.keys()}"
    assert 0 <= visibilty_level < 4, "visibility level must be between 0 and 4, where 0 is 100% visibility and 3 is 0% visibility"
    base_mode = (avaliable_versions[game_version] - 1) * 4
    mode = base_mode + visibilty_level
    return BaseAtariEnv(game="maze_craze", num_players=2, mode_num=mode, env_name=os.path.basename(__file__)[:-3], **kwargs)


env = base_env_wrapper_fn(raw_env)
parallel_env = parallel_wrapper_fn(env)
