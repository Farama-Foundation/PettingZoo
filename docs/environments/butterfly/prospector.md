---
actions: "Continuous"
title: "Prospector"
agents: "7"
manual-control: "Yes"
action-shape: "(3,), (2,)"
action-values: "[-1, 1]"
observation-shape: "(150, 150, 3), (154, 154, 3)"
observation-values: "(0, 255)"
state-shape: "(720, 1280, 3)"
state-values: "(0, 255)"
average-total-reward: "0"
import: "from pettingzoo.butterfly import prospector_v4"
agent-labels: "agents= ['prospector_0, 'prospector_1', 'prospector_2', 'prospector_3', 'banker_0', 'banker_1', 'banker_2']"
---

<div class="docu-info" markdown="1">
{% include info_box.md %}
</div>

<div class="docu-content" markdown="1">
<div class="appear_big env-title" markdown="1">
{% include env_icon.md %}
## {{page.title}}
</div>




This game is inspired by gold panning in the American "wild west" movies. There's a blue river at
the bottom of the screen, which contains gold. 4 "prospector" agents can move and touch the river
and pan from it, and get a gold nugget (visibly held by them). Prospectors can
only hold one nugget at a time, and nuggets stay in the same position relative to the prospector's
orientation.

Prospector agents take a 3-element vector of continuous values between -1 and 1, inclusive.
The action space is `(y, x, r)`, where `y` is used for forward/backward movement,
`x` is used for left/right movement, and `r` is used for clockwise/counter-clockwise rotation.

There are a handful of bank chests at the top of the screen. The prospector agents can hand their
held gold nugget to the 3 "banker" agents, to get a reward. The banker agents can't rotate,
and the prospector agents must give the nuggets (which are held in the same
position relative to the prospector's position and rotation) to the
front of the bankers (within a plus or minus 45 degree tolerance).
The bankers then get the gold, and can deposit it into the chests to receive a reward.

Bankers take a 2-element vector of continuous values between -1 and 1, inclusive.
The action space is `(y, x)`, where
`y` is used for forward/backward movement and `x` is used for left/right movement.

The observation space size for prospectors
is `(150, 150, 3)` and the size for
bankers is slightly bigger at
`(154, 154, 3)`. The diameter of both
prospector and banker agents is 30 pixels, so
the observation space sizes are about 5 times larger
than the diameter of each agent. There are fewer
bankers, so they're given a slightly
larger observation space to give them more
information on their surroundings.

**Rewards:**

Rewards are issued for a prospector retrieving a nugget, a prospector handing
a nugget off to a banker, a banker receiving a nugget from a prospector,
and a banker depositing the gold into a bank. There is
an individual reward, a group reward (for agents of the same type), and
an other-group reward (for agents of the other type).

By default, if a prospector retrieves a nugget from the water, then
that prospector receives a reward of
0.8, other
prospectors will
receive a reward of 0.1 and
all bankers receive a reward of
0.1.

By default, if a prospector
hands off a gold nugget to a banker (so the banker receives a gold nugget
from a prospector), there are two rewards that are processed:
the handing-off prospector gets 0.8,
the other prospectors get 0.1, and
all of the bankers get 0.1.
Similarly, the banker receiving the gold nugget gets
0.8, the other bankers
get 0.1, and
all of the prospectors get
0.1.

Finally, by default when a banker deposits gold in the bank,
that banker receives a reward of
0.8, the other bankers
receive rewards of 0.1, and
all of the prospectors receive
0.1.

### Manual Control

`"prospector_0"` is the first sprite you control. Use the left and
right arrow keys to switch between the agents.

Move prospectors using the 'WASD' keys for forward/left/backward/right movement.
Rotate using 'QE' for counter-clockwise/clockwise rotation.

Move the bankers using the 'WASD' keys for forward/left/backward/right movement.

The game lasts for 900 frames by default.

### Arguments

``` python
prospector_v4.env(ind_reward=0.8, group_reward=0.1, other_group_reward=0.1,
prospec_find_gold_reward=1, prospec_handoff_gold_reward=1, banker_receive_gold_reward=1,
banker_deposit_gold_reward=1, max_cycles=150
```

`ind_reward`: The reward multiplier for a single agent completing an objective.

`group_reward`: The reward multiplier that agents of the same type
as the scoring agent will earn.

`other_group_reward`: The reward multiplier that agents of the other type
as the scoring agent will earn. If the scoring agent is a prospector,
then this is the reward that the bankers get, and vice versa.

Constraint: `ind_reward + group_reward + other_group_reward == 1.0`

`prospec_find_gold_reward`: The reward for a prospector
retrieving gold from the water at the bottom of the screen.

`prospec_handoff_gold_reward`: The reward for a prospector
handing off gold to a banker.

`banker_receive_gold_reward`: The reward for a banker receiving
gold from a prospector.

`banker_deposit_gold_reward`: The reward for a banker depositing
gold into a bank.

`max_cycles`: The number of frames the game should run for.


### Version History

* v4: Changed default argument for `max_cycles`, bumped PyMunk version (1.6.0)
* v3: Misc fixes, bumped PyGame and PyMunk version (1.4.0)
* v2: Numerous bug fixes (1.3.5)
* v1: Fixed prospector agents leaving game area (1.3.4)
* v0: Initial versions release (1.0.0)
</div>