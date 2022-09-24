# Core API

```{eval-rst}
.. currentmodule:: pettingzoo.utils.env

.. autoclass:: AECEnv

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

    .. py:attribute:: agent_selection

        An attribute of the environment corresponding to the currently selected agent that an action can be taken for.

        :type: AgentID

    .. py:attribute:: dones

        A dict of the done state of every current agent at the time called, keyed by name. `last()` accesses this attribute. Note that agents can be added or removed from this dict. The returned dict looks like::

        dones = {0:[first agent done state], 1:[second agent done state] ... n-1:[nth agent done state]}

        :type: Dict[AgentID, bool]

    .. py:attribute:: rewards

        A dict of the rewards of every current agent at the time called, keyed by name. Rewards the instantaneous reward generated after the last step. Note that agents can be added or removed from this attribute. `last()` does not directly access this attribute, rather the returned reward is stored in an internal variable. The rewards structure looks like::

        {0:[first agent reward], 1:[second agent reward] ... n-1:[nth agent reward]}

        :type: Dict[AgentID, float]

    .. py:attribute:: infos

        A dict of info for each current agent, keyed by name. Each agent's info is also a dict. Note that agents can be added or removed from this attribute. `last()` accesses this attribute. The returned dict looks like::

        infos = {0:[first agent info], 1:[second agent info] ... n-1:[nth agent info]}

        :type: Dict[AgentID, Dict[str, Any]]

    .. py:attribute:: observation_spaces

        A dict of the observation spaces of every agent, keyed by name. This cannot be changed through play or resetting.

        :type: Dict[AgentID, gym.spaces.Space]

    .. py:attribute:: action_spaces

        A dict of the action spaces of every agent, keyed by name. This cannot be changed through play or resetting.

        :type: Dict[AgentID, gym.spaces.Space]

    .. automethod:: step
    .. automethod:: reset
    .. automethod:: observe
    .. automethod:: render
    .. automethod:: seed
    .. automethod:: close


```

