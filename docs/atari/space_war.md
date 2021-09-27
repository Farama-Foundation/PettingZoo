---
layout: "docu"
title: "Space War"
alt_title: "Spacewar"
actions: "Discrete"
agents: "2"
manual-control: "No"
action-shape: "(1,)"
action-values: "[0,17]"
observation-shape: "(250, 160, 3)"
observation-values: "(0,255)"
import: "from pettingzoo.atari import space_war_v1"
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




*Space war* is an competitive game where prediction and positioning are key.

The players move around the map. When your opponent is hit by your bullet,
you score a point. The game is similar to combat, but with a more advanced physics system where acceleration and momentum need to be taken into account.

Whenever you score a point, you are rewarded +1 and your opponent is penalized -1.

[Official space war manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=470)

#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .

### Version History

* v1: Breaking changes to entire API (1.4.0)
* v0: Initial versions release (1.0.0)
</div>
