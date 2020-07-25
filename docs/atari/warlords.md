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
import: "from pettingzoo.atari import warlords_v0"
agent-labels: "agents= ['first_0', 'second_0', 'third_0', 'fourth_0']"
---

## Warlords

<div class="floatright" markdown="1">

![warlords gif](atari_warlords.gif)

This environment is part of the [Atari environments](../atari). Please read that page first for general information.

{% include table.md %}

</div>



Four player last man standing!

Defend your fortress from the ball and hit it towards your opponents.

When your fortress falls, you receive -1 reward and are done. If you are the last player standing, you receive +1 reward.

[Official wizard_of_wor manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=598)

#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .
