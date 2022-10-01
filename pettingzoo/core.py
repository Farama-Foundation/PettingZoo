"""Core API for MultiAgentEnv and MultiAgentWrapper."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional, SupportsFloat, NamedTuple

import numpy as np
from gym.utils import seeding

import pettingzoo.spaces

EnvSpec = NamedTuple("EnvSpec", ("TODO",))


class MultiAgentEnv(ABC):
    """The main Multi-Agent API for environments."""

    _metadata: dict[str, Any] = {}
    _spec: EnvSpec | None = None
    _render_mode: str | None = None

    _observation_space: pettingzoo.spaces.Space[Any]
    _action_space: pettingzoo.spaces.Space[Any]

    _np_random: np.random.Generator

    _episode_steps: int = -1
    _max_episode_steps: Optional[int] = None

    _active: bool = False

    is_closed: bool = False

    @abstractmethod
    def reset(
        self, *, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Reset function for multi-agent environments.

        Args:
            seed: The seed for the environment
            options: The options when resetting the environment

        Returns:
            A tuple of agent observations and environment information
        """
        pass

    @abstractmethod
    def step(
        self, actions: dict[str, Any]
    ) -> tuple[
        dict[str, Any],
        dict[str, SupportsFloat],
        dict[str, bool],
        dict[str, bool],
        dict[str, Any],
    ]:
        """Step function for transitioning through the environment.

        Args:
            actions: The action to take for the current agent

        Returns:
            A tuple of next agent's observations, the agent's rewards, termination, truncation and info.
        """
        pass

    def render(self) -> Any:
        """Visualises the environment depending on `render_mode`.

        Returns:
            Depending on the `render_mode` the visualised environment state
        """
        raise NotImplementedError

    def close(self) -> None:
        """Closes the environment."""
        self.is_closed = True

    def __del__(self):
        """On destruction, if the environment hasn't been closed already, `env.close` is called."""
        if self.is_closed is False:
            self.close()

    @property
    def unwrapped(self) -> MultiAgentEnv:
        """Unwraps the wrappers to the base environment."""
        return self

    @property
    def observation_space(self) -> pettingzoo.spaces.Space[Any]:
        """The environment observation space."""
        return self._observation_space

    @observation_space.setter
    def observation_space(self, value: pettingzoo.spaces.Space[Any]):
        assert isinstance(value, pettingzoo.spaces.Space)
        self._observation_space = value

    @property
    def action_space(self) -> pettingzoo.spaces.Space[Any]:
        """The environment action space."""
        return self._action_space

    @action_space.setter
    def action_space(self, value: pettingzoo.spaces.Space[Any]):
        assert isinstance(value, pettingzoo.spaces.Space)
        self._action_space = value

    @property
    def np_random(self) -> np.random.Generator:
        """Returns the environment's internal :attr:`_np_random` that if not set will initialise with a random seed."""
        if self._np_random is None:
            self._np_random, _ = seeding.np_random()
        return self._np_random

    @np_random.setter
    def np_random(self, value: np.random.Generator):
        self._np_random = value

    @property
    def metadata(self) -> dict[str, Any]:
        """Returns the environment metadata."""
        return self._metadata

    @property
    def spec(self) -> EnvSpec | None:
        """Returns the environment specification used during `make`."""
        return self._spec

    @spec.setter
    def spec(self, value: EnvSpec):
        assert isinstance(value, EnvSpec)
        self._spec = value

    @property
    def render_mode(self) -> str | None:
        """Returns the environment render modes."""
        return self._render_mode

    @render_mode.setter
    def render_mode(self, value: str):
        assert isinstance(value, str)
        self._render_mode = value

    @property
    def active(self) -> bool:
        """If the environment is still alive to call `step`."""
        return self._active

    @property
    def episode_steps(self):
        """Returns the number of steps taken in an episode."""
        return self._episode_steps

    @episode_steps.setter
    def episode_steps(self, value: int):
        self._episode_steps = value

    @property
    def max_episode_steps(self) -> Optional[int]:
        """The maximum number of episode steps before truncation."""
        return self._max_episode_steps

    def __str__(self):
        """Returns a string of the environment with the spec id if specified."""
        if self.spec is None:
            return f"<{type(self).__name__} instance>"
        else:
            return f"<{type(self).__name__}<{self.spec.env_id}>>"

    def __enter__(self):
        """Support with-statement for the environment."""
        return self

    def __exit__(self):
        """Support with-statement for the environment."""
        self.close()
        return False


class MultiAgentWrapper(MultiAgentEnv, ABC):
    """Abstract wrapper for Multi-Agent Wrappers."""

    def __init__(
        self,
        env: MultiAgentEnv,
        observation_space: pettingzoo.spaces.Space[Any] | None = None,
        action_space: pettingzoo.spaces.Space[Any] | None = None,
    ):
        """Constructor for `MultiAgentWrapper` that requires the base environment and modified observation and action spaces.

        Args:
            env: The environment to wrap
            observation_space: The modified observation space, or `None` will use the `env.observation_space`
            action_space: The modified action space, otherwise `None` will use the `env.action_space`.
        """
        self.env = env

        self._wrapper_obs_space: pettingzoo.spaces.Space[Any] | None = observation_space
        self._wrapper_action_space: pettingzoo.spaces.Space[Any] | None = action_space

    def reset(
        self, *, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Resets the environment using the seed and options."""
        return self.env.reset(seed=seed, options=options)

    def step(
        self, actions: dict[str, Any]
    ) -> tuple[
        dict[str, Any],
        dict[str, SupportsFloat],
        dict[str, bool],
        dict[str, bool],
        dict[str, Any],
    ]:
        """Steps through the environment."""
        return self.env.step(actions)

    def render(self) -> Any:
        """Renders the environment returning the result."""
        return self.env.render()

    def close(self) -> None:
        """Closes the wrapper and the environment."""
        self.is_closed = True
        self.env.close()

    @property
    def observation_space(self):
        """The wrapper's observation space."""
        if self._wrapper_obs_space is None:
            return self.env.observation_space
        else:
            return self._wrapper_obs_space

    @observation_space.setter
    def observation_space(self, value: pettingzoo.spaces.Space[Any]):
        assert isinstance(value, pettingzoo.spaces.Space)
        self._wrapper_obs_space = value

    @property
    def action_space(self):
        """The wrapper's action space."""
        if self._wrapper_action_space is None:
            return self.env.action_space
        else:
            return self._wrapper_action_space

    @action_space.setter
    def action_space(self, value: pettingzoo.spaces.Space[Any]):
        assert isinstance(value, pettingzoo.spaces.Space)
        self._wrapper_action_space = value

    @property
    def unwrapped(self) -> MultiAgentEnv:
        """Wraps the wrappers from the base environment."""
        return self.env

    @property
    def np_random(self) -> np.random.Generator:
        """The random number generator of the environment."""
        return self.env.np_random

    @np_random.setter
    def np_random(self, value: np.random.Generator):
        self.env.np_random = value

    @property
    def metadata(self) -> dict[str, Any]:
        """Returns the environment metadata."""
        return self.env.metadata

    @property
    def spec(self) -> EnvSpec | None:
        """Returns the environment spec."""
        return self.env.spec

    @spec.setter
    def spec(self, value: EnvSpec):
        self.env.spec = value

    @property
    def render_mode(self) -> str | None:
        """Returns the environment render mode."""
        return self.env.render_mode

    @render_mode.setter
    def render_mode(self, value: str):
        self.env.render_mode = value

    @property
    def active(self) -> bool:
        """If the environment is still active."""
        return self.env.active

    @property
    def episode_steps(self) -> int:
        """The number of episode steps still left."""
        return self.env.episode_steps

    @episode_steps.setter
    def episode_steps(self, value: int):
        self.env.episode_steps = value

    @property
    def max_episode_steps(self) -> Optional[int]:
        """The maximum number of steps until the environment truncates."""
        return self.env.max_episode_steps
