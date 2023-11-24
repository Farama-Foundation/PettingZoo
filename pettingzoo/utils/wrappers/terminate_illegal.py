# pyright reportGeneralTypeIssues=false
from __future__ import annotations

from pettingzoo.utils.env import ActionType, AECEnv, AgentID, ObsType
from pettingzoo.utils.env_logger import EnvLogger
from pettingzoo.utils.wrappers.base import BaseWrapper


class TerminateIllegalWrapper(BaseWrapper[AgentID, ObsType, ActionType]):
    """This wrapper terminates the game with the current player losing in case of illegal values.

    Args:
        illegal_reward: number that is the value of the player making an illegal move.
    """

    def __init__(
        self, env: AECEnv[AgentID, ObsType, ActionType], illegal_reward: float
    ):
        super().__init__(env)
        self._illegal_value = illegal_reward
        self._prev_obs = None
        self._prev_info = None

    def reset(self, seed: int | None = None, options: dict | None = None) -> None:
        self._terminated = False
        self._prev_obs = None
        self._prev_info = None
        super().reset(seed=seed, options=options)

    def observe(self, agent: AgentID) -> ObsType | None:
        obs = super().observe(agent)
        if agent == self.agent_selection:
            self._prev_obs = obs
            if self.agent_selection in self.infos:
                self._prev_info = self.infos[self.agent_selection]
            else:
                self._prev_info = {}
        return obs

    def step(self, action: ActionType) -> None:
        current_agent = self.agent_selection
        if self._prev_obs is None:
            self.observe(self.agent_selection)
        if isinstance(self._prev_obs, dict):
            assert self._prev_obs is not None
            assert (
                "action_mask" in self._prev_obs
            ), f"`action_mask` not found in dictionary observation: {self._prev_obs}. Action mask must either be in `observation['action_mask']` or `info['action_mask']` to use TerminateIllegalWrapper."
            _prev_action_mask = self._prev_obs["action_mask"]

        else:
            assert self._prev_info is not None
            assert (
                "action_mask" in self._prev_info
            ), f"`action_mask` not found in info for non-dictionary observation: {self._prev_info}. Action mask must either be in observation['action_mask'] or info['action_mask'] to use TerminateIllegalWrapper."
            _prev_action_mask = self._prev_info["action_mask"]
        self._prev_obs = None
        self._prev_info = None
        if self._terminated and (
            self.terminations[self.agent_selection]
            or self.truncations[self.agent_selection]
        ):
            self._was_dead_step(action)  # pyright: ignore[reportGeneralTypeIssues]
        elif (
            not self.terminations[self.agent_selection]
            and not self.truncations[self.agent_selection]
            and not _prev_action_mask[action]
        ):
            EnvLogger.warn_on_illegal_move()
            self.env.unwrapped._cumulative_rewards[self.agent_selection] = 0
            self.env.unwrapped.terminations = {d: True for d in self.agents}
            self.env.unwrapped.truncations = {d: True for d in self.agents}
            self._prev_obs = None
            self._prev_info = None
            self.env.unwrapped.rewards = {d: 0 for d in self.truncations}
            self.env.unwrapped.rewards[current_agent] = float(self._illegal_value)
            self._accumulate_rewards()
            self._deads_step_first()
            self._terminated = True
        else:
            super().step(action)

    def __str__(self) -> str:
        return str(self.env)
