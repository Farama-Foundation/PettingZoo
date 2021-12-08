---
layout: "docu"
title: "Tennis"
actions: "Discrete"
agents: "2"
manual-control: "No"
action-shape: "(1,)"
action-values: "[0,17]"
observation-shape: "(210, 160, 3)"
observation-values: "(0,255)"
import: "from pettingzoo.atari import tennis_v2"
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




A competitive game of positioning and prediction.

Goal: Get the ball past your opponent. Don't let the ball get past you.

When a point is scored (by the ball exiting the area), you get +1 reward and your opponent gets -1 reward. Unlike normal tennis matches, the number of games won is not directly rewarded.

Serves are timed: If the player does not serve within 3 seconds of receiving the ball, they receive -1 points, and the timer resets. This prevents one player from indefinitely stalling the game, but also means it is no longer a purely zero sum game.

[Official tennis manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=555)

#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .

### Version History

* v2: No action timer (1.9.0)
* v1: Breaking changes to entire API (1.4.0)
* v0: Initial versions release (1.0.0)
</div>
