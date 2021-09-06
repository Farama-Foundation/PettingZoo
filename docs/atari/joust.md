---
layout: "docu"
title: "Joust"
actions: "Discrete"
agents: "2"
manual-control: "No"
action-shape: "(1,)"
action-values: "[0,17]"
observation-shape: "(210, 160, 3)"
observation-values: "(0,255)"
import: "from pettingzoo.atari import joust_v2"
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





Mixed sum game involving scoring points in an unforgiving world. Careful positioning, timing,
and control is essential, as well as awareness of your opponent.

In Joust, you score points by hitting the opponent and NPCs when
you are above them. If you are below them, you lose a life.
In a game, there are a variety of waves with different enemies
and different point scoring systems. However, expect that you can earn
around 3000 points per wave.

[Official joust manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=253)

#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .

### Version History

* v2: Breaking changes to entire API (1.4.0)
* v1: Fixes to how all environments handle premature death (1.3.0)
* v0: Initial versions release (1.0.0)
</div>
