## MPE environments

| Environment             | Observations | Actions  | Agents | Manual Control | Action Shape | Action Values    | Observation Shape | Observation Values | Num States |
|-------------------------|--------------|----------|--------|----------------|--------------|------------------|-------------------|--------------------|------------|
| simple                  | Vector       | Discrete | 1      | No             | (5)          | Discrete(5)      | (4)               | (-inf,inf)         | ?          |
| simple_adversary        | Vector       | Discrete | 3      | No             | (5)          | Discrete(5)      | (8),(10)          | (-inf,inf)         | ?          |
| simple_crypto           | Vector       | Discrete | 2      | No             | (4)          | Discrete(4)      | (4),(8)           | (-inf,inf)         | ?          |
| simple_push             | Vector       | Discrete | 2      | No             | (5)          | Discrete(5)      | (8),(19)          | (-inf,inf)         | ?          |
| simple_reference        | Vector       | Discrete | 2      | No             | (50)         | Discrete(50)     | (21)              | (-inf,inf)         | ?          |
| simple_speaker_listener | Vector       | Discrete | 2      | No             | (3),(5)      | Discrete(3),(5)  | (3),(11)          | (-inf,inf)         | ?          |
| simple_spread           | Vector       | Discrete | 3      | No             | (5)          | Discrete(5)      | (18)              | (-inf,inf)         | ?          |
| simple_tag              | Vector       | Discrete | 4      | No             | (5)          | Discrete(5)      | (14),(16)         | (-inf,inf)         | ?          |
| simple_world_comm       | Vector       | Discrete | 6      | No             | (5),(20)     | Discrete(5),(20) | (28),(34)         | (-inf,inf)         | ?          |


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

### Simple

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 1      | No             | (5)             | Discrete(5)             | (4)                      | (-inf,inf)         | ?          |

`pettingzoo.mpe.simple_v0`

`agents= [agent_0]`

*gif*

*AEC diagram*

In this environment, a single agent sees landmark position, and is rewarded based on how close it gets to landmark (Euclidian distance). This is not a multiagent environment, and is primarily intended for debugging purposes.

Observation space: `[self_vel, landmark_rel_position]`

```
simple.env(seed=None, max_frames=100)
```

```
seed: seed for random values. Set to None to use machine random source. Set to fixed value for deterministic behavior

max_frames: number of frames (a step for each agent) until game terminates
```

### Simple Adversary

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 3      | No             | (5)             | Discrete(5)             | (8),(10) | (-inf,inf)         | ?          |

`pettingzoo.mpe.simple_adversary_v0`

`agents= [adversary_0, agent_0,agent_1]`

*gif*

*AEC diagram*

In this environment, there is 1 adversary (red), N good agents (green), N landmarks (default N=2). All agents observe the position of landmarks and other agents. One landmark is the ‘target landmark’ (colored green). Good agents are rewarded based on how close one of them is to the target landmark, but negatively rewarded based on how close the adversary is to the target landmark. The adversary is rewarded based on distance to the target, but it doesn’t know which landmark is the target landmark. This means good agents have to learn to ‘split up’ and cover all landmarks to deceive the adversary.

Agent observation space: `[self_pos, self_vel, goal_rel_position, landmark_rel_position, other_agent_rel_positions]`

Adversary observation space: `[landmark_rel_position, other_agents_rel_positions]`

Agent action space: `[no_action, move_left, move_right, move_down, move_up]`

Adversary action space: `[no_action, move_left, move_right, move_down, move_up]`

```
simple_adversary.env(seed=None, N=2, max_frames=100)
```

```
seed: seed for random values. Set to None to use machine random source. Set to fixed value for deterministic behavior

N: number of good agents and landmarks

max_frames: number of frames (a step for each agent) until game terminates
```

### Simple Crypto

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 2      | No             | (4)             | Discrete(4)             | (4),(8)  | (-inf,inf)         | ?          |

`pettingzoo.mpe import simple_crypto_v0`

`agents= [eve_0, bob_0, alice_0]`

*gif*

*AEC diagram*

In this environment, there are 2 good agents (Alice and Bob) and 1 adversary (Eve). Alice must sent a private 1 bit message to Bob over a public channel. Alice and Bob are rewarded +2 if Bob reconstructs the message, but are rewarded -2 if Eve reconstruct the message (that adds to 0 if both teams recontruct the bit). Eve is rewarded -2 based if it cannot reconstruct the signal, zero if it can. Alice and Bob have a private key (randomly generated at beginning of each episode), which they must learn to use to encrypt the message.


Alice observation space: `[message, private_key]`

Bob observation space: `[private_key, alices_comm]`

Eve observation space: `[alices_comm]`

Alice action space: `[say_0, say_1, say_2, say_3]`

Bob action space: `[say_0, say_1, say_2, say_3]`

Eve action space: `[say_0, say_1, say_2, say_3]`

For Bob and Eve, their communication is checked to be the 1 bit of information that Alice is trying to convey.

```
simple_crypto.env(seed=None, max_frames=100)
```

```
seed: seed for random values. Set to None to use machine random source. Set to fixed value for deterministic behavior

max_frames: number of frames (a step for each agent) until game terminates
```


### Simple Push

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 2      | No             | (5)             | Discrete(5)             | (8),(19) | (-inf,inf)         | ?          |

`pettingzoo.mpe import simple_push_v0`

`agents= [adversary_0, agent_0]`

*gif*

*AEC diagram*

This environment has 1 good agent, 1 adversary, and 1 landmark. The good agent is rewarded based on the distance to the landmark. The adversary is rewarded if it is close to the landmark, and if the agent is far from the landmark (the difference of the distances). Thus the adversary must learn to push the good agent away from the landmark.

Agent observation space: `[self_vel, goal_rel_position, goal_landmark_id, all_landmark_rel_positions, landmark_ids, other_agent_rel_positions]`

Adversary observation space: `[self_vel, all_landmark_rel_positions, other_agent_rel_positions]`

Agent action space: `[no_action, move_left, move_right, move_down, move_up]`

Adversary action space: `[no_action, move_left, move_right, move_down, move_up]`

```
simple_push.env(seed=None, max_frames=100)
```

```
seed: seed for random values. Set to None to use machine random source. Set to fixed value for deterministic behavior

max_frames: number of frames (a step for each agent) until game terminates
```


### Simple Reference

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 2      | No             | (50)            | Discrete(50)            | (21)                     | (-inf,inf)         | ?          |

`pettingzoo.mpe import simple_reference_v0`

`agents= [agent_0, agent_1]`

*gif*

*AEC diagram*

This environment has 2 agents and 3 landmarks of different colors. Each agent wants to get closer to their target landmark, which is known only by the other agents. Both agents are simultaneous speakers and listeners.

Locally, the agents are rewarded by their distance to their target landmark. Globally, all agents are rewarded by the average distance of all the agents to their respective landmarks. The relative weight of these rewards is controlled by the `local_ratio` parameter.

Agent observation space: `[self_vel, all_landmark_rel_positions, landmark_ids, goal_id, communication]`

Agent action space: `[say_0, say_1, say_2, say_3, say_4, say_5, say_6, say_7, say_8, say_9] X [no_action, move_left, move_right, move_down, move_up]`

Where X is the Cartesian product (giving a total action space of 50).


```
simple_reference.env(seed=None, local_ratio=0.5, max_frames=100)
```

```
seed: seed for random values. Set to None to use machine random source. Set to fixed value for deterministic behavior

local_ratio: Weight applied to local reward and global reward. Global reward weight will always be 1 - local reward weight.

max_frames: number of frames (a step for each agent) until game terminates
```

### Simple Speaker Listener

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 2      | No             | (3),(5) | Discrete(3),(5)  | (3),(11) | (-inf,inf)         | ?          |

`pettingzoo.mpe import simple_speaker_listener_v0`

`agents=[speaker_0, listener_0]`

*gif*

*AEC diagram*

This environment is similar to simple_reference, except that one agent is the ‘speaker’ (gray) and can speak but cannot move, while the other agent is the listener (cannot speak, but must navigate to correct landmark).

Speaker observation space: `[goal_id]`

Listener observation space: `[self_vel, all_landmark_rel_positions, communication]`

Speaker action space: `[say_0, say_1, say_2, say_3, say_4, say_5, say_6, say_7, say_8, say_9]`

Listener action space: `[no_action, move_left, move_right, move_down, move_up]`

```
simple_speaker_listener.env(seed=None, max_frames=100)
```

```
seed: seed for random values. Set to None to use machine random source. Set to fixed value for deterministic behavior

max_frames: number of frames (a step for each agent) until game terminates
```

### Simple Spread

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 3      | No             | (5)              | Discrete(5)             | (18)                     | (-inf,inf)         | ?          |

`pettingzoo.mpe import simple_spread_v0`

`agents= [agent_0, agent_1, agent_2]`

*gif*

*AEC diagram*

This environment has N agents, N landmarks (default N=3). At a high level, agents must learn to cover all the landmarks while avoiding collisions.

More specifically, all agents are globally rewarded based on how far the closest agent is to each landmark (sum of the minimum distances). Locally, the agents are penalized if they collide with other agents (-1 for each collision). The relative weights of these rewards can be controlled with the `local_ratio` parameter.

Agent observations: `[self_vel, self_pos, landmark_rel_positions, other_agent_rel_positions, communication]`

Agent action space: `[no_action, move_left, move_right, move_down, move_up]`

```
simple_spread.env(seed=None, N=3, local_ratio=0.5, max_frames=100)
```

```
seed: seed for random values. Set to None to use machine random source. Set to fixed value for deterministic behavior

N: number of agents and landmarks

local_ratio: Weight applied to local reward and global reward. Global reward weight will always be 1 - local reward weight.

max_frames: number of frames (a step for each agent) until game terminates
```

### Simple Tag

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 4      | No             | (5)             | Discrete(5)             | (14),(16) | (-inf,inf)         | ?          |

`pettingzoo.mpe import simple_tag_v0`

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

Agent and adversary observations: `[self_vel, self_pos, landmark_rel_positions, other_agent_rel_positions, other_agent_velocities]`

Agent and adversary action space: `[no_action, move_left, move_right, move_down, move_up]`

```
simple_tag.env(seed=None, num_good=1, num_adversaries=3, num_obstacles=2 , max_frames=100)
```

```
seed: seed for random values. Set to None to use machine random source. Set to fixed value for deterministic behavior

num_good: number of good agents

num_adversaries: number of adversaries

num_obstacles: number of obstacles

max_frames: number of frames (a step for each agent) until game terminates
```


### Simple World Comm

| Observations | Actions  | Agents | Manual Control | Action Shape    | Action Values           | Observation Shape        | Observation Values | Num States |
|--------------|----------|--------|----------------|-----------------|-------------------------|--------------------------|--------------------|------------|
| Vector       | Discrete | 6      | No             | (5),(20) | Discrete(5),(20) | (28),(34) | (-inf,inf)         | ?          |

`pettingzoo.mpe import simple_world_comm_v0`

`agents=[leadadversary_0, adversary_0, adversary_1, adversary_3, agent_0, agent_1]`

*gif*

*AEC diagram*

This environment is similar to simple_tag, except there is food (small blue balls) that the good agents are rewarded for being near, there are 'forests' that hide agents inside from being seen, and there is a ‘leader adversary' that can see the agents at all times and can communicate with the other adversaries to help coordinate the chase. By default, there are 2 good agents, 3 adversaries, 1 obstacles, 2 foods, and 2 forests.

In particular, the good agents reward, is -5 for every collision with an adversary, -2 x bound by the `bound` function described in simple_tag, +2 for every collision with a food, and -0.05 x minimum distance to any food. The adversarial agents are rewarded +5 for collisions and -0.1 x minimum distance to a good agent. s

Good agent observations: `[self_vel, self_pos, landmark_rel_positions, other_agent_rel_positions, other_agent_velocities, self_in_forest]`

Normal adversary observations:`[self_vel, self_pos, landmark_rel_positions, other_agent_rel_positions, other_agent_velocities, self_in_forest, leader_comm]`

Adversary leader observations: `[self_vel, self_pos, landmark_rel_positions, other_agent_rel_positions, other_agent_velocities, leader_comm]`

*Note that when the forests prevent an agent from being seen, the observation of that agents relative position is set to (0,0).*

Good agent action space: `[no_action, move_left, move_right, move_down, move_up]`

Normal adversary action space: `[no_action, move_left, move_right, move_down, move_up]`

Adversary leader observation space: `[say_0, say_1, say_2, say_3] X [no_action, move_left, move_right, move_down, move_up]`

Where X is the Cartesian product (giving a total action space of 50).


```
simple_world_comm.env(seed=None, num_good=2, num_adversaries=4, num_obstacles=1,
                num_food=2, num_forests=2, max_frames=100)
```

```
seed: seed for random values. Set to None to use machine random source. Set to fixed value for deterministic behavior

num_good: number of good agents

num_adversaries: number of adversaries

num_obstacles: number of obstacles

num_food: number of food locations that good agents are rewarded at

num_forests: number of forest locations that hide agents from observation

max_frames: number of frames (a step for each agent) until game terminates
```
