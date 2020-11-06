---
layout: "docu"
title: "Entombed: Competitive"
actions: "Discrete"
agents: "2"
manual-control: "No"
action-shape: "(1,)"
action-values: "[0,17]"
observation-shape: "(210, 160, 3)"
observation-values: "(0,255)"
import: "from pettingzoo.atari import entombed_competitive_v2"
agent-labels: "agents= ['first_0', 'second_0']"
---

{% include info_box.md %}




Entomb's competitive version is a race to last the longest.

You need to quickly navigate down a constantly generating
maze you can only see part of. If you get stuck, you lose.
Note you can easily find yourself in a dead-end excapable only through the use of rare power-ups.
In addition, there dangerous zombies lurking around to avoid.
Whenever your opponent dies, you get +1 reward, and your opponent gets -1 reward.

[Official Entombed manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=165)


#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .
