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
import: "from pettingzoo.butterfly import knights_archers_zombies_v10"
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




Zombies walk from the top border of the screen down to the bottom border in unpredictable paths. The agents you control are knights and archers (default 2 knights and 2 archers) that are initially positioned at the bottom border of the screen. Each agent can rotate clockwise or counter-clockwise and move forward or backward. Each agent can also attack to kill zombies. When a knight attacks, it swings a mace in an arc in front of its current heading direction. When an archer attacks, it fires an arrow in a straight line in the direction of the archer's heading. The game ends when all agents die (collide with a zombie) or a zombie reaches the bottom screen border. A knight is rewarded 1 point when its mace hits and kills a zombie. An archer is rewarded 1 point when one of their arrows hits and kills a zombie.
There are two possible observation types for this environment, vectorized and image-based.

#### Vectorized (Default)
Pass the argument `vector_state=True` to the environment.

The observation is an (N+1)x5 array for each agent, where `N = num_archers + num_knights + num_swords + max_arrows + max_zombies`.
> Note that `num_swords = num_knights`

The ordering of the rows of the observation look something like this:
```
[
[current agent],
[archer 1],
...,
[archer N],
[knight 1],
...
[knight M],
[sword 1],
...
[sword M],
[arrow 1],
...
[arrow max_arrows],
[zombie 1],
...
[zombie max_zombies]
]
```

In total, there will be N+1 rows. Rows with no entities will be all 0, but the ordering of the entities will not change.

**Vector Breakdown**

This breaks down what a row in the observation means. All distances are normalized to [0, 1].
Note that for positions, [0, 0] is the top left corner of the image. Down is positive y, Left is positive x.

For the vector for `current agent`:
- The first value means nothing and will always be 0.
- The next four values are the position and angle of the current agent.
  - The first two values are position values, normalized to the width and height of the image respectively.
  - The final two values are heading of the agent represented as a unit vector.

For everything else:
- Each row of the matrix (this is an 5 wide vector) has a breakdown that looks something like this:
  - The first value is the absolute distance between an entity and the current agent.
  - The next four values are relative position and absolute angles of each entity relative to the current agent.
    - The first two values are position values relative to the current agent.
    - The final two values are the angle of the entity represented as a directional unit vector relative to the world.

**Typemasks**

There is an option to prepend a typemask to each row vector. This can be enabled by passing `use_typemasks=True` as a kwarg.

The typemask is a 6 wide vector, that looks something like this:
```
[0., 0., 0., 1., 0., 0.]
```

Each value corresponds to either
```
[zombie, archer, knight, sword, arrow, current agent]
```

If there is no entity there, the whole typemask (as well as the whole state vector) will be 0.

As a result, setting `use_typemask=True` results in the observation being a (N+1)x11 vector.

**Transformers** (Experimental)

There is an option to also pass `transformer=True` as a kwarg to the environment. This just removes all non-existent entities from the observation and state vectors. Note that this is **still experimental** as the state and observation size are no longer constant. In particular, `N` is now a variable number.

#### Image-based
Pass the argument `vector_state=False` to the environment.

Each agent observes the environment as a square region around itself, with its own body in the center of the square. The observation is represented as a 512x512 pixel image around the agent, or in other words, a 16x16 agent sized space around the agent.

### Manual Control

Move the archer using the 'W', 'A', 'S' and 'D' keys. Shoot the Arrow using 'F' key. Rotate the archer using 'Q' and 'E' keys.
Press 'X' key to spawn a new archer.

Move the knight using the 'I', 'J', 'K' and 'L' keys. Stab the Sword using ';' key. Rotate the knight using 'U' and 'O' keys.
Press 'M' key to spawn a new knight.



### Arguments

``` python
knights_archers_zombies_v10.env(
  spawn_rate=20,
  num_archers=2,
  num_knights=2,
  max_zombies=10,
  max_arrows=10,
  killable_knights=True,
  killable_archers=True,
  pad_observation=True,
  line_death=False,
  max_cycles=900,
  vector_state=True,
  use_typemasks=False,
  transformer=False,
```

`spawn_rate`:  how many cycles before a new zombie is spawned. A lower number means zombies are spawned at a higher rate.

`num_archers`:  how many archer agents initially spawn.

`num_knights`:  how many knight agents initially spawn.

`max_zombies`: maximum number of zombies that can exist at a time

`max_arrows`: maximum number of arrows that can exist at a time

`killable_knights`:  if set to False, knight agents cannot be killed by zombies.

`killable_archers`:  if set to False, archer agents cannot be killed by zombies.

`pad_observation`:  if agents are near edge of environment, their observation cannot form a 40x40 grid. If this is set to True, the observation is padded with black.

`line_death`:  if set to False, agents do not die when they touch the top or bottom border. If True, agents die as soon as they touch the top or bottom border.

`vector_state`: whether to use vectorized state, if set to `False`, an image-based observation will be provided instead.

`use_typemasks`: only relevant when `vector_state=True` is set, adds typemasks to the vectors.

`transformer`: **experimental**, only relevant when `vector_state=True` is set, removes non-existent entities in the vector state.


### Version History

* v10: Add vectorizable state space (1.17.0)
* v9: Code rewrite and numerous fixes (1.16.0)
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
