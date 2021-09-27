---
layout: env_selection
title: MPE Environments
---
<div class="selection-content" markdown="1">

The unique dependencies for this set of environments can be installed via:

````bash
pip install pettingzoo[mpe]
````

Multi Particle Environments (MPE) are a set of communication oriented environment where particle agents can (sometimes) move, communicate, see each other, push each other around, and interact with fixed landmarks.

These environments are from [OpenAI's MPE](https://github.com/openai/multiagent-particle-envs) codebase, with several minor fixes, mostly related to making the action space discrete by default, making the rewards consistent and cleaning up the observation space of certain environments.

### Types of Environments

The Simple Adversary, Simple Crypto, Simple Push, Simple Tag, and Simple World Comm environments are adversarial (a "good" agent being rewarded means an "adversary" agent is punished and vice versa, though not always in a perfectly zero-sum manner). In most of these environments, there are "good" agents rendered in green and an "adversary" team rendered in red.

The Simple Reference, Simple Speaker Listener, and Simple Spread environments are cooperative in nature (agents must work together to achieve their goals, and received a mixture of rewards based on their own success and the success of the other agents).

### Key Concepts

* **Landmarks**: Landmarks are static circular features of the environment that cannot be controlled. In some environments, like Simple, they are destinations that affect the rewards of the agents depending on how close the agents are to them. In other environments, they can be obstacles that block the motion of the agents. These are described in more detail in the documentation for each environment.

* **Visibility**: When an agent is visible to a another agent, that other agent's observation contains the first agent's relative position (and in Simple World Comm and Simple Tag, the first agent's velocity). If an agent is temporarily hidden (only possible in Simple World Comm) then the agent's position and velocity is set to zero.

* **Communication**: Some agents in some environments can broadcast a message as a part of its action (see action space for more details) which will be transmitted to each agent that is allowed to see that message. In Simple Crypto, this message is used to signal that Bob and Eve have reconstructed the message.

* **Color**: Since all agents are rendered as circles, the agents are only identifiable to a human by their color, so the color of the agents is described in most of the environments. The color is not observed by the agents.

* **Distances**: The landmarks and agents typically start out uniformly randomly placed from -1 to 1 on the map. This means they are typically around 1-2 units apart. This is important to keep in mind when reasoning about the scale of the rewards (which often depend on distance) and the observation space, which contains relative and absolute positions.

### Termination

The game terminates after the number of cycles specified by the `max_cycles` environment argument is executed. The default for all environments is 25 cycles, as in the original OpenAI source code.

### Observation Space

The observation space of an agent is a vector generally composed of the agent's position and velocity, other agents' relative positions and velocities, landmarks' relative positions, landmarks' and agents' types, and communications received from other agents. The exact form of this is detailed in the environments' documentation.

If an agent cannot see or observe the communication of a second agent, then the second agent is not included in the first's observation space, resulting in varying observation space sizes in certain environments.

### Action Space

Note: [OpenAI's MPE](https://github.com/openai/multiagent-particle-envs) uses continuous action spaces by default.

Discrete action space (Default):

The action space is a discrete action space representing the combinations of movements and communications an agent can perform. Agents that can move can choose between the 4 cardinal directions or do nothing. Agents that can communicate choose between 2 and 10 environment-dependent communication options, which broadcast a message to all agents that can hear it.

Continuous action space (Set by continuous_actions=True):

The action space is a continuous action space representing the movements and communication an agent can perform. Agents that can move can input a velocity between 0.0 and 1.0 in each of the four cardinal directions, where opposing velocities e.g. left and right are summed together. Agents that can communicate can output a continuous value over each communication channel in the environment which they have access to.

### Rendering

Rendering displays the scene in a window that automatically grows if agents wander beyond its border. Communication is rendered at the bottom of the scene. The `render()` method also returns the pixel map of the rendered area.

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

</div>
<div class="selection-table-container" markdown="1">
## MPE

{% include bigtable.html group="mpe/" cols=3 %}
</div>