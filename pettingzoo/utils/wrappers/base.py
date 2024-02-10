from __future__ import annotations

from typing import Any

import gymnasium.spaces
import numpy as np

from pettingzoo.utils.env import ActionType, AECEnv, AgentID, ObsType


class BaseWrapper(AECEnv[AgentID, ObsType, ActionType]):
    """Creates a wrapper around `env` parameter.

    All AECEnv wrappers should inherit from this base class
    """

    # This is a list of object variables (as strings), used by THIS wrapper,
    # which should be stored by the wrapper object and not by the underlying
    # environment. They are used to store information that the wrapper needs
    # to behave correctly. The list is used by __setattr__() to determine where
    # to store variables. It is very important that this list is correct to
    # prevent confusing bugs.
    # Wrappers inheriting from this class should include their own _local_vars
    # list with object variables used by that class. Note that 'env' is hardcoded
    # as part of the __setattr__ function so should not be included.
    _local_vars = []

    def __init__(self, env: AECEnv[AgentID, ObsType, ActionType]):
        super().__init__()
        self.env = env

    def __getattr__(self, name: str) -> Any:
        """Returns an attribute with ``name``, unless ``name`` starts with an underscore."""
        if name.startswith("_") and name not in [
            "_cumulative_rewards",
            "_skip_agent_selection",
        ]:
            raise AttributeError(f"accessing private attribute '{name}' is prohibited")
        return getattr(self.env, name)

    def __setattr__(self, name: str, value: Any) -> None:
        """Set attribute ``name`` if it is this class's value, otherwise send to env."""
        # these are the attributes that can be set on this wrapper directly
        if name == "env" or name in self._local_vars:
            self.__dict__[name] = value
        else:
            # If this is being raised by your wrapper while you are trying to access
            # a variable that is owned by the wrapper and NOT part of the env, you
            # may have forgotten to add the variable to the _local_vars list.
            if name.startswith("_") and name not in [
                "_cumulative_rewards",
                "_skip_agent_selection",
            ]:
                raise AttributeError(
                    f"setting private attribute '{name}' is prohibited"
                )
            # send to the underlying environment to handle
            setattr(self.__dict__["env"], name, value)

    @property
    def unwrapped(self) -> AECEnv:
        return self.env.unwrapped

    def close(self) -> None:
        self.env.close()

    def render(self) -> None | np.ndarray | str | list:
        return self.env.render()

    def reset(self, seed: int | None = None, options: dict | None = None):
        self.env.reset(seed=seed, options=options)

    def observe(self, agent: AgentID) -> ObsType | None:
        return self.env.observe(agent)

    def state(self) -> np.ndarray:
        return self.env.state()

    def step(self, action: ActionType) -> None:
        self.env.step(action)

    def observation_space(self, agent: AgentID) -> gymnasium.spaces.Space:
        return self.env.observation_space(agent)

    def action_space(self, agent: AgentID) -> gymnasium.spaces.Space:
        return self.env.action_space(agent)

    def __str__(self) -> str:
        """Returns a name which looks like: "max_observation<space_invaders_v1>"."""
        return f"{type(self).__name__}<{str(self.env)}>"
