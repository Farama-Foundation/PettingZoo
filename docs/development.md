## Creating Custom Environments
Creating a custom environment with PettingZoo should roughly look like the following:

```
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
from gym import spaces


class env(AECEnv):
    metadata = {'render.modes': ['human']} # only add if environment supports rendering

    def __init__(self, arg1, arg2, ...):
        super(env, self).__init__()

        self.agents = [0, 1 ... n] # agent names
        self.agent_order = # list of agent names in the order they act in a cycle. Usually this will be the same as the agents list.
        self.observation_spaces = # dict of observation spaces for each agent, from gym.spaces
        self.action_spaces = # dict of action spaces for each agent, from gym.spaces
        self.rewards = {0:[first agent's reward], 1:[second agent's reward] ... n-1:[nth agent's reward]}
        self.dones = {0:[first agent's done state], 1:[second agent's done state] ... n-1:[nth agent's done state]}
        self.infos = {0:[first agent's info], 1:[second agent's info] ... n-1:[nth agent's info]}

        # agent selection stuff
        self._agent_selector = agent_selector(self.agent_order)

        # Initialize game stuff

    def observe(self, agent):
        # return observation of an agent
        return observation

    def step(self, action, observe=True):
        # Do game stuff on the selected agent

        # Switch selection to next agents
        self.agent_selection = self._agent_selector.next()

        if observe:
            return self.observe(self.agent_selection)
        else:
            return

    # last is added as a part of the AECEnv class, don't write it yourself

    def reset(self, observe=True):
        # reset environment

        # selects the first agent
        self._agent_selector.reinit(self.agent_order)
        self.agent_selection = self._agent_selector.next()
        if observe:
            return self.observe(self.agent_selection)
        else:
            return

    def render(self, mode='human'): # not all environments will support rendering
        ...

    def close(self):
        ...
```

## Agent selector 

File location: `PettingZoo/pettingzoo/utils/agent_selector.py`

*Description:* Use an agent selector object (along with the agent_order list in your environment) to cycle through the agents so that the next agent can be selected at each step, using `next()` method.

### Methods

`reset()`: Resets the agent selector object. It uses the `agent_order` list that is already present in the object. Returns the first agent id of the order as the selected agent.

`reinit(agent_order)`: If the agent order changes (for example, if a 'Reverse' card is played in Uno), reinitialize the agent selector object with the new `agent_order`. Does not return anything.

`next()`: Returns the id (say, _x_) of the next agent in the `agent_order`. Auto-increments the internal agent counter so that next time `next()` is called, id of the agent next to _x_ in the order is returned.

`is_last()`: Checks if the previous agent that was returned in the last agent in the `agent_order`. Returns True if yes, False otherwise. Note this method serves little purpose if the `agent_order` might change in the game.

### Usage in game environments

Import this class into your environment as `from pettingzoo.utils import agent_selector` at the top of the module.

Define an agent selector object in the env as `self._agent_selector = self.agent_selector(self.agent_order)`.

In `reset()` method of your env, do `self.agent_selection = self._agent_selector.reset()`.

If you want to select the next agent, do `self.agent_selection = self._agent_selector.next()`.

If the agent order ever changes, reinitialize the object as `self._agent_selector.reinit(self.agent_order)`.

Finally, for a static agent order, you can check if the previous agent id that was output by the selector is the last agent in the order, by performing a truth value check on `self._agent_selector.is_last()`.
