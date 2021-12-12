---
layout: "docu"
title: "Double Dunk"
actions: "Discrete"
agents: "2"
manual-control: "No"
action-shape: "(1,)"
action-values: "[0,17]"
observation-shape: "(210, 160, 3)"
observation-values: "(0,255)"
import: "from pettingzoo.atari import double_dunk_v2"
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



An adversarial game that combines control and precise selection.

The game has two stages: selection and play. Selection can be
difficult because you have to hold the same action for a few steps and then
take the 0 action. Strategy choice is timed: if a player does not select any action after 2 seconds (120 frames)
then the player is rewarded -1, and the timer resets. This prevents one player from indefinitely stalling the game, but also means it is no longer a purely zero sum game.

Once play begins, each team has two players. You only control
one at a time, and and which one you control depends on the selected play.
Scoring should be familiar to basketball fans (2-3 points per successful shot).

[Official double dunk manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=153)


#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .

### Version History

* v2: No action timer (1.9.0)
* v1: Breaking changes to entire API (1.4.0)
* v0: Initial versions release (1.0.0)
</div>
