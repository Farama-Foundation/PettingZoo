---
layout: "docu"
title: "Backgammon"
actions: "Discrete"
agents: "2"
manual-control: "No"
action-shape: "Discrete(26^2 * 2 + 1)"
action-values: "Discrete(26^2 * 2 + 1)"
observation-shape: "(198,)"
observation-values: "[0, 7.5]"
num-states: "10^26"
import: "from pettingzoo.classic import backgammon_v3"
agent-labels: "agents= ['player_0', 'player_1']"
---
<div class="docu-info" markdown="1">
{% include info_box.md %}
</div>

<div class="docu-content" markdown="1">
<div class="appear_big env-title" markdown="1">
{% include env_icon.md %}
## {{page.title}}
</div>




Backgammon is a 2-player turn-based board game. Players take turns rolling 2 dice and moving checkers forward according to those rolls. A player wins if they are the first to remove all of their checkers from the board.

This environment uses [gym-backgammon](https://github.com/dellalibera/gym-backgammon)'s implementation of backgammon.

The rules of backgammon can be found [here.](https://www.bkgm.com/rules.html)

### Observation Space

The observation is a dictionary which contains an `'obs'` element which is the usual RL observation described below, and an  `'action_mask'` which holds the legal moves, described in the Legal Actions Mask section.

The main observation space has shape (198,). Entries 0-97 represent the positions of any white checkers, entries 98-195 represent the positions of any black checkers, and entries 196-197 encode the current player.

| Num       | Observation                                                         | Min  | Max  |
| --------- | -----------------------------------------------------------------   | ---- | ---- |
| 0         | WHITE - 1st point, 1st component                                    | 0.0  | 1.0  |
| ...         |                                     |   |   |
| 3         | WHITE - 1st point, 4th component                                    | 0.0  | 6.0  |
| 4         | WHITE - 2nd point, 1st component                                    | 0.0  | 1.0  |
| ...       |                                                                     |      |      |
| 96        | WHITE - BAR checkers                                                | 0.0  | 7.5  |
| 97        | WHITE - OFF bar checkers                                            | 0.0  | 1.0  |
| 98        | BLACK - 1st point, 1st component                                    | 0.0  | 1.0  |
| ...       |                                                                     |      |      |
| 194       | BLACK - BAR checkers                                                | 0.0  | 7.5  |
| 195       | BLACK - OFF bar checkers                                            | 0.0  | 1.0  |
| 196 - 197 | Current player                                                      | 0.0  | 1.0  |

If there are more than 3 checkers on a point, then the value of the 4th component of that point will be (checkers - 3.0) / 2.0

Encoding of checkers on the bar:

| Checkers | Encoding             |
| -------- | -------------------- |
| 0 - 14   | bar_checkers / 2.0 |

Encoding of off checkers:

| Checkers | Encoding              |
| -------- | --------------------- |
| 0 - 14   | off_checkers / 15.0 |

Encoding of the current player:

| Player  | Encoding   |
| ------- | ---------- |
| WHITE   | [1.0, 0.0] |
| BLACK   | [0.0, 1.0] |


#### Legal Actions Mask

The legal moves available to the current agent are found in the `action_mask` element of the dictionary observation. The `action_mask` is a binary vector where each index of the vector represents whether the action is legal or not. The `action_mask` will be all zeros for any agent except the one whose turn it is. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents.

### Action Space
The action space for this environment is Discrete(26^2 * 2 + 1).

An agent's turn involves rolling two dice and then performing an action based on those rolls. An action involves using the two dice values to move checkers from one point to another or off of the board.

Each action value encodes the two points to move checkers from (source locations), and which dice roll to use first. An action moves a checker from the first source location forward by the amount of the first dice roll (either low roll or high roll, depending on the action value), and then moves a checker from the second source location forward by the amount of the other dice roll.

It is possible that only one of the dice rolls can be used. In that case, one of the source locations will be out of the bounds of the board and is not used.

Actions from 0 to 26^2 -1 use the low dice roll first, and actions from 26^2 to 2*26 ^2 - 1 use the high dice roll first.

The two locations to move a checker from are encoded as a number in base 26.

The 'do nothing' action is 26^2*2

| Action  | First Source Location ID | Second Source Location ID|  First Roll Used | Second Roll Used |         
| ------- | ---------- |---------- |---------- |---------- |
| 0 to 26^ 2 -1   | action mod 26 | action / 26 | Low Roll | High Roll
| 26^2 to 26^2*2 -1   | (action - 26^2) mod 26 |(action - 26^2) / 26 | High Roll | Low Roll
| 26^2*2   | None |None | None | None |

The location on the board can be found from the location ID, which is either the source ID, or the destination ID (source ID + Roll).

| Location ID (S) | Board Location |
| ------- |  ------- |
| <1 | White's bear off location|
|1 to 24 | Point number S-1|
|25 | Bar|
|>25 | Black's bear off location|

#### Agent Order
The game starts with rolling two dice until their values are different. If the first roll is larger, then the first agent is assigned the color white. Otherwise, the first agent is assigned the color black.

Following this, white and black alternate turns. However, if both dice have the same value on an agent's turn (a double roll), then that agent gets an extra turn with the same roll immediately after their current turn. This is reflected in the environment by assigning the current agent as the next player in the agent order and not re-rolling their dice on that turn.  

#### Rewards

The winner is the first player to remove all of their checkers from the board.

| Winner | Loser |
| :----: | :---: |
| +1     | -1    |

### Version History

* v3: Fixed bug in arbitrary calls to observe() (1.8.0)
* v2: Legal action mask in observation replaced illegal move list in infos (1.5.0)
* v1: Bumped version of all environments due to adoption of new agent iteration scheme where all agents are iterated over after they are done (1.4.0)
* v0: Initial versions release (1.0.0)
</div>