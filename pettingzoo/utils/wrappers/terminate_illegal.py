from .base import BaseWrapper
from ..env_logger import EnvLogger


class TerminateIllegalWrapper(BaseWrapper):
    '''
    this wrapper terminates the game with the current player losing
    in case of illegal values

    parameters:
        - illegal_reward: number that is the value of the player making an illegal move.
    '''
    def __init__(self, env, illegal_reward):
        super().__init__(env)
        self._illegal_value = illegal_reward
        self._prev_obs = None

    def reset(self):
        self._terminated = False
        self._prev_obs = None
        super().reset()

    def observe(self, agent):
        obs = super().observe(agent)
        if agent == self.agent_selection:
            self._prev_obs = obs
        return obs

    def step(self, action):
        current_agent = self.agent_selection
        if self._prev_obs is None:
            self.observe(self.agent_selection)
        assert 'action_mask' in self._prev_obs, "action_mask must always be part of environment observation as an element in a dictionary observation to use the TerminateIllegalWrapper"
        _prev_action_mask = self._prev_obs['action_mask']
        self._prev_obs = None
        if self._terminated and self.dones[self.agent_selection]:
            self._was_done_step(action)
        elif not self.dones[self.agent_selection] and not _prev_action_mask[action]:
            EnvLogger.warn_on_illegal_move()
            self._cumulative_rewards[self.agent_selection] = 0
            self.dones = {d: True for d in self.dones}
            self._prev_obs = None
            self.rewards = {d: 0 for d in self.dones}
            self.rewards[current_agent] = float(self._illegal_value)
            self._accumulate_rewards()
            self._dones_step_first()
            self._terminated = True
        else:
            super().step(action)

    def __str__(self):
        return str(self.env)
