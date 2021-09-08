---
layout: "docu"
title: "Ice Hockey"
actions: "Discrete"
agents: "2"
manual-control: "No"
action-shape: "(1,)"
action-values: "[0,17]"
observation-shape: "(210, 160, 3)"
observation-values: "(0,255)"
import: "from pettingzoo.atari import ice_hockey_v1"
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




Competitive game of control and timing.

When you are on offense you must pass the puck between your two players (you control the one with the puck) to get it past your opponent's defense. On defense, you control the player directly in front of the puck. Both players must handle the rapid switches of control, while maneuvering around your opponent. If you score, you are rewarded +1, and your opponent -1.

[Official ice hockey manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=241)


#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .

### Version History

* v1: Breaking changes to entire API (1.4.0)
* v0: Initial versions release (1.0.0)
</div>
