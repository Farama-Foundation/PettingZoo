from __future__ import annotations

from collections import deque
from typing import Any, Final, cast

import numpy as np
from gymnasium.spaces import Space
from gymnasium.wrappers.utils import create_zero_array
from typing_extensions import override

from pettingzoo.utils.env import ActionType, AECEnv, AgentID, ObsType, ParallelEnv
from pettingzoo.utils.wrappers.base import BaseWrapper
from pettingzoo.utils.wrappers.base_parallel import BaseParallelWrapper


def _validate_delay(delay: int) -> int:
    if not np.issubdtype(type(delay), np.integer):
        raise TypeError(
            f"The delay is expected to be an integer, actual type: {type(delay)}"
        )
    if delay < 0:
        raise ValueError(
            f"The delay needs to be greater than or equal to zero, actual value: {delay}"
        )
    return int(delay)


def _create_initial_observation(space: Space[ObsType]) -> ObsType:
    observation = create_zero_array(space)

    # SuperSuit's delay_observations_v0 uses an all-ones action mask while the
    # observation history is empty so that the placeholder does not declare
    # every action illegal.
    if (
        isinstance(observation, dict)
        and "observation" in observation
        and "action_mask" in observation
    ):
        observation["action_mask"] = np.ones_like(observation["action_mask"])

    return cast(ObsType, observation)


class DelayObservation(BaseWrapper[AgentID, ObsType, ActionType]):
    """Add a fixed, per-agent delay to observations from an AEC environment.

    Each agent has an independent observation history. Before an agent has
    accumulated ``delay`` previous observations, the wrapper returns a valid
    zero-like observation from that agent's observation space. For observation
    dictionaries containing ``"observation"`` and ``"action_mask"``, the
    initial action mask contains ones so that it does not mark every action as
    illegal.

    Observation histories advance only when the environment progresses to an
    agent. Calling :meth:`observe` repeatedly does not advance the delay.
    Histories are cleared whenever the environment is reset.

    Args:
        env: The AEC environment to wrap.
        delay: The number of that agent's observation updates to delay. Must be
            a non-negative integer.
    """

    def __init__(self, env: AECEnv[AgentID, ObsType, ActionType], delay: int):
        super().__init__(env)

        self.delay: Final[int] = _validate_delay(delay)
        self._observation_queues: dict[AgentID, deque[ObsType]] = {}
        self._delayed_observations: dict[AgentID, ObsType | None] = {}

    def _delay_observation(self, agent: AgentID, observation: ObsType) -> ObsType:
        observation_queue = self._observation_queues.setdefault(agent, deque())
        observation_queue.append(observation)

        if len(observation_queue) > self.delay:
            return observation_queue.popleft()
        return cast(ObsType, _create_initial_observation(self.observation_space(agent)))

    def _update_selected_agent_observation(self) -> None:
        if not self.agents:
            return

        agent = self.agent_selection
        observation = super().observe(agent)
        if observation is None:
            self._delayed_observations[agent] = None
        else:
            self._delayed_observations[agent] = self._delay_observation(
                agent, observation
            )

    @override
    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> None:
        """Reset the environment and clear all agents' observation histories."""
        self._observation_queues.clear()
        self._delayed_observations.clear()
        super().reset(seed=seed, options=options)
        self._update_selected_agent_observation()

    @override
    def step(self, action: ActionType) -> None:
        """Step the environment and update the newly selected agent's history."""
        super().step(action)
        self._update_selected_agent_observation()

    @override
    def observe(self, agent: AgentID) -> ObsType | None:
        """Return an agent's cached delayed observation without advancing it."""
        if agent in self._delayed_observations:
            return self._delayed_observations[agent]
        observation = super().observe(agent)
        if observation is None:
            return None
        return cast(ObsType, _create_initial_observation(self.observation_space(agent)))


class DelayObservationParallel(BaseParallelWrapper[AgentID, ObsType, ActionType]):
    """Add a fixed, per-agent delay to observations from a Parallel environment.

    Each agent has an independent observation history. Before an agent has
    accumulated ``delay`` previous observations, the wrapper returns a valid
    zero-like observation from that agent's observation space. For observation
    dictionaries containing ``"observation"`` and ``"action_mask"``, the
    initial action mask contains ones so that it does not mark every action as
    illegal. Histories are cleared whenever the environment is reset.

    Args:
        env: The Parallel environment to wrap.
        delay: The number of that agent's observation updates to delay. Must be
            a non-negative integer.
    """

    def __init__(self, env: ParallelEnv[AgentID, ObsType, ActionType], delay: int):
        super().__init__(env)

        self.delay: Final[int] = _validate_delay(delay)
        self._observation_queues: dict[AgentID, deque[ObsType]] = {}

    def _delay_observation(self, agent: AgentID, observation: ObsType) -> ObsType:
        observation_queue = self._observation_queues.setdefault(agent, deque())
        observation_queue.append(observation)

        if len(observation_queue) > self.delay:
            return observation_queue.popleft()
        return cast(ObsType, _create_initial_observation(self.observation_space(agent)))

    @override
    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict[AgentID, ObsType], dict[AgentID, dict[str, Any]]]:
        """Reset the environment and clear all agents' observation histories."""
        self._observation_queues.clear()
        observations, infos = super().reset(seed=seed, options=options)
        delayed_observations = {
            agent: self._delay_observation(agent, observation)
            for agent, observation in observations.items()
        }
        return delayed_observations, infos

    @override
    def step(
        self, actions: dict[AgentID, ActionType]
    ) -> tuple[
        dict[AgentID, ObsType],
        dict[AgentID, float],
        dict[AgentID, bool],
        dict[AgentID, bool],
        dict[AgentID, dict[str, Any]],
    ]:
        """Step the environment and delay each returned agent observation."""
        observations, rewards, terminations, truncations, infos = super().step(actions)
        delayed_observations = {
            agent: self._delay_observation(agent, observation)
            for agent, observation in observations.items()
        }
        return delayed_observations, rewards, terminations, truncations, infos
