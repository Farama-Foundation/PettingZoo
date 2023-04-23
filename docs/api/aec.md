# AEC API

By default, PettingZoo models games as [*Agent Environment Cycle*](https://arxiv.org/abs/2009.13051) (AEC) environments. This allows it to support any type of game multi-agent RL can consider.

## Usage

AEC environments can be interacted with as follows:

```python
from pettingzoo.classic import rps_v2

env = rps_v2.env(render_mode="human")
env.reset(seed=42)

for agent in env.agent_iter():
    observation, reward, termination, truncation, info = env.last()
    
    if termination or truncation:
        break
        
    action = env.action_space(agent).sample() # this is where you would insert your policy
    
    env.step(action) # execute the action in the environment
env.close()
```

### Action Masking
AEC environments often include action masks, in order to mark valid & invalid actions for the agent. 

[//]: # (For details about action masking, see [A Closer Look at Invalid Action Masking in Policy Gradient Algorithms]&#40;https://arxiv.org/abs/2006.14171&#41; &#40;Huang, 2022&#41;.)

To sample actions using invalid action masking: 
```python
from pettingzoo.classic import chess_v5

env = chess_v5.env(render_mode="human")
env.reset(seed=42)

for agent in env.agent_iter():
    observation, reward, termination, truncation, info = env.last()

    if termination or truncation:
        break
        
    # invalid action masking is optional and environment-dependent
    if "action_mask" in info:
        mask = info["action_mask"] # used in Shimmy OpenSpiel compatibility wrapper
    elif isinstance(observation, dict) and "action_mask" in observation:
        mask = observation["action_mask"] # used in PettingZoo Classic environments
    else:
        mask = None 
        
    action = env.action_space(agent).sample(mask) # this is where you would insert your policy

    env.step(action) # execute the action in the environment
env.close()
```

Note: invalid action masking is optional, and can be stored either in `observation` or `info`. For example:
* [PettingZoo Classic](https://pettingzoo.farama.org/environments/classic/) environments store illegal action mask in the `observation` dict:
  * `mask = observation["action_mask"]`
* [Shimmy](https://shimmy.farama.org/)'s [OpenSpiel environments](https://shimmy.farama.org/environments/open_spiel/) stores illegal action mask in the `info` dict:
  * `mask = info["action_mask"` 

To implement action masking in a custom environment, see [Environment Creation: Action Masking](https://pettingzoo.farama.org/tutorials/environmentcreation/3-action-masking/)

For more information on action masking, see [A Closer Look at Invalid Action Masking in Policy Gradient Algorithms](https://arxiv.org/abs/2006.14171) (Huang, 2022)


## AECEnv

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

