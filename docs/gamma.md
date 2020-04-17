## Gamma Environments

| Environment             | Observations | Actions    | Agents  | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|:------------------------|:-------------|:-----------|:-------:|:--------------:|:------------:|:-------------:|:-----------------:|:------------------:|----------:|
| Cooperative Pong        | Graphical    | Discrete   | 2       | Yes            | ?            | ?             | ?                 | ?                  | ?          |
| Knights Archers Zombies | Graphical    | Discrete   | 4 (+/-) | Yes            | ?            | ?             | ?                 | ?                  | ?          |
| Pistonball              | Graphical    | Either     | 20      | Yes            | ?            | ?             | ?                 | ?                  | ?          |
| Prison                  | Either       | Either     | 8       | Yes            | ?            | ?             | ?                 | ?                  | ?          |
| Prospector              | Graphical    | Continuous | 7 (+/-) | Yes            | ?            | ?             | ?                 | ?                  | ?          |

`pip install pettingzoo[gamma]`

All Gamma environments were created by us, using PyGame, with visual Atari spaces. In Prison, all agents are completely independent (i.e. no coordination is possible, each agent is in it's own cell. It is intended as a debugging tool.

All other environments require a high degree of coordination and learning emergent behaviors to achieve an optimal policy. As such, these environments are currently very challenging to learn.

### Cooperative Pong
| Observations | Actions  | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|:-------------|:---------|:------:|:--------------:|:------------:|:-------------:|:-----------------:|:------------------:|:----------:|
| Graphical    | Discrete | 2      | Yes            |      --      |   [0, 1]      |  (560, 480, 3)    |   [0, 255]         | ?          |

`from pettingzoo.gamma import cooperative_pong_v0`

`agents= ["paddle_0", "paddle_1"]`

Example gameplay:

![](media/cooperative_pong.gif)

AEC diagram:

![](media/cooperative_pong_aec.png)

Cooperative pong is a game of simple pong, where the objective is to keep the ball in play for the longest time. The game is over when the ball goes out of bounds from either the left or right edge of the screen. There are two agents (paddles), one that moves along the left edge and the other that moves along the right edge of the screen. All collisions of the ball are elastic. The ball always starts moving in a random direction from the center of the screen with each reset. To make learning a little more challenging, the right paddle is tiered cake-shaped , by default. Observation space of each agent is its own half of the screen. There are two possible actions for the agents (_move up/down_). If the ball stays within bounds, both agents receive a combined reward of `100 / max_frames`, if they successfully complete a frame. Otherwise, they receive $-100$ reward and the game ends. 


Manual Control:

Move the left paddle using the 'W' and 'S' keys. Move the right paddle using 'UP' and 'DOWN' arrow keys.

```
cooperative_pong.env(ball_speed=18, left_paddle_speed=25,
right_paddle_speed=25, is_cake_paddle=True, max_frames=900, bounce_randomness=False)
```

The speed of ball is held constant (governed by the argument `ball_speed`) throughout the game, while the initial direction of the ball is randomized when `reset()` method is called. The speed of left and right paddles are controlled by `left_paddle_speed` and `right_paddle_speed` respectively. If `is_cake_paddle` is `True`, the right paddle has the shape of a 4-tiered wedding cake. `done` of all agents are set to `True` after `max_frames` number of frames elapse. If `bounce_randomness` is `True`, each collision of the ball with the paddles adds a small random angle to the direction of the ball, while the speed of the ball remains unchanged.

Leaderboard:

| Average Total Reward | Method | Institution | Paper | Code |
|----------------------|--------|-------------|-------|------|
| x                    | x      | x           | x     | x    |


### Knights Archers Zombies ('KAZ')
| Observations | Actions  | Agents  | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|----------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Graphical    | Discrete | 4 (+/-) | Yes            | ?            | ?             | ?                 | ?                  | ?          |

`from pettingzoo.gamma import knights_archers_zombies_v0`

`agents= `

*gif*

*AEC diagram*

Zombies walk from the top border of the screen down to the bottom border in unpredictable paths. The agents you control are knights and archers (default 2 knights and 2 archers) that are initially positioned at the bottom border of the screen. Each agent can rotate clockwise or counter-clockwise and move forward or backward. Each agent can also attack to kill zombies. When a knight attacks, it swings a mace in an arc in front of its current heading direction. When an archer attacks, it fires an arrow in a straight line in the direction of the archer's heading. The game ends when all agents die (collide with a zombie) or a zombie reaches the bottom screen border. An agent gets a reward when it kills a zombie. Each agent observes the environment as a square region around itself, with its own body in the center of the square. The observation is represented as a 1600-element vector (40x40 grid around the agent).

Manual Control:

Move the archer using the 'W', 'A', 'S' and 'D' keys. Shoot the Arrow using 'F' key. Rotate the archer using 'Q' and 'E' keys.
Press 'X' key to spawn a new archer.

Move the knight using the 'I', 'J', 'K' and 'L' keys. Stab the Sword using ';' key. Rotate the knight using 'U' and 'O' keys.
Press 'M' key to spawn a new knight.


```
knights_archers_zombies.env(spawn_rate=?, knights=2, archers=2, 
killable_knights=True, killable_archers=True, line_death=True, max_frames=900)
```

*about arguments*

Leaderboard:

| Average Total Reward | Method | Institution | Paper | Code |
|----------------------|--------|-------------|-------|------|
| x                    | x      | x           | x     | x    |


### Pistonball
| Observations | Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|---------|--------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Graphical    | Either  | 20     | Yes            | ?            | ?             | ?                 | ?                  | ?          |

`from pettingzoo.gamma import pistonball_v0`

`agents= `

*gif*

*AEC diagram*

This is a simple physics based cooperative game where the goal is to move the ball to the left wall of the game border by activating any of the twenty vertically moving pistons. Pistons can only see themselves, and the two pistons next to them. 
Thus, pistons must learn highly coordinated emergent behavior to achieve an optimal policy for the environment. Each agent get's a reward that is a combination of how much the ball moved left overall, and how much the ball moved left if it was close to the piston (i.e. movement it contributed to). Balancing the ratio between these appears to be critical to learning this environment, and as such is an environment parameter.

Pistonball uses the chipmunk physics engine, and are thus the physics are about as realistic as Angry Birds.

Keys *a* and *d* control which piston is selected to move (initially the rightmost piston is selected) and keys *w* and *s* move the piston in the vertical direction.

```
pistonball.env(local_ratio=.02, continuous=False, random_drop=True,
starting_angular_momentum=True, ball_mass = .75, ball.friction=.3,
ball.elasticity=1.5, max_frames=900)
```

*about arguments*

Discrete Leaderboard:

| Average Total Reward | Method | Institution | Paper | Code |
|----------------------|--------|-------------|-------|------|
| x                    | x      | x           | x     | x    |

Continuous Leaderboard:

| Average Total Reward | Method | Institution | Paper | Code |
|----------------------|--------|-------------|-------|------|
| x                    | x      | x           | x     | x    |


### Prison

| Observations | Actions | Agents | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|---------|--------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Either       | Either  | 8      | Yes            | ?            | ?             | ?                 | ?                  | ?          |

`from pettingzoo.gamma import prison_v0`

`agents= `

*gif*

*AEC diagram*

In prison, 8 aliens locked in identical prison cells are controlled by the user. They cannot communicate with each other in any way, and can only pace in their cell. Every time they touch one end of the cell and then the other, they get a reward of 1. Due to the fully independent nature of these agents and the simplicity of the task, this is an environment primarily intended for debugging purposes- it's multiple individual purely single agent tasks. To make this debugging tool as compatible with as many methods as possible, it can accept both discrete and continuous actions and the observation can be automatically turned into a number representing position of the alien from the left of it's cell instead of the normal graphical output.

Arguments:

```
prison.env(graphical_output=True, discrete_input=True, syncronized_start=False,
identical_aliens=False, max_frames=900, random_aliens=False)
```

*about arguments*

Discrete Leaderboard:

| Average Total Reward | Method | Institution | Paper | Code |
|----------------------|--------|-------------|-------|------|
| x                    | x      | x           | x     | x    |

Continuous Leaderboard:

| Average Total Reward | Method | Institution | Paper | Code |
|----------------------|--------|-------------|-------|------|
| x                    | x      | x           | x     | x    |


### Prospector
| Observations | Actions    | Agents  | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|------------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Graphical    | Continuous | 7 (+/-) | Yes            | ?            | ?             | ?                 | ?                  | ?          |

`from pettingzoo.gamma import prospector_v0`

`agents= `

*gif*

*AEC diagram*

This game is inspired by gold panning in the American "wild west" movies. There's a blue river at the bottom of the screen, which contains gold. 4 "panner" agents can move and touch the river and pan from it, and get a gold nugget (visibly held by them). They take a 3 element vector of continuous values (the first for forward/backward, the second for left/right movement, the third for clockwise/counter-clockwise rotation). They can only hold 1 nugget at a time.

There are a handful of bank chests at the top of the screen. The panner agents can hand their held gold nugget to the 2 "manager" agents, to get a reward. The manager agents can't rotate, and the panner agents must give the nuggets (which are held in the front of their body) to the front (always pointing upwards) of the managers. The managers then get the gold, and can deposit it into the chests to recieve a reward. They take a 2 element vector of continuous values (the first for forward/backward, the second for left/right movement). They can only hold 1 nugget at a time. The game lasts for 900 frames by default.

*arguments*

*about arguments*

Leaderboard:

| Average Total Reward | Method | Institution | Paper | Code |
|----------------------|--------|-------------|-------|------|
| x                    | x      | x           | x     | x    |
