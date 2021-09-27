---
layout: "docu"
title: "Wizard of Wor"
alt_title: "WizardOfWor"
actions: "Discrete"
agents: "2"
manual-control: "No"
action-shape: "(1,)"
action-values: "[0,17]"
observation-shape: "(210, 160, 3)"
observation-values: "(0,255)"
import: "from pettingzoo.atari import wizard_of_wor_v2"
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




Battling both against NPCs and the other player. Careful timing,
and control is essential, as well as awareness of your opponent.

You score points by hitting the opponent and NPCs with your bullets. Hitting an NPC scores between 200 to 2500 points depending on the NCP, and hitting a player scores 1000 points.

If you get hit by a bullet, you lose a life. When both players lose 3 lives, the game is over.

Note that in addition to the competitive aspect where you benefit from attacking the other player, there is a cooperative aspect to the game where clearing levels means that both players will have more opportunities to score.

[Official Warlords manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=593)

#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .

### Version History

* v2: Breaking changes to entire API (1.4.0)
* v1: Fixes to how all environments handle premature death (1.3.0)
* v0: Initial versions release (1.0.0)
</div>
