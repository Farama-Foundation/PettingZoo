---
layout: "docu"
title: "Entombed: Cooperative"
actions: "Discrete"
agents: "2"
manual-control: "No"
action-shape: "(1,)"
action-values: "[0,17]"
observation-shape: "(210, 160, 3)"
observation-values: "(0,255)"
average-total-reward: "6.23"
import: "from pettingzoo.atari import entombed_cooperative_v2"
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





Entombed's cooperative version is an exploration game
where you need to work with your teammate to make it
as far as possible into the maze.

You both need to quickly navigate down a constantly generating
maze you can only see part of. If you get stuck, you lose.
Note you can easily find yourself in a dead-end escapable only through the use of rare power-ups.
If players help each other by the use of these powerups, they can last longer. Note that optimal coordination requires that the agents be on opposite sides of the map, because powerups appear on one side or the other, but can be used to break through walls on both sides (the break is symmetric and effects both halves of the screen).
In addition, there dangerous zombies lurking around to avoid.

The reward was designed to be identical to the single player rewards. In particular, an entombed stage is divided into 5 invisible sections. You receive reward immediately after changing sections, or after resetting the stage. Note that this means that you receive a reward when you lose a life, because it resets the stage, but not when you lose your last life, because the game terminates without the stage resetting.


[Official Entombed manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=165)


#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .

### Version History

* v2: Breaking changes to entire API, fixed Entombed rewards (1.4.0)
* v1: Fixes to how all environments handle premature death (1.3.0)
* v0: Initial versions release (1.0.0)
</div>
