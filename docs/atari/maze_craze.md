---
layout: "docu"
title: "Maze Craze"
actions: "Discrete"
agents: "2"
manual-control: "No"
action-shape: "(1,)"
action-values: "[0,17]"
observation-shape: "(250, 160, 3)"
observation-values: "(0,255)"
import: "from pettingzoo.atari import maze_craze_v2"
agent-labels: "agents= ['first_0', 'second_0']"
---

<div class="docu-info" markdown="1">
{% include info_box.md %}
</div>

<div class="docu-content" markdown="1">
<div class="appear_big env-title" markdown="1">
{% include env_icon.md %}
## {{page.title}}
</div>




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

``` python
maze_craze.env(game_version="robbers", visibilty_level=0)
```

`game_version`:  Possibilities are "robbers", "race", "capture", corresponding to the 3 game versions described above

`visibilty_level`:  A number from 0-3. Set to 0 for 100% visible map, and 3 for 0% visibility map.

### Version History

* v2: Breaking changes to entire API (1.4.0)
* v1: Fixes to how all environments handle premature death (1.3.0)
* v0: Initial versions release (1.0.0)
</div>
