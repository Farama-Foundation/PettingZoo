---
layout: "docu"
title: "Pong: Foozpong"
actions: "Discrete"
agents: "4"
manual-control: "No"
action-shape: "(1,)"
action-values: "[0,17]"
observation-shape: "(210, 160, 3)"
observation-values: "(0,255)"
import: "from pettingzoo.atari import pong_foozpong"
agent-labels: "agents= ['first_0', 'second_0', 'third_0', 'fourth_0']"
---

<div class="floatright" markdown="1">

![pong_volleyball gif](atari_pong_foozpong.gif)

This environment is part of the [Atari environments](../atari). Please read that page first for general information.

{% include table.md %}

</div>

## Pong: Foozpong


Four player team battle.

Get the ball past your opponent's defenders to the scoring area. Like traditional foozball, the board has alternating layers of paddles from each team between the goal areas. To succeed at this game, the two players on each side must coordinate to allow the ball to be passed between these layers up the board and into your opponent's scoring area.

Scoring a point gives your team +1 reward and your opponent's team -1 reward.

[Official Video Olympics manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=587)

#### Environment parameters

Some environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari).

Parameters specific to Pong Foozpong are

```
pong_classic.env(num_players=4)
```

```
num_players: Number of players (must be either 2 or 4)
```
