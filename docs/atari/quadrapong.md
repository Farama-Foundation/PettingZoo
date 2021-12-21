---
layout: "docu"
title: "Quadrapong"
actions: "Discrete"
agents: "4"
manual-control: "No"
action-shape: "(1,)"
action-values: "[0,17]"
observation-shape: "(210, 160, 3)"
observation-values: "(0,255)"
import: "from pettingzoo.atari import quadrapong_v3"
agent-labels: "agents= ['first_0', 'second_0', 'third_0', 'fourth_0']"
---

<div class="docu-info" markdown="1">
{% include info_box.md %}
</div>

<div class="docu-content" markdown="1">
<div class="appear_big env-title" markdown="1">
{% include env_icon.md %}
## {{page.title}}
</div>




Four player team battle.

Each player controls a paddle and defends a scoring area. However, this is a team game, and so two of the 4 scoring areas belong to the same team. So a given team must try to coordinate to get the ball away from their scoring areas towards their opponent's.
Specifically `first_0` and `third_0` are on one team and `second_0` and `fourth_0` are on the other.

Scoring a point gives your team +1 reward and your opponent team -1 reward.

Serves are timed: If the player does not serve within 2 seconds of receiving the ball, their team receives -1 points, and the timer resets. This prevents one player from indefinitely stalling the game, but also means it is no longer a purely zero sum game.


[Official Video Olympics manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=587)

#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .

### Version History

* v3: No action timer (1.9.0)
* v1: Breaking changes to entire API (1.4.0)
* v2: Fixed quadrapong rewards (1.2.0)
* v0: Initial versions release (1.0.0)
</div>
