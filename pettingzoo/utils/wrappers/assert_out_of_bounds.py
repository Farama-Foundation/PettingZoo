from gymnasium.spaces import Discrete

from .base import BaseWrapper


class AssertOutOfBoundsWrapper(BaseWrapper):
    """Asserts if the action given to step is outside of the action space. Applied in PettingZoo environments with discrete action spaces."""

    def __init__(self, env):
        super().__init__(env)
        assert all(
            isinstance(self.action_space(agent), Discrete)
            for agent in getattr(self, "possible_agents", [])
        ), "should only use AssertOutOfBoundsWrapper for Discrete spaces"

    def step(self, action):
        assert (
            action is None
            and (
                self.terminations[self.agent_selection]
                or self.truncations[self.agent_selection]
            )
        ) or self.action_space(self.agent_selection).contains(
            action
        ), "action is not in action space"
        super().step(action)

    def __str__(self):
        return str(self.env)
