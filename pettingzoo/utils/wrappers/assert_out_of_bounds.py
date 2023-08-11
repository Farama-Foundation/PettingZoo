from __future__ import annotations

from pettingzoo.utils.env import ActionType, AECEnv
from pettingzoo.utils.wrappers.base import BaseWrapper


class AssertOutOfBoundsWrapper(BaseWrapper):
    """Asserts if the action given to step is outside of the action space."""

    def __init__(self, env: AECEnv):
        super().__init__(env)

    def step(self, action: ActionType) -> None:
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

    def __str__(self) -> str:
        return str(self.env)
