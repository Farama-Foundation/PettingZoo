from typing import Callable, Dict, Optional, Protocol, TypeVar, Union
import gymnasium
from pettingzoo import AECEnv


Action = TypeVar("Action")
Observation = TypeVar("Observation")

ActOther = Callable[[Observation], Action]


class PZ2GymnasiumWrapper(gymnasium.Env):
  """
  This class wraps a PettingZoo environment (AECEnv) and exposes a simple Gymnasium environment
  (for single agent).
  In order to make it work, one needs to provide in the initialization a mechanism to get the actions
  of all other agents.

  Note that this class is actually a Gymnasium environment.
  It is not a PettingZoo wrapper and is neigher a Gymnasium one.
  """

  def __init__(
    self,
    pz_env: AECEnv,
    act_others: Dict[str, ActOther],
    take_spaces_from: Union[str, None]
  ):
    super().__init__()
    self._pz_env = pz_env
    self._act_others = act_others
    take_spaces_from = (
      take_spaces_from
      or next(iter(act_others)) # just use any of the keys in the _act_others dict.
    )
    self.observation_space = self._pz_env.observation_space(take_spaces_from)
    self.action_space = self._pz_env.action_space(take_spaces_from)

  def reset(
    self,
    seed: Optional[int] = None,
    options: Optional[dict] = None,
  ):
    super().reset(seed=seed)
    self._pz_env.reset(seed=seed)
    self._loop_others()
    agent = self._pz_env.agent_selection
    observation, info = (
      self._pz_env.observe(agent),
      self._pz_env.infos[agent]
    )
    return observation, info

  def step(self, action):
    agent = self._pz_env.agent_selection
    assert agent not in self._act_others, f"expected it to be my turn, got {agent}"
    self._pz_env.step(action)
    self._loop_others()
    observation, reward, terminated, truncated, info = (
      self._pz_env.observe(agent),
      self._pz_env.rewards[agent],
      self._pz_env.terminations[agent],
      self._pz_env.truncations[agent],
      self._pz_env.infos[agent]
    )
    return observation, reward, terminated, truncated, info

  def _loop_others(self):
    agent = self._pz_env.agent_selection
    while agent in self._act_others:
      act_current = self._act_others[agent]
      obs_current = self._pz_env.observe(agent)
      action_current = act_current(obs_current)
      self._pz_env.step(action_current)
      agent = self._pz_env.agent_selection

  def render(self, *args, **kwargs):
    self._pz_env.render(*args, **kwargs)
