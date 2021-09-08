---
layout: "docu"
title: "Boxing"
actions: "Discrete"
agents: "2"
manual-control: "No"
action-shape: "(1,)"
action-values: "[0,17]"
observation-shape: "(210, 160, 3)"
observation-values: "(0,255)"
import: "from pettingzoo.atari import boxing_v1"
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


*Boxing* is an adversarial game where precise control and
appropriate responses to your opponent are key.

The players have two minutes (around 1200 steps) to duke it
out in the ring. Each step, they can move and punch.
Successful punches score points,
1 point for a long jab, 2 for a close power punch,
and 100 points for a KO (which also will end the game).
Whenever you score a number of points, you are rewarded by
that number and your opponent is penalized by that number.

[Official Boxing manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=45)

#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .

### Version History

* v1: Breaking changes to entire API (1.4.0)
* v0: Initial versions release (1.0.0)
</div>
