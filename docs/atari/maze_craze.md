
### Maze Craze: Blockade

This environment is part of the [Atari environments](../atari.md). Please read that page first for general information.

| Observations | Actions | Agents  | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|---------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Graphical    | Discrete  | 2 | No      | (1,)    | [0,17]         | (210, 160, 3)         | (0,255)            | ?          |

`from pettingzoo.atari import maze_craze_blockade_v0`

`agents= ["first_0", "second_0"]`

![maze_craze_blockade gif](atari_maze_craze.gif)

*AEC diagram*

A competitive game of memory and planning!

Its a race to leave the maze. There are 3 main versions of the game.

1. **Race**: A basic version of the game. First to leave the maze wins
2. **Robbers**: There are 2 robbers randomly traversing the maze. If you are captured by the robbers, you lose the game, and receive -1 reward, and will be done. The player that has not been captured will not receive any reward, but they can still exit the maze and win, scoring +1 reward.
3. **Capture**: Each player have to capture all 3 robbers before you are able to exit the maze. Additionally, you can confuse your opponent (and yourself, if you are not careful!) by creating a block that looks identical to a wall in the maze, but all players can pass through it. You can only create one wall at a time, when you create a new one, the old one disappears.

The first player to leave the maze scores +1, the other player scores -1 (unless that other player has already been captured in Robbers mode).


#### Environment parameters

Some environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari.md).

Parameters specific to Maze Craze are

```
maze_craze.env(game_version="robbers", visibilty_level=0)
```

```
game_version: Possibilities are "robbers", "race", "capture", corresponding to the 3 game versions described above

visibilty_level: A number from 0-3. Set to 0 for 100% visible map, and 3 for 0% visibility map.
```
