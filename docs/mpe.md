## MPE environments

| Environment             | Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|-------------------------|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| simple                  | Vector       | Discrete | 1      | No             | (5)             | Discrete(5)             | (4)                      | (-inf,inf)         | ?          |
| simple_adversary        | Vector       | Discrete | 3      | No             | (5)             | Discrete(5)             | agent dependent max (10) | (-inf,inf)         | ?          |
| simple_crypto           | Vector       | Discrete | 2      | No             | (4)             | Discrete(4)             | agent dependent max (8)  | (-inf,inf)         | ?          |
| simple_push             | Vector       | Discrete | 2      | No             | (5)             | Discrete(5)             | agent dependent max (19) | (-inf,inf)         | ?          |
| simple_reference        | Vector       | Discrete | 2      | No             | (50)            | Discrete(50)            | (21)                     | (-inf,inf)         | ?          |
| simple_speaker_listener | Vector       | Discrete | 2      | No             | agent dependent max(5) | agent dependent  | agent dependent max (11) | (-inf,inf)         | ?          |
| simple_spread           | Vector       | Discrete | 3      | No             | (5)              | Discrete(5)             | (18)                     | (-inf,inf)         | ?          |
| simple_tag              | Vector       | Discrete | 4      | No             | (5)             | Discrete(5)             | agent dependent max (16) | (-inf,inf)         | ?          |
| simple_world_comm       | Vector       | Discrete | 6      | No             | agent dependent max(20) | agent dependent | agent dependent max (34) | (-inf,inf)         | ?          |


`pip install pettingzoo[mpe]`

*General notes on environments*

Please additionally cite:

Environments in this repo:
```
@article{lowe2017multi,
  title={Multi-Agent Actor-Critic for Mixed Cooperative-Competitive Environments},
  author={Lowe, Ryan and Wu, Yi and Tamar, Aviv and Harb, Jean and Abbeel, Pieter and Mordatch, Igor},
  journal={Neural Information Processing Systems (NIPS)},
  year={2017}
}
```
Original particle world environment:
```
@article{mordatch2017emergence,
  title={Emergence of Grounded Compositional Language in Multi-Agent Populations},
  author={Mordatch, Igor and Abbeel, Pieter},
  journal={arXiv preprint arXiv:1703.04908},
  year={2017}
}
```

### Simple

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 1      | No             | (5)             | Discrete(5)             | (4)                      | (-inf,inf)         | ?          |

`pettingzoo.mpe.simple`

Single agent sees landmark position, rewarded based on how close it gets to landmark. Not a multiagent environment -- used for debugging policies.

*arguments*

*about arguments*

### Simple Adversary

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 3      | No             | (5)             | Discrete(5)             | agent dependent max (10) | (-inf,inf)         | ?          |

`pettingzoo.mpe.simple_adversary`

1 adversary (red), N good agents (green), N landmarks (usually N=2). All agents observe position of landmarks and other agents. One landmark is the ‘target landmark’ (colored green). Good agents rewarded based on how close one of them is to the target landmark, but negatively rewarded if the adversary is close to target landmark. Adversary is rewarded based on how close it is to the target, but it doesn’t know which landmark is the target landmark. So good agents have to learn to ‘split up’ and cover all landmarks to deceive the adversary.

*arguments*

*about arguments*


### Simple Crypto

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 2      | No             | (4)             | Discrete(4)             | agent dependent max (8)  | (-inf,inf)         | ?          |

`pettingzoo.mpe.simple_crypto`

Two good agents (alice and bob), one adversary (eve). Alice must sent a private message to bob over a public channel. Alice and bob are rewarded based on how well bob reconstructs the message, but negatively rewarded if eve can reconstruct the message. Alice and bob have a private key (randomly generated at beginning of each episode), which they must learn to use to encrypt the message.

*arguments*

*about arguments*


### Simple Push

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 2      | No             | (50)            | Discrete(50)            | (21)                     | (-inf,inf)         | ?          |

`pettingzoo.mpe.simple_push`

1 agent, 1 adversary, 1 landmark. Agent is rewarded based on distance to landmark. Adversary is rewarded if it is close to the landmark, and if the agent is far from the landmark. So the adversary learns to push agent away from the landmark.

*arguments*

*about arguments*


### Simple Reference

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 2      | No             | (50)            | Discrete(50)            | (21)                     | (-inf,inf)         | ?          |

`pettingzoo.mpe.simple_reference`

2 agents, 3 landmarks of different colors. Each agent wants to get to their target landmark, which is known only by other agent. Reward is collective. So agents have to learn to communicate the goal of the other agent, and navigate to their landmark. This is the same as the simple_speaker_listener scenario where both agents are simultaneous speakers and listeners.

*arguments*

*about arguments*

### Simple Speaker Listener

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 2      | No             | agent dependent | agent dependent max(5)  | agent dependent max (11) | (-inf,inf)         | ?          |

`pettingzoo.mpe.simple_speaker_listener`

Same as simple_reference, except one agent is the ‘speaker’ (gray) that does not move (observes goal of other agent), and other agent is the listener (cannot speak, but must navigate to correct landmark).

*arguments*

*about arguments*

### Simple Spread

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 3      | No             | (5)             | Discrete(5)             | (18)                     | (-inf,inf)         | ?          |

`pettingzoo.mpe.simple_spread`

N agents, N landmarks. Agents are rewarded based on how far any agent is from each landmark. Agents are penalized if they collide with other agents. So, agents have to learn to cover all the landmarks while avoiding collisions.

*arguments*

*about arguments*


### Simple Tag

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 4      | No             | (5)             | Discrete(5)             | agent dependent max (16) | (-inf,inf)         | ?          |

`pettingzoo.mpe.simple_tag`

Predator-prey environment. Good agents (green) are faster and want to avoid being hit by adversaries (red). Adversaries are slower and want to hit good agents. Obstacles (large black circles) block the way.

*arguments*

*about arguments*


### Simple World Comm

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 6      | No             | agent dependent | agent dependent max(20) | agent dependent max (34) | (-inf,inf)         | ?          |

`pettingzoo.mpe.simple_world_comm`

Environment seen in the video accompanying the paper. Same as simple_tag, except (1) there is food (small blue balls) that the good agents are rewarded for being near, (2) we now have ‘forests’ that hide agents inside from being seen from outside; (3) there is a ‘leader adversary” that can see the agents at all times, and can communicate with the other adversaries to help coordinate the chase.

*arguments*

*about arguments*
