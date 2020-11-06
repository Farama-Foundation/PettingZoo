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
import: "from pettingzoo.atari import quadrapong_v1"
agent-labels: "agents= ['first_0', 'second_0', 'third_0', 'fourth_0']"
---

{% include info_box.md %}



Four player team battle.

Each player controls a paddle and defends a scoring area. However, this is a team game, and so two of the 4 scoring areas belong to the same team. So a given team must try to coordinate to get the ball away from their scoring areas towards their opponent's.

Scoring a point gives your team +1 reward and your opponent team -1 reward.

[Official Video Olympics manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=587)

#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .
