---
layout: env_selection
title: MAgent Environments
---
<div class="selection-content" markdown="1">

The unique dependencies for this set of environments can be installed via:

````bash
pip install pettingzoo[magent]
````

MAgent is a set of environments where large numbers of pixel agents in a gridworld interact in battles or other competitive scenarios. These environments were originally derived from the [MAgent](https://github.com/geek-ai/MAgent) codebase.

### Types of Environments

All environments, except Gather, are competitive team games where agents in each team must cooperate to defeat the other team. Note that reward is allocated entirely individually.

Gather is a competitive free for all game where agents try to stay alive for as long as possible, either by gathering food or killing other agents.

### Key Concepts

* **Observation view**: All agents observe a box around themselves. They see whether the coordinates are empty, contain an obstacle, or contain an agent in any of the observation channels. If an agent is on a coordinate, that entry will contain the value (agent's HP / max agent HP).

* **Feature vector**: The feature vector contains information about the agent itself, rather than its surrounding. In normal mode it contains `<agent_id, action, last_reward>`, in minimap mode it also contains the agent position on the map, normalized to 0-1.

* **Observation**: The observation is 3D observation view concatenated with the 1D feature vector by repeating the value of the feature across an entire image channel.

* **Minimap mode**: For most of the games (Battle, Battlefield, Combined Arms, Gather), the agents have access to additional global information: two density maps of the teams' respective presences on the map that are binned and concatenated onto the agent's observation view (concatenated in the channel dimension, axis=2). Their own absolute positions on the global map is appended to the feature vector. This feature can be turned on or off with the `minimap_mode` environment argument.

* **Moving and attacking**: An agent can only act or move each step, so the action space is the concatenations of all possible moves and all possible attacks.

* **State** *: A global observation of the environment can be retrieved by calling `env.state()`. The state observation space is a 3D observation of the complete map with dimensions equal to the map size. The first channel shows the walls in the map, where each element represents if the coordinate is empty or has an obstacle. Concatenated to this channel there is another pair of channels for each agent type, which sees if the coordinates contain an agent of that type bined to the value (agent's HP/ max agent HP). If extra features are selected the respective feature vector is concatenated and bined to each agent in the observation state.

### Termination

The game terminates after all agents of either team have died. This means that in the battle environments, where HP heals over time instead of decays, the game will go on for a very long time with random actions.

### Citation

The MAgent environments were originally created for the following work:

```
@article{DBLP:journals/corr/abs-1712-00600,
  author    = {Lianmin Zheng and Jiacheng Yang and Han Cai and Weinan Zhang and Jun Wang and Yong Yu},
  title     = {MAgent: {A} Many-Agent Reinforcement Learning Platform for Artificial Collective Intelligence},
  journal   = {CoRR},
  volume    = {abs/1712.00600},
  year      = {2017},
  url       = {http://arxiv.org/abs/1712.00600},
  eprint    = {1712.00600},
}
```

Please cite this paper if you use these environments in your research.

</div>
<div class="selection-table-container" markdown="1">
## MAgent

{% include bigtable.html group="magent/" cols=3 %}
</div>
