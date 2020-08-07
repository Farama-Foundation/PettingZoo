
## MAgent environments


{% include bigtable.html group="magent/" %}


`pip install pettingzoo[magent]`

MAgent is a set of environments where large numbers of pixel agents in a gridworld interact in battles or other competitive scenarios.
These environments were originally derived from the [MAgent](https://github.com/geek-ai/MAgent) codebase.

### Types of Environments

All environments except gather are competitive team games where each team must cooperate to defeat the other team. Note that reward is allocated entirely individually, so the team coordination, if any, must arise out of emergent behavior.

Gather is a survival game where agents must try to keep alive either by gathering the food or by killing other agents.

### Key Concepts

* HP decay: In Gather and for the tigers in Tiger Deer, agent's HP decays over time, so the agents slowly lose HP until they die. The only way to prevent this is to eat something.

* HP recovery: In battle games, agents recover HP over time, so low HP agents can hide or be protected until they heal.

* Observation view: All agents observe a box around themselves. They see whether the coordinates is empty, an obstacle, or if there is an agent as entries in different channels. If an agent in on a coordinate, that entry will contain the value (agent's HP / max agent HP).

* Feature vector: The feature vector contains <agent_id, action, last_reward>

* Observation concatenates the 1d feature vector with 3d observation view by repeating the value of the feature across an entire image channel.

* Minimap mode: For the battle games (Battle, Battlefield, Combined Arms), the agents have access to additional global information: two density map of the team's respective presences on the map binned and concatenated onto the agent's observation view (concatenated in the channel dimension, axis=2). Their own absolute position on the global map is appended to the feature vector.

* Moving and attacking: An agent can only act or move with a single action, so the action space is the concatenations of all possible moves and all possible attacks.

### Termination

The game terminates after all agents of either team have died. This means that the battle environments, where HP heals over time instead of decays, the game will go on for a very long time with random actions.


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
