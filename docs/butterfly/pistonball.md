---
action-type: "either"
title: "Pistonball"
alt_title: "PistonBall"
actions: Either
agents: "20"
manual-control: "Yes"
action-shape: "(1,)"
action-values: "[-1, 1]"
observation-shape: "(457, 120, 3)"
observation-values: "(0, 255)"
state-shape: "(560, 880, 3)"
state-values: "(0, 255)"
average-total-reward: "-91.2"
import: "from pettingzoo.butterfly import pistonball_v6"
agent-labels: "agents= ['piston_0', 'piston_1', ..., 'piston_19']"
---

<div class="docu-info" markdown="1">
{% include info_box.md %}
</div>

<div class="docu-content" markdown="1">
<div class="appear_big env-title" markdown="1">
{% include env_icon.md %}
## {{page.title}}
</div>




This is a simple physics based cooperative game where the goal is to move the ball to the left wall of the game border by activating the vertically moving pistons. Each piston agent's observation is an RGB image of the two pistons (or the wall) next to the agent and the space above them. Every piston can be acted on in any given time. The action space in discrete mode is 0 to move down, 1 to stay still, and 2 to move up. In continuous mode, the value in the range [-1, 1] is proportional to the amount that the pistons are raised or lowered by. Continuous actions are scaled by a factor of 4, so that in both the discrete and continuous action space, the action 1 will move a piston 4 pixels up, and -1 will move pistons 4 pixels down.

Accordingly, pistons must learn highly coordinated emergent behavior to achieve an optimal policy for the environment. Each agent gets a reward that is a combination of how much the ball moved left overall and how much the ball moved left if it was close to the piston (i.e. movement the piston contributed to). A piston is considered close to the ball if it is directly below any part of the ball. Balancing the ratio between these local and global rewards appears to be critical to learning this environment, and as such is an environment parameter. The local reward applied is 0.5 times the change in the ball's x-position. Additionally, the global reward is change in x-position divided by the starting position, times 100, plus the `time_penalty` (default -0.1). For each piston, the reward is `local_ratio` * local_reward + (1-`local_ratio`) * global_reward. The local reward is applied to pistons surrounding the ball while the global reward is provided to all pistons.

Pistonball uses the chipmunk physics engine, and are thus the physics are about as realistic as in the game Angry Birds.

Keys *a* and *d* control which piston is selected to move (initially the rightmost piston is selected) and keys *w* and *s* move the piston in the vertical direction.


### Arguments


``` python
pistonball_v6.env(n_pistons=20, time_penalty=-0.1, continuous=True,
random_drop=True, random_rotate=True, ball_mass=0.75, ball_friction=0.3,
ball_elasticity=1.5, max_cycles=125)
```

`n_pistons`: The number of pistons (agents) in the environment.

`time_penalty`: Amount of reward added to each piston each time step. Higher values mean higher weight towards getting the ball across the screen to terminate the game.

`continuous`:  If true, piston action is a real value between -1 and 1 which is added to the piston height. If False, then action is a discrete value to move a unit up or down.

`random_drop`:  If True, ball will initially spawn in a random x value. If False, ball will always spawn at x=800

`random_rotate`:  If True, ball will spawn with a random angular momentum

`ball_mass`:  Sets the mass of the ball physics object

`ball_friction`:  Sets the friction of the ball physics object

`ball_elasticity`:  Sets the elasticity of the ball physics object

`max_cycles`:  after max_cycles steps all agents will return done


### Version History

* v6: Fix ball bouncing off of left wall.
* v5: Ball moving into the left column due to physics engine imprecision no longer gives additional reward
* v4: Changed default arguments for `max_cycles` and `continuous`, bumped PyMunk version (1.6.0)
* v3: Refactor, added number of pistons argument, minor visual changes (1.5.0)
* v2: Misc fixes, bumped PyGame and PyMunk version (1.4.0)
* v1: Fix to continuous mode (1.0.1)
* v0: Initial versions release (1.0.0)
</div>
