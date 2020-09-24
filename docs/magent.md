
## MAgent environments


{% include bigtable.html group="magent/" %}

The unique dependencies for this set of environments can be installed via:

````bash
pip install pettingzoo[magent]
````

MAgent is a set of environments where large numbers of pixel agents in a gridworld interact in battles or other competitive scenarios. These environments were originally derived from the [MAgent](https://github.com/geek-ai/MAgent) codebase.

### Types of Environments

All environments except Gather are competitive team games where each team must cooperate to defeat the other team. Note that reward is allocated entirely individually, so the team coordination, if any, must arise out of emergent behavior.

Gather is a survival game where agents must try to stay alive either by gathering the food or by killing other agents.

### Key Concepts

* **HP decay**: The agents in Gather and the tigers in Tiger-Deer have HP (health points) that decays over time, so the agents slowly lose HP until they die. The only way to prevent this is by eating something.

* **HP recovery**: In battle games, agents recover HP over time, so low HP agents can hide or be protected until they heal.

* **Observation view**: All agents observe a box around themselves. They see whether the coordinates are empty, contain an obstacle, or contain an agent in any of the observation channels. If an agent in on a coordinate, that entry will contain the value (agent's HP / max agent HP).

* **Feature vector**: The feature vector contains `<agent_id, action, last_reward>`

* Observation concatenates the 1D feature vector with 3D observation view by repeating the value of the feature across an entire image channel.

* **Minimap mode**: For the battle games (Battle, Battlefield, Combined Arms), the agents have access to additional global information: two density maps of the teams' respective presences on the map that are binned and concatenated onto the agent's observation view (concatenated in the channel dimension, axis=2). Their own absolute positions on the global map is appended to the feature vector.

* **Moving and attacking**: An agent can only act or move with a single action, so the action space is the concatenations of all possible moves and all possible attacks.

### Termination

The game terminates after all agents of either team have died. This means that in the battle environments, where HP heals over time instead of decays, the game will go on for a very long time with random actions.

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
