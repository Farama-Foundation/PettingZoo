---
layout: docu
actions: Discrete
agents: 2
manual-control: No
action-shape: (1,)
action-values: [0,17]
observation-shape: (210, 160, 3)
observation-values: (0,255)
---


### Tennis



This environment is part of the [Atari environments](../atari). Please read that page first for general information.





`from pettingzoo.atari import tennis_v0`



`agents= ["first_0", "second_0"]`



![tennis gif](atari_tennis.gif)



*AEC diagram*



A competitive game of positioning and prediction.



Goal: Get the ball past your opponent. Don't let the ball get past you.



When a point is scored (by the ball exiting the area), you get +1 reward and your opponent gets -1 reward. Unlike normal tennis matches, the number of games won is not directly rewarded.



[Official tennis manual](https://atariage.com/manual_html_page.php?SoftwareLabelID=555)



#### Environment parameters



Environment parameters are common to all Atari environments and are described in the [base Atari documentation](../atari) .
