from typing import Callable, Optional
import gymnasium
from gymnasium.core import ActType, ObsType
from pettingzoo import AECEnv


# The first parameter is an agent (it's identification), second parameter is the relevant observation.
# The callable is expected to return the action that the given agent would like to take.
ActOthers = Callable[[str, ObsType], ActType]


class PZ2GymnasiumWrapper(gymnasium.Env):
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
    pz_env: AECEnv,
    the_external_agent: str,
    act_others: ActOthers
  ):
    """
    'pz_env' is the PezttingZoo environment to wrap.

    'the_external_agent' is the agent for which the Gymnasium 'step' function is called.
    In other words, this is the agent that would interact with this Gymnasium environment.

    'act_other' is a callable that accepts an agent and a
    relevant observation and returns the action that should be taken on behalf of that agent.
    """

    super().__init__()
    self._pz_env = pz_env
    self._the_external_agent = the_external_agent
    self._act_others = act_others
    self.observation_space = self._pz_env.observation_space(the_external_agent)
    self.action_space = self._pz_env.action_space(the_external_agent)

  def reset(
    self,
    seed: Optional[int] = None,
    options: Optional[dict] = None,
  ):
    super().reset(seed=seed)
    self._pz_env.reset(seed=seed)
    self._loop_others()
    observation, _, _, _, info = self._pz_env.last()
    return observation, info

  def step(self, action):
    agent = self._pz_env.agent_selection
    assert agent == self._the_external_agent, f"expected it to be my turn, got {agent}"
    self._pz_env.step(action)
    self._loop_others()
    return self._pz_env.last()

  def _loop_others(self):
    agent = self._pz_env.agent_selection
    while agent != self._the_external_agent:
      obs_current = self._pz_env.observe(agent)
      action_current = self._act_others(agent, obs_current)
      self._pz_env.step(action_current)
      agent = self._pz_env.agent_selection

  def render(self, *args, **kwargs):
    self._pz_env.render(*args, **kwargs)
