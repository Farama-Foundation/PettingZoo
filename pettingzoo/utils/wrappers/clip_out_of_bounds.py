import numpy as np
from gymnasium.spaces import Box

from pettingzoo.utils.env import AECEnv
from pettingzoo.utils.env_logger import EnvLogger
from pettingzoo.utils.wrappers.base import BaseWrapper


class ClipOutOfBoundsWrapper(BaseWrapper):
    """Clips the input action to fit in the continuous action space (emitting a warning if it does so).

    Applied to continuous environments in pettingzoo.
    """

    def __init__(self, env: AECEnv) -> None:
        super().__init__(env)
        assert all(
            isinstance(self.action_space(agent), Box)
            for agent in getattr(self, "possible_agents", [])
        ), "should only use ClipOutOfBoundsWrapper for Box spaces"

    def step(self, action: np.ndarray | None) -> None:
        space = self.action_space(self.agent_selection)
        if not (
            action is None
            and (
                self.terminations[self.agent_selection]
                or self.truncations[self.agent_selection]
            )
        ) and not space.contains(action):
            if action is None or np.isnan(action).any():
                EnvLogger.error_nan_action()
            assert (
                space.shape == action.shape  # type: ignore
            ), f"action should have shape {space.shape}, has shape {action.shape}"  # type: ignore

            EnvLogger.warn_action_out_of_bound(
                action=action, action_space=space, backup_policy="clipping to space"
            )
            action = np.clip(action, space.low, space.high)  # type: ignore

        super().step(action)

    def __str__(self) -> str:
        return str(self.env)
