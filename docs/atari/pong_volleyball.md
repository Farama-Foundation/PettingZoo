---
layout: docu
actions: Discrete
agents: 4
manual-control: No
action-shape: (1,)
action-values: [0,17]
observation-shape: (210, 160, 3)
observation-values: (0,255)
---

### Pong: Volleyball

This environment is part of the [Atari environments](../atari). Please read that page first for general information.


`from pettingzoo.atari import pong_volleyball_v0`

`agents= ["first_0", "second_0", "third_0", "fourth_0"]`

![pong_volleyball gif](atari_pong_volleyball.gif)

*AEC diagram*

Four player team battle.

Get the ball onto your opponent's floor to score. In addition to being able to move left and right, each player can also jump higher to affect the ball's motion above the net.

Scoring a point gives your team +1 reward and your opponent team -1 reward.

[Official Video Olympics manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=587)

#### Environment parameters

Some environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari).

Parameters specific to Pong Volleyball are

```
pong_classic.env(num_players=4)
```

```
num_players: Number of players (must be either 2 or 4)
```
