## MPE environments

| Environment             | Observations | Actions  | Agents | Manual Control | Action Shape | Action Values    | Observation Shape | Observation Values | Num States |
|-------------------------|--------------|----------|--------|----------------|--------------|------------------|-------------------|--------------------|------------|
| [simple](mpe/simple.md)                  | Vector       | Discrete | 1      | No             | (5)          | Discrete(5)      | (4)               | (-inf,inf)         | ?          |
| [simple_adversary](mpe/simple_adversary.md)        | Vector       | Discrete | 3      | No             | (5)          | Discrete(5)      | (8),(10)          | (-inf,inf)         | ?          |
| [simple_crypto](mpe/simple_crypto.md)           | Vector       | Discrete | 2      | No             | (4)          | Discrete(4)      | (4),(8)           | (-inf,inf)         | ?          |
| [simple_push](mpe/simple_push.md)             | Vector       | Discrete | 2      | No             | (5)          | Discrete(5)      | (8),(19)          | (-inf,inf)         | ?          |
| [simple_reference](mpe/simple_reference.md)        | Vector       | Discrete | 2      | No             | (50)         | Discrete(50)     | (21)              | (-inf,inf)         | ?          |
| [simple_speaker_listener](mpe/simple_speaker_listener.md) | Vector       | Discrete | 2      | No             | (3),(5)      | Discrete(3),(5)  | (3),(11)          | (-inf,inf)         | ?          |
| [simple_spread](mpe/simple_spread.md)           | Vector       | Discrete | 3      | No             | (5)          | Discrete(5)      | (18)              | (-inf,inf)         | ?          |
| [simple_tag](mpe/simple_tag.md)              | Vector       | Discrete | 4      | No             | (5)          | Discrete(5)      | (14),(16)         | (-inf,inf)         | ?          |
| [simple_world_comm](mpe/simple_world_comm.md)       | Vector       | Discrete | 6      | No             | (5),(20)     | Discrete(5),(20) | (28),(34)         | (-inf,inf)         | ?          |


`pip install pettingzoo[mpe]`

Multi Particle Environments (MPE) are a set of communication oriented environment where particle agents can (sometimes) move, communicate, see each other, push each other around, and interact with fixed landmarks.

These environments are from [OpenAI's MPE](https://github.com/openai/multiagent-particle-envs) codebase, with several minor fixes, mostly related to making the action space discrete, making the rewards consistent and cleaning up the observation space of certain environments.

### Types of Environments

The simple_adversary, simple_crypto, simple_push, simple_tag, simple_world_comm are adversarial- a "good" agent being rewarded means an "adversary" agent is punished and vice versa (though not always in a perfectly zero-sum manner). In most of these environments, there are "good" agents rendered in green and a "adversary" team rendered in red.

The simple_reference, simple_speaker_listener, and simple_spread environments are cooperative in nature: agents must work together to achieve their goals, and received a mixture of rewards based on their own success and the success of the other agents.

### Key Concepts

* Landmarks: Landmarks are static circular features of the environment that cannot be controlled. In some environments, like simple, they are destinations that affect the rewards of the agents depending on how close the agents are to them. In other environments, they can be obstacles that block the motion of the agents. These are described in more details for each environment.

* Visibility: When an agent is visible to another, the other agent's observation contains the agent's relative position (and in simple_world_comm and simple_tag, the agent's velocity). If the agent is temporarily hidden (only possible in simple_world_comm) the agent's position and velocity is set to zero.

* Communication: Some agents in some environments can broadcast a message as part of its action (see action space for more details) which will be transmitted to each agent that is allowed to see that message. In simple_crypto, this message is also used to signal that Bob and Eve have reconstructed the message.

* Color: Since all agents are rendered as circles, the agents are only identifiable to a human by their color, so the color of the agents is described in most of the environments. The color is not observed by the agents.

* Distances: The landmarks and agents typically start out uniformly randomly placed from -1. to 1. on the map. This means they are typically around 1-2 units distance apart, so keep that in mind when reasoning about the scale of the rewards, which often depend on distance, and the observation space, which contain relative and absolute positions.

### Termination

The game terminates after a number of cycles specified by the `max_frames` environment argument is executed. The default for all environments is 100 cycles. Note that in the original source code, the default value was 25, not 100.

### Observation Space

The observation space of an agent is a vector generally composed of the agent's position and velocity, other agent's relative position and velocity, the landmarks relative positions, the landmark's and agent's types, and communications it received from other agents. The exact form of this is detailed in the environments.

If an agent_1 cannot see or observe the communication of agent_2, then agent_2 is not included in agent_1's observation space, resulting in varying observation space sizes in certain environments.

### Action Space

The action space is a discrete action space representing the combinations of the movements and communications an agent can perform. Agents that can move can choose between the 4 cardinal directions and do nothing. Agents that can communicate choose between 2 and 10 environment dependent options, and the message is broadcast all agents which can hear it.

### Rendering

Rendering displays the scene in a window that automatically grows if agents wander beyond its border. Communication is rendered at the bottom of the scene. Render also method returns the pixel map of the rendered area.

### Citation

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
