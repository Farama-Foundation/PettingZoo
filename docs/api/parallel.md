# Parallel API

In addition to the main API, we have a secondary parallel API for environments where all agents have simultaneous actions and observations. An environment with parallel API support can be created via `<game>.parallel_env()`. This API is based around the paradigm of *Partially Observable Stochastic Games* (POSGs) and the details are similar to [RLLib's MultiAgent environment specification](https://docs.ray.io/en/latest/rllib-env.html#multi-agent-and-hierarchical), except we allow for different observation and action spaces between the agents.

### Example Usage

Environments can be interacted with as follows:

``` python
parallel_env = pistonball_v1.parallel_env()
observations = parallel_env.reset()
max_cycles = 500
for step in range(max_cycles):
    actions = {agent: policy(observations[agent], agent) for agent in parallel_env.agents}
    observations, rewards, terminations, truncations, infos = parallel_env.step(actions)
```

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
    .. automethod:: seed
    .. automethod:: render
    .. automethod:: close
    .. automethod:: state
    .. automethod:: observation_space
    .. automethod:: action_space

```