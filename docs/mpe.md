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

The MPE environments were originally described in the following work:

```
@article{mordatch2017emergence,
  title={Emergence of Grounded Compositional Language in Multi-Agent Populations},
  author={Mordatch, Igor and Abbeel, Pieter},
  journal={arXiv preprint arXiv:1703.04908},
  year={2017}
}
```

But were first released as a part of this work:

```
@article{lowe2017multi,
  title={Multi-Agent Actor-Critic for Mixed Cooperative-Competitive Environments},
  author={Lowe, Ryan and Wu, Yi and Tamar, Aviv and Harb, Jean and Abbeel, Pieter and Mordatch, Igor},
  journal={Neural Information Processing Systems (NIPS)},
  year={2017}
}
```

Please cite one or both of these if you use these environments in your research.

### Simple

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 1      | No             | (5)             | Discrete(5)             | (4)                      | (-inf,inf)         | ?          |

`pettingzoo.mpe.simple`

*gif*

*AEC diagram*

In this environment, a single agent sees landmark position, and is rewarded based on how close it gets to landmark. This is not a multiagent environment, and is primarily intended for debugging purposes.


### Simple Adversary

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 3      | No             | (5)             | Discrete(5)             | agent dependent max (10) | (-inf,inf)         | ?          |

`pettingzoo.mpe.simple_adversary`

In this environment, there is 1 adversary (red), N good agents (green), N landmarks (usually N=2). All agents observe the position of landmarks and other agents. One landmark is the ‘target landmark’ (colored green). Good agents rewarded based on how close one of them is to the target landmark, but negatively rewarded if the adversary is close to target landmark. The adversary is rewarded based on how close it is to the target, but it doesn’t know which landmark is the target landmark. This means good agents have to learn to ‘split up’ and cover all landmarks to deceive the adversary.


### Simple Crypto

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 2      | No             | (4)             | Discrete(4)             | agent dependent max (8)  | (-inf,inf)         | ?          |

`pettingzoo.mpe import simple_crypto`

*gif*

*AEC diagram*

In this environment, there are 2 good agents (Alice and Bob) and 1 adversary (Eve). Alice must sent a private message to Bob over a public channel. Alice and Bob are rewarded based on how well Bob reconstructs the message, but are negatively rewarded if Eve can reconstruct the message. Alice and Bob have a private key (randomly generated at beginning of each episode), which they must learn to use to encrypt the message.


### Simple Push

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 2      | No             | (50)            | Discrete(50)            | (21)                     | (-inf,inf)         | ?          |

`pettingzoo.mpe import simple_push`

*gif*

*AEC diagram*

This environment has 1 good agent, 1 adversary, and 1 landmark. The good agent is rewarded based on the distance to the landmark. The adversary is rewarded if it is close to the landmark, and if the agent is far from the landmark. Thus the adversary must learn to push the good agent away from the landmark.


### Simple Reference

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 2      | No             | (50)            | Discrete(50)            | (21)                     | (-inf,inf)         | ?          |

`pettingzoo.mpe import simple_reference`

This environment has 2 agents and 3 landmarks of different colors. Each agent wants to get to their target landmark, which is known only by the other agents. The reward is collective, so agents have to learn to communicate the goal of the other agent, and navigate to their landmark. Both agents are simultaneous speakers and listeners.

*gif*

*AEC diagram*


### Simple Speaker Listener

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 2      | No             | agent dependent | agent dependent max(5)  | agent dependent max (11) | (-inf,inf)         | ?          |

`pettingzoo.mpe import simple_speaker_listener`

This environment is similar to simple_reference, except that one agent is the ‘speaker’ (gray) and can speak but cannot move, while the other agent is the listener (cannot speak, but must navigate to correct landmark).


### Simple Spread

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 3      | No             | (5)             | Discrete(5)             | (18)                     | (-inf,inf)         | ?          |

`pettingzoo.mpe import simple_spread`

*gif*

*AEC diagram*

This environment has N agents, N landmarks. The agents are rewarded based on how far any agent is from each landmark, but are penalized if they collide with other agents. Agents must learn to cover all the landmarks while avoiding collisions.


### Simple Tag

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 4      | No             | (5)             | Discrete(5)             | agent dependent max (16) | (-inf,inf)         | ?          |

`pettingzoo.mpe import simple_tag`

*gif*

*AEC diagram*

This is a predator-prey environment. Good agents (green) are faster and recieve a negative reward for being hit by adversaries (red). Adversaries are slower and are rewarded for hitting good agents. Obstacles (large black circles) block the way.


### Simple World Comm

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 6      | No             | agent dependent | agent dependent max(20) | agent dependent max (34) | (-inf,inf)         | ?          |

`pettingzoo.mpe import simple_world_comm`

*gif*

*AEC diagram*

This environment is similar to simple_tag, except there is food (small blue balls) that the good agents are rewarded for being near, there are ‘forests’ that hide agents inside from being seen, and there is a ‘leader adversary' that can see the agents at all times and can communicate with the other adversaries to help coordinate the chase.
