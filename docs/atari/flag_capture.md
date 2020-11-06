---
layout: "docu"
title: "Flag Capture"
actions: "Discrete"
agents: "2"
manual-control: "No"
action-shape: "(1,)"
action-values: "[0,17]"
observation-shape: "(210, 160, 3)"
observation-values: "(0,255)"
import: "from pettingzoo.atari import flag_capture_v1"
agent-labels: "agents= ['first_0', 'second_0']"
---

{% include info_box.md %}




A battle of memory and information.

A flag is hidden
on the map.
You can travel through the map and check
the squares in it. If it is the flag,
you score a point (and your opponent is penalized).
If it is a bomb, you get sent back to your starting location.
Otherwise, it will give you a hint to where the flag is,
either a direction or a distance.
Your player needs to be able to use information from both
your own search and your opponent's search in order to
narrow down the location of the flag quickly and effectively.

[Official flag capture manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=183)


#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .
