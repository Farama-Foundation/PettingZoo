---
layout: "docu"
title: "Warlords"
actions: "Discrete"
agents: "4"
manual-control: "No"
action-shape: "(1,)"
action-values: "[0,17]"
observation-shape: "(210, 160, 3)"
observation-values: "(0,255)"
import: "from pettingzoo.atari import warlords_v2"
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




Four player last man standing!

Defend your fortress from the ball and hit it towards your opponents.

When your fortress falls, you receive -1 reward and are done. If you are the last player standing, you receive +1 reward.

[Official wizard_of_wor manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=598)

#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .

### Version History

* v2: Breaking changes to entire API (1.4.0)
* v1: Fixes to how all environments handle premature death (1.3.0)
* v0: Initial versions release (1.0.0)
</div>
