---
actions: "Either"
title: "Prison"
agents: "8"
manual-control: "Yes"
action-shape: "(1,)"
action-values: "[0, 2]"
observation-shape: "(100, 300, 3) or (1,)"
observation-values: "(0, 255) or (-300, 300)"
state-shape: "(650, 750, 3)"
state-values: "(0, 255)"
average-total-reward: "2.77"
import: "from pettingzoo.butterfly import prison_v3"
agent-labels: "agents= ['prisoner_0', 'prisoner_1', ..., 'prisoner_7']"
---


<div class="docu-info" markdown="1">
{% include info_box.md %}
</div>

<div class="docu-content" markdown="1">
<div class="appear_big env-title" markdown="1">
{% include env_icon.md %}
## {{page.title}}
</div>





In prison, 8 aliens locked in identical prison cells are controlled by the user. They cannot communicate with each other in any way, and can only pace in their cell. Every time they touch one end of the cell and then the other, they get a reward of 1. Due to the fully independent nature of these agents and the simplicity of the task this is an environment primarily intended for debugging purposes - its multiple individual purely single agent tasks. To make this debugging tool as compatible with as many methods as possible it can accept both discrete and continuous actions and the observation can be automatically turned into a number representing position of the alien from the left of its cell instead of the normal graphical output.

### Manual Control

Select different aliens with 'W', 'A', 'S' or 'D'. Move the selected alien left with 'J' and right with 'K'.


### Arguments

``` python
prison_v3.env(vector_observation=False, continuous=False, synchronized_start=False,
identical_aliens=False, max_cycles=150, num_floors=4, random_aliens=False)
```


`vector_observation`:  If set to False an image of the prisoner's cell is observed. If set to True, the distance to the left side wall is returned.

`continuous`:  If False, each agent action is a discrete value indicating whether to move left or right one unit. If True, each agent action represents a real value that is added to the agent's x position

`synchronized_start`:  If set to true, all aliens will start in the same x position, relative to their cells. Otherwise, their position is random.

`num_floors`:  A floor contains two aliens. Add more or fewer floor to increase or decrease the number of agents in the environment.

`identical_aliens`:  If set to true, each alien will have the some randomly chosen sprite. This argument overrides the random_aliens argument.

`random_aliens`:  If set to True, each alien's sprite is randomly chosen from all possible sprites. If random_aliens and synchronized_aliens are both False, each alien's sprite is chosen cyclically from all possible sprites.

`max_cycles`:  after max_cycles steps all agents will return done


### Version History

* v3: Changed default argument for `max_cycles`  (1.6.0)
* v2: Misc fixes, bumped PyGame and PyMunk version (1.4.0)
* v1: Fix to continuous mode (1.0.1)
* v0: Initial versions release (1.0.0)
</div>