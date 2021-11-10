---
layout: "docu"
title: "Space Invaders"
actions: "Discrete"
agents: "2"
manual-control: "No"
action-shape: "(1,)"
action-values: "[0,17]"
observation-shape: "(210, 160, 3)"
observation-values: "(0,255)"
import: "from pettingzoo.atari import space_invaders_v1"
agent-labels: "agents= ['first_0', 'second_0']"
---

<div class="docu-info" markdown="1">
{% include info_box.md %}
</div>

<div class="docu-content" markdown="1">
<div class="appear_big env-title" markdown="1">
{% include env_icon.md %}
## {{page.title}}
</div>




Classic Atari game, but there are two ships controlled by two players that are each trying to maximize their score.

This game has a cooperative aspect where the players can choose to maximize their score by working together to clear the levels. The normal aliens are 5-30 points, depending on how high up they start, and the ship that flies across the top of the screen is worth 100 points.

However, there is also a competitive aspect where a player receives a 200 point bonus when the other player is hit by the aliens. So sabotaging the other player somehow is a possible strategy.

The number of lives is shared between the ships, i.e. the game ends when a ship has been hit 3 times.

[Official Space Invaders manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=460)

#### Environment parameters

Some environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari).

Parameters specific to Space Invaders are

``` python
space_invaders_v1.env(alternating_control=False, moving_shields=True,
zigzaging_bombs=False, fast_bomb=False, invisible_invaders=False)
```

`alternating_control`:  Only one of the two players has an option to fire at one time. If you fire, your opponent can then fire. However, you can't hoard the firing ability forever, eventually, control shifts to your opponent anyways.

`moving_shields`:  The shields move back and forth, leaving less reliable protection.

`zigzaging_bombs`:  The invader's bombs move back and forth, making them more difficult to avoid.

`fast_bomb`:  The bombs are much faster, making them more difficult to avoid.

`invisible_invaders`:  The invaders are invisible, making them more difficult to hit.


### Version History

* v1: Breaking changes to entire API (1.4.0)
* v0: Initial versions release (1.0.0)
</div>
