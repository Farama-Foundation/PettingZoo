---
action-type: "Discrete"
agents: "2"
manual-control: "Yes"
action-shape: "--"
action-values: "[0, 1]"
observation-shape: "(280, 240, 3)"
observation-values: "[0, 255]"
---

### Cooperative Pong

This environment is part of the [butterfly environments](../butterfly). Please read that page first for general information.

{% include table.md %}


`from pettingzoo.butterfly import cooperative_pong_v0`

`agents= ["paddle_0", "paddle_1"]`

Example gameplay:

![](butterfly_cooperative_pong.gif)

AEC diagram:

![](cooperative_pong_aec.png)

Cooperative pong is a game of simple pong, where the objective is to keep the ball in play for the longest time. The game is over when the ball goes out of bounds from either the left or right edge of the screen. There are two agents (paddles), one that moves along the left edge and the other that moves along the right edge of the screen. All collisions of the ball are elastic. The ball always starts moving in a random direction from the center of the screen with each reset. To make learning a little more challenging, the right paddle is tiered cake-shaped , by default. Observation space of each agent is its own half of the screen. There are two possible actions for the agents (_move up/down_). If the ball stays within bounds, both agents receive a combined reward of `100 / max_frames` (default 0.11), if they successfully complete a frame. Otherwise, each agent receive a reward of `-100` and the game ends.


Manual Control:

Move the left paddle using the 'W' and 'S' keys. Move the right paddle using 'UP' and 'DOWN' arrow keys.

*Arguments*

```
cooperative_pong.env(ball_speed=9, left_paddle_speed=12,
right_paddle_speed=12, cake_paddle=True, max_frames=900, bounce_randomness=False)
```

*About Arguments*

```
ball_speed: Speed of ball
left_paddle_speed: Speed of left paddle
right_paddle_speed: Speed of right paddle
cake_paddle: If True, the right paddle cakes the shape of a 4 tiered wedding cake
max_frames: Done is set to True for all agents after this number of frames (steps through all agents) elapses.
bounce_randomness: If True, each collision of the ball with the paddles adds a small random angle to the direction of the ball, with the speed of the ball remaining unchanged.
