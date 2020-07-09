
## MAgent environments

| Environment                              | Actions  | Agents | Manual Control | Action Shape | Action Values    | Observation Shape      | Observation Values |
|------------------------------------------|----------|--------|----------------|--------------|------------------|------------------------|--------------------|
| [adversarial pursuit](adversarial_pursuit)             | Discrete | 75     | No             | (9),(13)     | Discrete(9),(13) | (10,10,19), (9,9,15)    | [0,2]              |
| [battle](battle)               | Discrete | 162    | No             | (21)         | Discrete(21)     | (13,13,41)             | [0,2]              |
| [battlefield](battlefield)     | Discrete | 24     | No             | (21)         | Discrete(21)     | (13,13,41)             | [0,2]              |
| [combined arms](combined_arms) | Discrete | 162    | No             | (9),(25)     | Discrete(9),(25) | (13,13,35), (13,13,51) | [0,2]              |
| [gather](gather)               | Discrete | 495    | No             | (33)         | Discrete(33)     | (15,15,43)             | [0,2]              |
| [tiger_deer](tiger_deer)       | Discrete | 121    | No             | (5),(9)      | Discrete(5),(9)  | (3,3,21), (9,9,25)      | [0,2]              |


`pip install pettingzoo[magent]`

MAgent is a set of environments where large numbers of agents interact in battles or other competitive scenarios.
These environments are derived from the [MAgent](https://github.com/geek-ai/MAgent) codebase.

### Types of Environments

All environments except gather are competitive team games where each team must cooperate to defeat the other team. Note that reward is allocated entirely individually, so the team coordination, if any, must arise out of emergent behavior.

Gather is a survival game where agents must try to keep alive either by gathering the food or by killing other agents.

### Key Concepts

* HP decay: In gather and the tigers in tiger_deer, the HP decays over time, so the agents slowly lose HP until they die. The only way to prevent this is to eat something.

* HP recovery: In battle games, agents recover HP over time, so low HP agents can hide or be protected until they heal.

* Observation view: All agents see a certain distance around itself. It sees whether the coordinate is empty, an obstacle, or if there is an agent as entries in different channels. It signals an agent's HP by labeling the observation with the fraction of total HP.

* Feature vector: The feature vector contains <agent_id, action, last_reward>

* Observation concatenates the 1d feature vector with 3d observation view by repeating the value of the feature across an entire image channel.

* Minimap Mode: For the battle games (battle, battlefield, combined_arms), the agents have access to additional global information: two density map of the team's respective presences on the map binned and appended onto the agent's observation view. Their own absolute position on the global map is appended to the feature vector.

* An action can either be an attack or a move, not both. So the action space is the concatenations of all possible moves and all possible attacks.  

### Termination

The game terminates after all agents of either team have died. This means that the battle environments, where HP heals over time instead of decays, the games will go on indefinitely with random actions.


### Citation

The MAgent environments were originally created for the following work:

```
@article{DBLP:journals/corr/abs-1712-00600,
  author    = {Lianmin Zheng and
               Jiacheng Yang and
               Han Cai and
               Weinan Zhang and
               Jun Wang and
               Yong Yu},
  title     = {MAgent: {A} Many-Agent Reinforcement Learning Platform for Artificial
               Collective Intelligence},
  journal   = {CoRR},
  volume    = {abs/1712.00600},
  year      = {2017},
  url       = {http://arxiv.org/abs/1712.00600},
  archivePrefix = {arXiv},
  eprint    = {1712.00600},
  timestamp = {Sun, 21 Apr 2019 10:04:41 +0200},
  biburl    = {https://dblp.org/rec/journals/corr/abs-1712-00600.bib},
  bibsource = {dblp computer science bibliography, https://dblp.org}
}
```

Please cite this paper if you use these environments in your research.
