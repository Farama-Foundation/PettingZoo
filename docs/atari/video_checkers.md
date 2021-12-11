---
layout: "docu"
title: "Video Checkers"
actions: "Discrete"
agents: "2"
manual-control: "No"
action-shape: "(1,)"
action-values: "[0,17]"
observation-shape: "(210, 160, 3)"
observation-values: "(0,255)"
import: "from pettingzoo.atari import video_checkers_v3"
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




A classical strategy game with arcade style controls.

Capture all of your opponents pieces by jumping over them. To move a piece, you must select a piece by hovering the cursor and pressing fire (action 1), moving the cursor, and pressing fire again. Note that the buttons must be held for multiple frames to be registered.

If you win by capturing all your opponent's pieces, you are rewarded +1 and your opponent -1.

This is a timed game: if a player does not take a turn after 10 seconds, then that player is rewarded -1 points, their opponent is rewarded nothing, and the timer resets. This prevents one player from indefinitely stalling the game, but also means it is no longer a purely zero sum game.


[Official video checkers manual](https://atariage.com/manual_html_page.php?SoftwareID=1427)

#### Environment parameters

Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .

### Version History

* v3: No action timer (1.9.0)
* v2: Fixed checkers rewards (1.5.0)
* v1: Breaking changes to entire API (1.4.0)
* v0: Initial versions release (1.0.0)
</div>
