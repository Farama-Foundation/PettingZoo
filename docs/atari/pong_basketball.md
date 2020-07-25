---
layout: "docu"
title: "Pong: Basketball"
actions: "Discrete"
agents: "2"
manual-control: "No"
action-shape: "(1,)"
action-values: "[0,17]"
observation-shape: "(210, 160, 3)"
observation-values: "(0,255)"
import: "from pettingzoo.atari import pong_basketball_v0"
agent-labels: "agents= ['first_0', 'second_0']"
---

<div class="floatright" markdown="1">

![pong_basketball gif](atari_pong_basketball.gif)

This environment is part of the [Atari environments](../atari). Please read that page first for general information.

{% include table.md %}

</div>

## Pong: Basketball


A competitive game of control.

Try to get the ball in your opponents hoop. But you cannot move on their side of the court. Scoring a point also gives your opponent -1 reward.

[Official Video Olympics manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=587)

#### Environment parameters

Some environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari).

Parameters specific to Pong Basketball are

```
pong_classic.env(num_players=2)
```

```
num_players: Number of players (must be either 2 or 4)
```
