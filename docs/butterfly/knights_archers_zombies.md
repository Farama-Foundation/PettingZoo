---
action type: "Discrete"
title: "Knights Archers Zombies ('KAZ')"
actions: Discrete
agents: "4"
manual-control: "Yes"
action-shape: "(1,)"
action-values: "[0, 5]"
observation-shape: "(512, 512, 3)"
observation-values: "(0, 255)"
state-shape: "(720, 1280, 3)"
state-values: "(0, 255)"
average-total-reward: "2.95"
import: "from pettingzoo.butterfly import knights_archers_zombies_v8"
agent-labels: "agents= ['archer_0', 'archer_1', 'knight_0', 'knight_1']"
---

<div class="docu-info" markdown="1">
{% include info_box.md %}
</div>

<div class="docu-content" markdown="1">
<div class="appear_big env-title" markdown="1">
{% include env_icon.md %}
## {{page.title}}
</div>




Zombies walk from the top border of the screen down to the bottom border in unpredictable paths. The agents you control are knights and archers (default 2 knights and 2 archers) that are initially positioned at the bottom border of the screen. Each agent can rotate clockwise or counter-clockwise and move forward or backward. Each agent can also attack to kill zombies. When a knight attacks, it swings a mace in an arc in front of its current heading direction. When an archer attacks, it fires an arrow in a straight line in the direction of the archer's heading. The game ends when all agents die (collide with a zombie) or a zombie reaches the bottom screen border. A knight is rewarded 1 point when its mace hits and kills a zombie. An archer is rewarded 1 point when one of their arrows hits and kills a zombie. Each agent observes the environment as a square region around itself, with its own body in the center of the square. The observation is represented as a 512x512 pixel image around the agent, or in other words, a 16x16 agent sized space around the agent.

### Manual Control

Move the archer using the 'W', 'A', 'S' and 'D' keys. Shoot the Arrow using 'F' key. Rotate the archer using 'Q' and 'E' keys.
Press 'X' key to spawn a new archer.

Move the knight using the 'I', 'J', 'K' and 'L' keys. Stab the Sword using ';' key. Rotate the knight using 'U' and 'O' keys.
Press 'M' key to spawn a new knight.



### Arguments

``` python
knights_archers_zombies_v8.env(spawn_rate=20, num_knights=2, num_archers=2,
killable_knights=True, killable_archers=True, line_death=True, pad_observation=True,
max_cycles=900)
```


`spawn_rate`:  how many cycles before a new zombie is spawned. A lower number means zombies are spawned at a higher rate.

`num_knights`:  how many knight agents initially spawn.

`num_archers`:  how many archer agents initially spawn.

`killable_knights`:  if set to False, knight agents cannot be killed by zombies.

`killable_archers`:  if set to False, archer agents cannot be killed by zombies.

`line_death`:  if set to False, agents do not die when they touch the top or bottom border. If True, agents die as soon as they touch the top or bottom border.

`pad_observation`:  if agents are near edge of environment, their observation cannot form a 40x40 grid. If this is set to True, the observation is padded with black.


### Version History

* v8: Code cleanup and several bug fixes (1.14.0)
* v7: Minor bug fix relating to end of episode crash (1.6.0)
* v6: Fixed reward structure (1.5.2)
* v5: Removed black death argument (1.5.0)
* v4: Fixed observation and rendering issues (1.4.2)
* v3: Misc bug fixes, bumped PyGame and PyMunk version (1.4.0)
* v2: Fixed bug in how `dones` were computed (1.3.1)
* v1: Fixes to how all environments handle premature death (1.3.0)
* v0: Initial versions release (1.0.0)
</div>
