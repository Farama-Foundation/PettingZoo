---
env_icon: "../../../_static/img/icons/butterfly/cooperative_pong.png"
firstpage: 
---

# Cooperative Pong

```{figure} butterfly_cooperative_pong.gif 
:width: 200px
:name: cooperative_pong
```

This environment is part of the <a href='..'>butterfly environments</a>. Please read that page first for general information.

| Import               | `from pettingzoo.butterfly import cooperative_pong_v4` |
|----------------------|--------------------------------------------------------|
| Actions              | Discrete                                               |
| Parallel API         | Yes                                                    |
| Manual Control       | Yes                                                    |
| Agents               | `agents= ['paddle_0', 'paddle_1']`                     |
| Agents               | 2                                                      |
| Action Shape         | Discrete(3)                                            |
| Action Values        | [0, 1]                                                 |
| Observation Shape    | (280, 480, 3)                                          |
| Observation Values   | [0, 255]                                               |
| State Shape          | (560, 960, 3)                                          |
| State Values         | (0, 255)                                               |
| Average Total Reward | -92.9                                                  |

```{figure} ../../_static/img/aec/butterfly_cooperative_pong_aec.svg
:width: 200px
:name: cooperative_pong
```

Cooperative pong is a game of simple pong, where the objective is to keep the ball in play for the longest time. The game is over when the ball goes out of bounds from either the left or right edge of the screen. There are two agents (paddles), one that moves along the left edge and the other that moves along the right edge of the screen. All collisions of the ball are elastic. The ball always starts moving in a random direction from the center of the screen with each reset. To make learning a little more challenging, the right paddle is tiered cake-shaped by default. The observation space of each agent is its own half of the screen. There are two possible actions for the agents (_move up/down_). If the ball stays within bounds, each agent receives a reward of `max_reward / max_cycles` (default 0.11) at each timestep. Otherwise, each agent receives a reward of `off_screen_penalty` (default -10) and the game ends.


### Manual Control

Move the left paddle using the 'W' and 'S' keys. Move the right paddle using 'UP' and 'DOWN' arrow keys.

### Arguments

``` python
cooperative_pong_v4.env(ball_speed=9, left_paddle_speed=12,
right_paddle_speed=12, cake_paddle=True, max_cycles=900, bounce_randomness=False, max_reward=100, off_screen_penalty=-10)
```

`ball_speed`: Speed of ball (in pixels)

`left_paddle_speed`: Speed of left paddle (in pixels)

`right_paddle_speed`: Speed of right paddle (in pixels)

`cake_paddle`: If True, the right paddle cakes the shape of a 4 tiered wedding cake

`max_cycles`:  after max_cycles steps all agents will return done

`bounce_randomness`: If True, each collision of the ball with the paddles adds a small random angle to the direction of the ball, with the speed of the ball remaining unchanged.

`max_reward`:  Total reward given to each agent over max_cycles timesteps

`off_screen_penalty`:  Negative reward penalty for each agent if the ball goes off the screen

### Version History

* v5: Fixed ball teleporting bugs
* v4: Added max_reward and off_screen_penalty arguments and changed default, fixed glitch where ball would occasionally teleport, reward redesign (1.14.0)
* v3: Change observation space to include entire screen (1.10.0)
* v2: Misc fixes (1.4.0)
* v1: Fixed bug in how `dones` were computed (1.3.1)
* v0: Initial versions release (1.0.0)

