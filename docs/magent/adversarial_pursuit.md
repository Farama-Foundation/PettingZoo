---
actions: "Discrete"
title: "Adversarial Pursuit"
agents: "75"
manual-control: "No"
action-shape: "(9),(13)"
action-values: "Discrete(9),(13)"
observation-shape: "(9,9,15), (10,10,19)"
observation-values: "[0,2]"
import: "pettingzoo.magent import adversarial_pursuit_v1"
agent-labels: "agents= [predator_[0-24], prey_[0-49]]"
---

{% include info_box.md %}



The red agents must navigate the obstacles and attack the blue agents. The blue agents should try to avoid being attacked. Since the red agents are slower (but larger) than the blue agents, they must work together to trap the blue agents, so they can attack them continually (note that they blue agent's won't die if attacked, so they can be used as an infinite source of reward).

Predator action options: `[do_nothing, move_4, attack_8]`

Predator's reward is given as:

* 1 reward for attacking a prey
* -0.2 reward for attacking (attack_penalty option)

Prey action options: `[do_nothing, move_8]`

Prey's reward is given as:

* -1 reward for being attacked

Observation space: `[empty, obstacle, predators, prey, one_hot_action, last_reward]`

Map size: 45x45

### Arguments

```
adversarial_pursuit_v1.env(attack_penalty=-0.2, max_frames=500)
```


`attack_penalty`:  Adds the following value to the reward whenever an attacking action is taken

`max_frames`:  number of frames (a step for each agent) until game terminates
