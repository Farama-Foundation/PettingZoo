import warnings

'''
Base environment definitions

See docs/api.md for api documentation
See docs/dev_docs.md for additional documentation and an example environment.
'''


class AECEnv:
    '''
    The AECEnv steps agents one at a time. If you are unsure if you
    have implemented a AECEnv correctly, try running the `api_test` documented in
    the Developer documentation on the website.
    '''
    def __init__(self):
        pass

    def step(self, action):
        '''
        Receives a dictionary of actions keyed by the agent name.
        Returns the observation dictionary, reward dictionary, done dictionary, and info dictionary,
        where each dictionary is keyed by the agent.
        '''
        raise NotImplementedError

    def reset(self):
        '''
        Resets the environment to a starting state.
        '''
        raise NotImplementedError

    def seed(self, seed=None):
        '''
        Reseeds the environment (making the resulting environment deterministic).
        `reset()` must be called after `seed()`, and before `step()`.
        '''
        pass

    def observe(self, agent):
        '''
        Returns the observation an agent currently can make. `last()` calls this function.
        '''
        raise NotImplementedError

    def render(self, mode='human'):
        '''
        Displays a rendered frame from the environment, if supported.
        Alternate render modes in the default environments are `'rgb_array'`
        which returns a numpy array and is supported by all environments outside of classic,
        and `'ansi'` which returns the strings printed (specific to classic environments).
        '''
        raise NotImplementedError

    def state(self):
        '''
        State returns a global view of the environment appropriate for
        centralized training decentralized execution methods like QMIX
        '''
        raise NotImplementedError('state() method has not been implemented in the environment {}.'.format(self.metadata.get('name', self.__class__.__name__)))

    def close(self):
        '''
        Closes the rendering window, subprocesses, network connections, or any other resources
        that should be released.
        '''
        pass

    def observation_space(self, agent):
        '''
        Takes in agent and returns the observation space for that agent.

        MUST return the same value for the same agent name

        Default implementation is to return the observation_spaces dict
        '''
        warnings.warn("Your environment should override the observation_space function. Attempting to use the observation_spaces dict attribute.")
        return self.observation_spaces[agent]

    def action_space(self, agent):
        '''
        Takes in agent and returns the action space for that agent.

        MUST return the same value for the same agent name

        Default implementation is to return the action_spaces dict
        '''
        warnings.warn("Your environment should override the action_space function. Attempting to use the action_spaces dict attribute.")
        return self.action_spaces[agent]

    @property
    def num_agents(self):
        return len(self.agents)

    @property
    def max_num_agents(self):
        return len(self.possible_agents)

    def _dones_step_first(self):
        '''
        Makes .agent_selection point to first done agent. Stores old value of agent_selection
        so that _was_done_step can restore the variable after the done agent steps.
        '''
        _dones_order = [agent for agent in self.agents if self.dones[agent]]
        if _dones_order:
            self._skip_agent_selection = self.agent_selection
            self.agent_selection = _dones_order[0]
        return self.agent_selection

    def _clear_rewards(self):
        '''
        clears all items in .rewards
        '''
        for agent in self.rewards:
            self.rewards[agent] = 0

    def _accumulate_rewards(self):
        '''
        adds .rewards dictionary to ._cumulative_rewards dictionary. Typically
        called near the end of a step() method
        '''
        for agent, reward in self.rewards.items():
            self._cumulative_rewards[agent] += reward

    def agent_iter(self, max_iter=2**63):
        '''
        yields the current agent (self.agent_selection) when used in a loop where you step() each iteration.
        '''
        return AECIterable(self, max_iter)

    def last(self, observe=True):
        '''
        returns observation, cumulative reward, done, info   for the current agent (specified by self.agent_selection)
        '''
        agent = self.agent_selection
        observation = self.observe(agent) if observe else None
        return observation, self._cumulative_rewards[agent], self.dones[agent], self.infos[agent]

    def _was_done_step(self, action):
        '''
        Helper function that performs step() for done agents.

        Does the following:

        1. Removes done agent from .agents, .dones, .rewards, ._cumulative_rewards, and .infos
        2. Loads next agent into .agent_selection: if another agent is done, loads that one, otherwise load next live agent
        3. Clear the rewards dict

        Highly recommended to use at the beginning of step as follows:

        def step(self, action):
            if self.dones[self.agent_selection]:
                self._was_done_step()
                return
            # main contents of step
        '''
        if action is not None:
            raise ValueError("when an agent is done, the only valid action is None")

        # removes done agent
        agent = self.agent_selection
        assert self.dones[agent], "an agent that was not done as attempted to be removed"
        del self.dones[agent]
        del self.rewards[agent]
        del self._cumulative_rewards[agent]
        del self.infos[agent]
        self.agents.remove(agent)

        # finds next done agent or loads next live agent (Stored in _skip_agent_selection)
        _dones_order = [agent for agent in self.agents if self.dones[agent]]
        if _dones_order:
            if getattr(self, '_skip_agent_selection', None) is None:
                self._skip_agent_selection = self.agent_selection
            self.agent_selection = _dones_order[0]
        else:
            if getattr(self, '_skip_agent_selection', None) is not None:
                self.agent_selection = self._skip_agent_selection
            self._skip_agent_selection = None
        self._clear_rewards()

    def __str__(self):
        '''
        returns a name which looks like: "space_invaders_v1"
        '''
        if hasattr(self, 'metadata'):
            return self.metadata.get('name', self.__class__.__name__)
        else:
            return self.__class__.__name__

    @property
    def unwrapped(self):
        return self


class AECIterable:
    def __init__(self, env, max_iter):
        self.env = env
        self.max_iter = max_iter

    def __iter__(self):
        return AECIterator(self.env, self.max_iter)


class AECIterator:
    def __init__(self, env, max_iter):
        self.env = env
        self.iters_til_term = max_iter

    def __next__(self):
        if not self.env.agents or self.iters_til_term <= 0:
            raise StopIteration
        self.iters_til_term -= 1
        return self.env.agent_selection


class ParallelEnv:
    '''
    The Parallel environment steps every live agent at once. If you are unsure if you
    have implemented a ParallelEnv correctly, try running the `parallel_api_test` in
    the Developer documentation on the website.
    '''
    def reset(self):
        '''
        resets the environment and returns a dictionary of observations (keyed by the agent name)
        '''
        raise NotImplementedError

    def seed(self, seed=None):
        '''
         Reseeds the environment (making it deterministic).
         `reset()` must be called after `seed()`, and before `step()`.
        '''
        pass

    def step(self, actions):
        '''
        receives a dictionary of actions keyed by the agent name.
        Returns the observation dictionary, reward dictionary, done dictionary,
        and info dictionary, where each dictionary is keyed by the agent.
        '''
        raise NotImplementedError

    def render(self, mode="human"):
        '''
        Displays a rendered frame from the environment, if supported.
        Alternate render modes in the default environments are `'rgb_array'`
        which returns a numpy array and is supported by all environments outside
        of classic, and `'ansi'` which returns the strings printed
        (specific to classic environments).
        '''
        raise NotImplementedError

    def close(self):
        '''
        Closes the rendering window.
        '''
        pass

    def state(self):
        '''
        State returns a global view of the environment appropriate for
        centralized training decentralized execution methods like QMIX
        '''
        raise NotImplementedError('state() method has not been implemented in the environment {}.'.format(self.metadata.get('name', self.__class__.__name__)))

    def observation_space(self, agent):
        '''
        Takes in agent and returns the observation space for that agent.

        MUST return the same value for the same agent name

        Default implementation is to return the observation_spaces dict
        '''
        warnings.warn("Your environment should override the observation_space function. Attempting to use the observation_spaces dict attribute.")
        return self.observation_spaces[agent]

    def action_space(self, agent):
        '''
        Takes in agent and returns the action space for that agent.

        MUST return the same value for the same agent name

        Default implementation is to return the action_spaces dict
        '''
        warnings.warn("Your environment should override the action_space function. Attempting to use the action_spaces dict attribute.")
        return self.action_spaces[agent]

    @property
    def num_agents(self):
        return len(self.agents)

    @property
    def max_num_agents(self):
        return len(self.possible_agents)

    def __str__(self):
        '''
        returns a name which looks like: "space_invaders_v1" by default
        '''
        if hasattr(self, 'metadata'):
            return self.metadata.get('name', self.__class__.__name__)
        else:
            return self.__class__.__name__

    @property
    def unwrapped(self):
        return self
