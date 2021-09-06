---
layout: "docu"
title: "Mario Bros"
actions: "Discrete"
agents: "2"
manual-control: "No"
action-shape: "(1,)"
action-values: "[0,17]"
observation-shape: "(210, 160, 3)"
observation-values: "(0,255)"
import: "from pettingzoo.atari import mario_bros_v2"
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




A mixed-sum game of planning and control.

The main goal is to kick a pest off the floor. This requires 2 steps:

1. Hit the floor below the pest, flipping it over. This knocks the pest on its back.
2. You to move up onto the floor where the pest is and you can kick it off. This earns +800 reward

Note that since this process has two steps there are opportunities for the two agents to either collaborate by helping each other knock pests over and collect them (potentially allowing both to collect reward more quickly), or for agents to steal the other's work.

If you run into an active pest or a fireball, you lose a life. If you lose all your lives, you are done, and the other player keeps playing. You can gain a new life after earning 20000 points.

There are other ways of earning points, by collecting bonus coins or wafers, earning 800 points each.

[Official mario bros manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=286)

#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .

### Version History

* v2: Breaking changes to entire API (1.4.0)
* v1: Fixes to how all environments handle premature death (1.3.0)
* v0: Initial versions release (1.0.0)
</div>
