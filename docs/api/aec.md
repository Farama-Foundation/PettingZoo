# AEC API

```{eval-rst}
.. currentmodule:: pettingzoo.utils.env

.. autoclass:: AECEnv

```

## Attributes


```{eval-rst}

.. autoattribute:: AECEnv.agents

    A list of the names of all current agents, typically integers. These may be changed as an environment progresses (i.e. agents can be added or removed).

    :type: List[AgentID]

.. autoattribute:: AECEnv.num_agents

    The length of the agents list.

.. autoattribute:: AECEnv.possible_agents

    A list of all possible_agents the environment could generate. Equivalent to the list of agents in the observation and action spaces. This cannot be changed through play or resetting.

    :type: List[AgentID]

.. autoattribute:: AECEnv.max_num_agents

    The length of the possible_agents list.

.. autoattribute:: AECEnv.agent_selection

    An attribute of the environment corresponding to the currently selected agent that an action can be taken for.

    :type: AgentID

.. autoattribute:: AECEnv.terminations

.. autoattribute:: AECEnv.truncations

.. autoattribute:: AECEnv.rewards

    A dict of the rewards of every current agent at the time called, keyed by name. Rewards the instantaneous reward generated after the last step. Note that agents can be added or removed from this attribute. `last()` does not directly access this attribute, rather the returned reward is stored in an internal variable. The rewards structure looks like::

    {0:[first agent reward], 1:[second agent reward] ... n-1:[nth agent reward]}

    :type: Dict[AgentID, float]

.. autoattribute:: AECEnv.infos

    A dict of info for each current agent, keyed by name. Each agent's info is also a dict. Note that agents can be added or removed from this attribute. `last()` accesses this attribute. The returned dict looks like::

        infos = {0:[first agent info], 1:[second agent info] ... n-1:[nth agent info]}

    :type: Dict[AgentID, Dict[str, Any]]

.. autoattribute:: AECEnv.observation_spaces

    A dict of the observation spaces of every agent, keyed by name. This cannot be changed through play or resetting.

    :type: Dict[AgentID, gymnasium.spaces.Space]

.. autoattribute:: AECEnv.action_spaces

    A dict of the action spaces of every agent, keyed by name. This cannot be changed through play or resetting.

    :type: Dict[AgentID, gymnasium.spaces.Space]
```

## Methods

```{eval-rst}
.. automethod:: AECEnv.step
.. automethod:: AECEnv.reset
.. automethod:: AECEnv.observe
.. automethod:: AECEnv.render
.. automethod:: AECEnv.seed
.. automethod:: AECEnv.close

```

