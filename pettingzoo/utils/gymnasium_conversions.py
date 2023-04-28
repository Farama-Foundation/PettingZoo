"""Creates Gymnasium environments from PettingZoo ones.

Wrapping PettingZoo environments into the matching Gymnasium environments for specific agent by providing the action for all other agents.
"""

from typing import Any, Callable, Dict, Optional

import gymnasium
from gymnasium.core import ActType, ObsType

from pettingzoo import AECEnv, ParallelEnv

# The first parameter is an agent (its identification), second parameter is the relevant observation.
# The callable is expected to return the action that the given agent would like to take.
ActOthers = Callable[[str, ObsType], ActType]


class aec_to_gymnasium(gymnasium.Env):
    """Makes a Gymnasium environment out of a AECEnv.

    Wraps a PettingZoo environment (AECEnv) and make a Gymnasium environment out of it (for a single agent).
    In order to make it work, one needs to provide a mechanism to get the actions of all other agents.

    Args:
      aec_env: is the PezttingZoo AECEnv environment to wrap.
      external_agent: is the agent for which the Gymnasium 'step' function is called.
        In other words, this is the agent that would interact with this Gymnasium environment.
      act_other: is a callable that accepts an agent and a
        relevant observation and returns the action that should be taken on behalf of that agent.

    Returns:
      A Gymnasium environment.
    """

    def __init__(self, aec_env: AECEnv, external_agent: str, act_others: ActOthers):
        super().__init__()
        self._aec_env = aec_env
        self._external_agent = external_agent
        self._act_others = act_others
        self.observation_space = self._aec_env.observation_space(external_agent)
        self.action_space = self._aec_env.action_space(external_agent)

    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[dict] = None,
    ):
        super().reset(seed=seed)
        self._aec_env.reset(seed=seed)
        self._loop_others()
        observation, _, _, _, info = self._aec_env.last()
        return observation, info

    def step(self, action):
        agent = self._aec_env.agent_selection
        assert agent == self._external_agent, f"expected it to be my turn, got {agent}"
        self._aec_env.step(action)
        self._loop_others()
        return self._aec_env.last()

    def _loop_others(self):
        for agent in self._aec_env.agent_iter():
            if agent == self._external_agent:
                break
            observation, _, terminated, truncated, _ = self._aec_env.last()
            if terminated or truncated:
                break
            action_current = self._act_others(agent, observation)
            self._aec_env.step(action_current)

    def render(self, *args, **kwargs):
        return self._aec_env.render(*args, **kwargs)

    def close(self):
        return self._aec_env.close()


class parallel_to_gymnasium(gymnasium.Env):
    """Makes a Gymnasium environment out of a ParallelEnv.

    Wraps a PettingZoo environment (ParallelEnv) and make a Gymnasium environment out of it (for a single agent).
    In order to make it work, one needs to provide a mechanism to get the actions of all other agents.

    Args:
      parallel_env: is the PezttingZoo ParallelEnv environment to wrap.
      external_agent: is the agent for which the Gymnasium 'step' function is called.
        In other words, this is the agent that would interact with this Gymnasium environment.
      act_other: is a callable that accepts an agent and a
        relevant observation and returns the action that should be taken on behalf of that agent.

    Returns:
      A Gymnasium environment.
    """

    def __init__(
        self, parallel_env: ParallelEnv, external_agent: str, act_others: ActOthers
    ):
        super().__init__()
        self._parallel_env = parallel_env
        self._external_agent = external_agent
        self._act_others = act_others
        self.observation_space = self._parallel_env.observation_space(external_agent)
        self.action_space = self._parallel_env.action_space(external_agent)
        self._observations: Dict[str, Any]

    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[dict] = None,
    ):
        super().reset(seed=seed)
        self._observations = self._parallel_env.reset(seed=seed)
        return self._observations[self._external_agent], {}

    def step(self, action):
        assert self._observations is not None
        actions = {
            agent: (
                action
                if agent == self._external_agent
                else self._act_others(agent, self._observations[agent])
            )
            for agent in self._parallel_env.agents
        }
        (
            observations,
            rewards,
            terminations,
            truncations,
            infos,
        ) = self._parallel_env.step(actions)
        self._observations = observations
        return (
            self._observations[self._external_agent],
            rewards[self._external_agent],
            terminations[self._external_agent],
            truncations[self._external_agent],
            infos[self._external_agent],
        )

    def render(self, *args, **kwargs):
        return self._parallel_env.render(*args, **kwargs)

    def close(self):
        return self._parallel_env.close()
