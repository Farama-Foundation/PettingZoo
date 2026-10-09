---
title: Parallel
---


# Parallel API

In addition to the main API, we have a secondary parallel API for environments where all agents have simultaneous actions and observations. An environment with parallel API support can be created via `make("parallel", <game>, ...)`. This API is based around the paradigm of *Partially Observable Stochastic Games* (POSGs) and the details are similar to [RLlib's MultiAgent environment specification](https://docs.ray.io/en/latest/rllib-env.html#multi-agent-and-hierarchical), except we allow for different observation and action spaces between the agents.

For a comparison with the AEC API, see [About AEC](https://pettingzoo.farama.org/api/aec/#about-aec). For more information, see [*PettingZoo: A Standard API for Multi-Agent Reinforcement Learning*](https://arxiv.org/pdf/2009.14471.pdf).

[PettingZoo Wrappers](/api/wrappers/pz_wrappers/) can be used to convert between Parallel and AEC environments, with some restrictions (e.g., an AEC env must only update once at the end of each cycle).

## Examples

[PettingZoo Butterfly](/environments/butterfly/) provides standard examples of Parallel environments, such as [Pistonball](/environments/butterfly/pistonball).

We provide tutorials for creating two custom Parallel environments: [Rock-Paper-Scissors (Parallel)](https://pettingzoo.farama.org/content/environment_creation/#example-custom-parallel-environment), and a simple [gridworld environment](/tutorials/custom_environment/2-environment-logic/)

## Usage

Parallel environments can be interacted with as follows:

```python
from pettingzoo import make

parallel_env = make("parallel", "butterfly/pistonball-v6", render_mode="human")
observations, infos = parallel_env.reset(seed=42)

while parallel_env.agents:
    actions = {}
    for agent in parallel_env.agents:
        agent_observation = observations[agent]
        action_mask = infos[agent].get("action_mask")
        if isinstance(agent_observation, dict) and "action_mask" in agent_observation:
            # When both locations provide a mask, the observation mask takes precedence.
            action_mask = agent_observation["action_mask"]

        action_space = parallel_env.action_space(agent)
        if action_mask is None:
            actions[agent] = action_space.sample()
        else:
            actions[agent] = action_space.sample(mask=action_mask)

    observations, rewards, terminations, truncations, infos = parallel_env.step(actions)
parallel_env.close()
```

Parallel environments can provide an action mask in `infos[agent]["action_mask"]` or, when the
observation is a dictionary, in `observations[agent]["action_mask"]`. If both are present, the
dictionary observation takes precedence. The [custom action-masking tutorial](/tutorials/custom_environment/3-action-masking/)
shows a working environment that supplies masks in dictionary observations.

## ParallelEnv

```{eval-rst}
.. currentmodule:: pettingzoo.utils.env

.. autoclass:: ParallelEnv

    .. py:attribute:: agents

        A list of the names of all current agents, typically integers. These may be changed as an environment progresses (i.e. agents can be added or removed).

        :type: list[AgentID]

    .. py:attribute:: num_agents

        The length of the agents list.

        :type: int

    .. py:attribute:: possible_agents

        A list of all possible_agents the environment could generate. Equivalent to the list of agents in the observation and action spaces. This cannot be changed through play or resetting.

        :type: list[AgentID]

    .. py:attribute:: max_num_agents

        The length of the possible_agents list.

        :type: int

    .. py:attribute:: observation_spaces

        A dict of the observation spaces of every agent, keyed by name. This cannot be changed through play or resetting.

        :type: Dict[AgentID, gym.spaces.Space]

    .. py:attribute:: action_spaces

        A dict of the action spaces of every agent, keyed by name. This cannot be changed through play or resetting.

        :type: Dict[AgentID, gym.spaces.Space]

    .. automethod:: step
    .. automethod:: reset
    .. automethod:: render
    .. automethod:: close
    .. automethod:: state
    .. automethod:: observation_space
    .. automethod:: action_space

```
