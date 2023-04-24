from typing import Callable, Optional
import gymnasium
from gymnasium.core import ActType, ObsType
from pettingzoo import AECEnv


# The first parameter is an agent (its identification), second parameter is the relevant observation.
# The callable is expected to return the action that the given agent would like to take.
ActOthers = Callable[[str, ObsType], ActType]


class Aec2GymnasiumEnv(gymnasium.Env):
  """
  This class wraps a PettingZoo environment (AECEnv) and exposes a simple Gymnasium environment
  (for single agent).
  In order to make it work, one needs to provide in the initialization a mechanism to get the actions
  of all other agents.

  Note that this class is actually a Gymnasium environment.
  It is not a PettingZoo wrapper and is neither a Gymnasium one.
  """

  def __init__(
    self,
    aec_env: AECEnv,
    external_agent: str,
    act_others: ActOthers
  ):
    """

    Args:
      aec_env: is the PezttingZoo AECEnv environment to wrap.

      external_agent: is the agent for which the Gymnasium 'step' function is called.
      In other words, this is the agent that would interact with this Gymnasium environment.

      act_other: is a callable that accepts an agent and a
      relevant observation and returns the action that should be taken on behalf of that agent.
    """

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
    self._aec_env.render(*args, **kwargs)
