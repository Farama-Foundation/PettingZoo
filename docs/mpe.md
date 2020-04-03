## MPE environments

| Environment             | Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|-------------------------|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| simple                  | Vector       | Discrete | 1      | No             | (5)             | Discrete(5)             | (4)                      | (-inf,inf)         | ?          |
| simple_adversary        | Vector       | Discrete | 3      | No             | (5)             | Discrete(5)             | agent dependent (8),(10) | (-inf,inf)         | ?          |
| simple_crypto           | Vector       | Discrete | 2      | No             | (4)             | Discrete(4)             | (4), (8)  | (-inf,inf)         | ?          |
| simple_push             | Vector       | Discrete | 2      | No             | (5)             | Discrete(5)             | (8), (19) | (-inf,inf)         | ?          |
| simple_reference        | Vector       | Discrete | 2      | No             | (50)            | Discrete(50)            | (21)                     | (-inf,inf)         | ?          |
| simple_speaker_listener | Vector       | Discrete | 2      | No             | (3),(5) | agent dependent  | agent dependent (3),(11) | (-inf,inf)         | ?          |
| simple_spread           | Vector       | Discrete | 3      | No             | (5)              | Discrete(5)             | (18)                     | (-inf,inf)         | ?          |
| simple_tag              | Vector       | Discrete | 4      | No             | (5)             | Discrete(5)             | (14),(16) | (-inf,inf)         | ?          |
| simple_world_comm       | Vector       | Discrete | 6      | No             | (5),(20) | agent dependent | (28), (34) | (-inf,inf)         | ?          |


`pip install pettingzoo[mpe]`

Multi Particle Environments (MPE) are a set of communication oriented environment where particle agents can (sometimes) move, communicate, see each other, push each other around, and interact with fixed landmarks.

These environments are from [OpenAI's MPE](https://github.com/openai/multiagent-particle-envs) codebase, with several minor fixes, mostly related to the action space and reward of certain environments.

### Types of Environments

The simple_adversary, simple_crypto, simple_push, simple_tag, simple_world_comm are adversarial- a "good" agent being rewarded means an "adversary" agent is punished and vice versa (though not always in a perfectly zero-sum manner). In most of these environments, there are "good" agents rendered in green and a "adversary" team rendered in red.

The simple_reference, simple_speaker_listener, and simple_spread environments are more cooperative in nature, where the agents all benefit from working with the others, though the rewards for each agent are not identical.

### Key Concepts

* Landmarks: Landmarks are static circular features of the environment that cannot be controlled. In some environments, like simple, they are destinations that affect the rewards of the agents depending on how close the agents are to them. In other environments, they can be obstacles that block the motion of the agents. These are described in more details for each environment.

* Visibility: When an agent is visible to another, the other agent can see its

* Communication: Some agents in some environments can broadcast a message as part of its action (see action space for more details) which will be transmitted to each agent that is allowed to see that message. In simple_crypto, this message is also used to signal that Bob and Eve have reconstructed the message.

* Color: Since all agents are rendered as circles, the agents are only identifiable to a human by their color, so the color of the agents is described in most of the environments. The color is not observed by the agents.

### Observation Space

The observation space of an agent is a vector generally composed of the agent's position and velocity, other agent's relative position and velocity, the landmarks relative positions, the landmark's and agent's types, and communications it received from other agents. The exact form of this is detailed in the environments.

If an agent_1 cannot see or observe the communication of agent_2, then agent_2 is not included in agent_1's observation space, resulting in varying observation space sizes in certain environments.

### Action Space

The action space is a discrete action space representing the combinations of the movements and communications an agent can perform. Agents that can move can choose between the 4 cardinal directions and do nothing. Agents that can communicate choose between 2 and 10 environment dependent options, and the message is broadcast all agents which can hear it.

### Rendering

Rendering works by opening a graphical window of the environment surrounding each agent, with the agent at the center. Note that agents can move outside the scope of that screen, and that the render also method returns the pixel map of the rendered area. <Ben talk about the terminal printing in in render>

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

### Simple

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 1      | No             | (5)             | Discrete(5)             | (4)                      | (-inf,inf)         | ?          |

`pettingzoo.mpe.simple`

`agents= `

*gif*

*AEC diagram*

In this environment, a single agent sees landmark position, and is rewarded based on how close it gets to landmark (Euclidian distance). This is not a multiagent environment, and is primarily intended for debugging purposes.

Observation space: `[self_vel, landmark_offset]`

```
simple.env(max_frames=500)
```

```
max_frames: number of frames (a step for each agent) until game terminates
```

### Simple Adversary

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 3      | No             | (5)             | Discrete(5)             | agent dependent (8),(10) | (-inf,inf)         | ?          |

`pettingzoo.mpe.simple_adversary`

`agents= [adversary_0, agent_0,agent_1]`

*gif*

*AEC diagram*

In this environment, there is 1 adversary (red), N good agents (green), N landmarks (default N=2). All agents observe the position of landmarks and other agents. One landmark is the ‘target landmark’ (colored green). Good agents are rewarded based on how close one of them is to the target landmark, but negatively rewarded based on how close the adversary is to the target landmark. The adversary is rewarded based on distance to the target, but it doesn’t know which landmark is the target landmark. This means good agents have to learn to ‘split up’ and cover all landmarks to deceive the adversary.

Agent Observation space: `[self_pos, self_vel, goal_offset, landmark_offset, other_agent_offsets]`

Adversary observation space: `[landmark_offset, other_agents_offsets]`

```
simple_adversary.env(N=2, max_frames=500)
```

```
N: number of good agents and landmarks

max_frames: number of frames (a step for each agent) until game terminates
```

### Simple Crypto

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 2      | No             | (4)             | Discrete(4)             | agent dependent (4),(8)  | (-inf,inf)         | ?          |

`pettingzoo.mpe import simple_crypto`

`agents= [eve_0, bob_0, alice_0]`

*gif*

*AEC diagram*

In this environment, there are 2 good agents (Alice and Bob) and 1 adversary (Eve). Alice must sent a private 1 bit message to Bob over a public channel. Alice and Bob are rewarded if Bob reconstructs the message, but are negatively rewarded if Eve reconstruct the message. Eve is rewarded based on how well it can reconstruct the signal. Alice and Bob have a private key (randomly generated at beginning of each episode), which they must learn to use to encrypt the message.


Alice Observation space: `[message, private_key]`

Bob Observation space: `[private_key, alices_comm, 1]`

Eve's observation space: `[alices_comm, 1]`

```
simple_crypto.env(max_frames=500)
```

```
max_frames: number of frames (a step for each agent) until game terminates
```


### Simple Push

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 2      | No             | (5)             | Discrete(5)             | agent dependent (8),(19) | (-inf,inf)         | ?          |

`pettingzoo.mpe import simple_push`

`agents= [adversary_0, agent_0]`

*gif*

*AEC diagram*

This environment has 1 good agent, 1 adversary, and 1 landmark. The good agent is rewarded based on the distance to the landmark. The adversary is rewarded if it is close to the landmark, and if the agent is far from the landmark (the difference of the distances). Thus the adversary must learn to push the good agent away from the landmark.

Agent Observation space: `[self_vel, goal_offset, goal_landmark_id, all_landmark_offsets, landmark_ids, other_agent_offsets]`

Adversary Observation space: `[self_vel, all_landmark_offsets, other_agent_offsets]`


```
simple_push.env(max_frames=500)
```

```
max_frames: number of frames (a step for each agent) until game terminates
```


### Simple Reference

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 2      | No             | (50)            | Discrete(50)            | (21)                     | (-inf,inf)         | ?          |

`pettingzoo.mpe import simple_reference`

`agents= [agent_0, agent_1]`

*gif*

*AEC diagram*

This environment has 2 agents and 3 landmarks of different colors. Each agent wants to get closer to their target landmark, which is known only by the other agents. The reward is collective, so agents have to learn to communicate the goal of the other agent, and navigate to their landmark. Both agents are simultaneous speakers and listeners.

Agent Observation space: `[self_vel, all_landmark_offsets, landmark_ids, goal_id, communication]`

```
simple_reference.env(max_frames=500)
```

```
max_frames: number of frames (a step for each agent) until game terminates
```

### Simple Speaker Listener

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 2      | No             | agent dependent (3),(5) | agent dependent  | agent dependent (3),(11) | (-inf,inf)         | ?          |

`pettingzoo.mpe import simple_speaker_listener`

`agents=[speaker_0, listener_0]`

*gif*

*AEC diagram*

This environment is similar to simple_reference, except that one agent is the ‘speaker’ (gray) and can speak but cannot move, while the other agent is the listener (cannot speak, but must navigate to correct landmark).

Speaker: `[goal_id]`

Listener: `[self_vel, all_landmark_offsets, communication]`


```
simple_speaker_listener.env(max_frames=500)
```

```
max_frames: number of frames (a step for each agent) until game terminates
```

### Simple Spread

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 3      | No             | (5)              | Discrete(5)             | (18)                     | (-inf,inf)         | ?          |

`pettingzoo.mpe import simple_spread`

`agents= [agent_0, agent_1, agent_2]`

*gif*

*AEC diagram*

This environment has N agents, N landmarks (default N=3). The agents are rewarded based on how far the closest agent is to each landmark (sum of the minimum distances), but are penalized if they collide with other agents (-1 for each collision). Agents must learn to cover all the landmarks while avoiding collisions.

Agent observations: `[self_vel, self_pos, landmark_offsets, other_agent_offsets, communication]`

```
simple_spread.env(N=3, max_frames=500)
```

```
N: number of agents and landmarks

max_frames: number of frames (a step for each agent) until game terminates
```

### Simple Tag

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 4      | No             | (5)             | Discrete(5)             | agent dependent (14),(16) | (-inf,inf)         | ?          |

`pettingzoo.mpe import simple_tag`

`agents= [adversary_0, adversary_1, adversary_2, agent_0]`

*gif*

*AEC diagram*

This is a predator-prey environment. Good agents (green) are faster and receive a negative reward for being hit by adversaries (red) (-10 for each collision). Adversaries are slower and are rewarded for hitting good agents (+10 for each collision). Obstacles (large black circles) block the way. By default, there is 1 good agent, 3 adversaries and 2 obstacles.

So that good agents don't run to infinity, they are also penalized for exiting the area by the following function:

```
def bound(x):
      if x < 0.9:
          return 0
      if x < 1.0:
          return (x - 0.9) * 10
      return min(np.exp(2 * x - 2), 10)
```

Agent and adversary observations: `[self_vel, self_pos, landmark_offsets, other_agent_offsets, other_agent_velocities]`


```
simple_tag.env(num_good=1, num_adversaries=3, num_obstacles=2 , max_frames=500)
```

```
num_good: number of good agents

num_adversaries: number of adversaries

num_obstacles: number of obstacles

max_frames: number of frames (a step for each agent) until game terminates
```


### Simple World Comm

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 6      | No             | agent dependent (5),(20) | agent dependent | agent dependent (28),(34) | (-inf,inf)         | ?          |

`pettingzoo.mpe import simple_world_comm`

`agents=[lead_adversary_0, adversary_0, adversary_1, adversary_3, agent_0, agent_1]`

*gif*

*AEC diagram*

This environment is similar to simple_tag, except there is food (small blue balls) that the good agents are rewarded for being near, there are 'forests' that hide agents inside from being seen, and there is a ‘leader adversary' that can see the agents at all times and can communicate with the other adversaries to help coordinate the chase. By default, there are 2 good agents, 3 adversaries, 1 obstacles, 2 foods, and 2 forests.

In particular, the good agents reward, is -5 for every collision with an adversary, -2*bound by the `bound` function described in simple_tag, +2 for every collision with a food, and -0.05*minimum distance to any food. The adversarial agents are rewarded +5 for collisions and -0.1*minimum distance to a good agent.


Good agent observations: `[self_vel, self_pos, landmark_offsets, other_agent_offsets, other_agent_velocities, self_in_forest]`

Normal adversary observations:`[self_vel, self_pos, landmark_offsets, other_agent_offsets, other_agent_velocities, self_in_forest, leader_comm]`

Adversary leader observations: `[self_vel, self_pos, landmark_offsets, other_agent_offsets, other_agent_velocities, leader_comm]`

Note that when the forests prevent an agent from being seen, the observation of that agents relative position is set to (0,0).


```
simple_world_comm.env(num_good=2, num_adversaries=4, num_obstacles=1,
                num_food=2, num_forests=2, max_frames=500)
```

```
num_good: number of good agents

num_adversaries: number of adversaries

num_obstacles: number of obstacles

num_food: number of food locations that good agents are rewarded at

num_forests: number of forest locations that hide agents from observation

max_frames: number of frames (a step for each agent) until game terminates
```
