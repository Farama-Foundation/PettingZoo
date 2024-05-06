from __future__ import annotations

import pytest

from pettingzoo.butterfly import pistonball_v6
from pettingzoo.classic import texas_holdem_no_limit_v6
from pettingzoo.utils.env import AECEnv
from pettingzoo.utils.wrappers import (
    BaseWrapper,
    MultiEpisodeEnv,
    MultiEpisodeParallelEnv,
)


@pytest.mark.parametrize(("num_episodes"), [1, 2, 3, 4, 5, 6])
def test_multi_episode_env_wrapper(num_episodes: int) -> None:
    """test_multi_episode_env_wrapper.

    The number of steps per environment are dictated by the seeding of the action space, not the environment.

    Args:
        num_episodes: number of episodes to run the MultiEpisodeEnv
    """
    env = texas_holdem_no_limit_v6.env(num_players=3)
    env = MultiEpisodeEnv(env, num_episodes=num_episodes)
    env.reset(seed=42)

    steps = 0
    for agent in env.agent_iter():
        steps += 1
        obs, rew, term, trunc, info = env.last()

        if term or trunc:
            action = None
        else:
            action_space = env.action_space(agent)
            action_space.seed(0)
            action = action_space.sample(mask=obs["action_mask"])

        env.step(action)

    env.close()

    assert (
        steps == num_episodes * 6
    ), f"Expected to have 6 steps per episode, got {steps / num_episodes}."


@pytest.mark.parametrize(("num_episodes"), [1, 2, 3, 4, 5, 6])
def test_multi_episode_parallel_env_wrapper(num_episodes) -> None:
    """test_multi_episode_parallel_env_wrapper.

    The default action for this test is to move all pistons down. This results in an episode length of 125.

    Args:
        num_episodes: number of episodes to run the MultiEpisodeEnv
    """
    env = pistonball_v6.parallel_env()
    env = MultiEpisodeParallelEnv(env, num_episodes=num_episodes)
    _ = env.reset(seed=42)

    steps = 0
    while env.agents:
        steps += 1
        # this is where you would insert your policy
        actions = {agent: env.action_space(agent).low for agent in env.agents}

        _ = env.step(actions)

    env.close()

    assert (
        steps == num_episodes * 125
    ), f"Expected to have 125 steps per episode, got {steps / num_episodes}."


class FakeEnv(AECEnv):
    """Fake environment used by the getattr and setattr tests."""

    def __init__(self):
        self.public_value: int = 123
        self._private_value: int = 456
        self.agents = ["a1, a2"]
        self.terminations = {agent: True for agent in self.agents}
        self.agent_selection = self.agents[0]
        self._name = "env"  # should never be used

    def compare_private(self, value: int) -> bool:
        """Return comparison of value with _private_value."""
        return self._private_value == value


class FakeWrapper(BaseWrapper):
    """Fake wrapper used by the getattr and setattr tests."""

    # these variables should be settable
    _local_vars = ["wrapper_variable", "_private_wrapper_variable"]

    def __init__(self, env: FakeEnv):
        super().__init__(env)
        # bypass __setattr__ so we have a private variable that is not in
        # the _local_vars list. We should be able to access this.
        self.__dict__["_name"] = "wrapper"


def test_wrapper_getattr() -> None:
    """Test that the base wrapper's __getattr__ works correctly.

    Public variables of the env can be accessed from the wrapper.
    Private variables cannot and will raise an AttributeError.
    """
    wrapped = FakeWrapper(FakeEnv())

    # Public values: fall through the the base env
    expected_public = wrapped.env.public_value  # can access directly from env
    assert (
        wrapped.public_value == expected_public
    ), "Wrapper can't access public env value"

    # Private values: trying to access should trigger an AttributeError
    expected_private = wrapped.env._private_value  # can access directly from env
    with pytest.raises(AttributeError):
        result = wrapped._private_value == expected_private

    # Meanwhile, calling an env function that does the same thing
    # should be fine because the the function is delegated to the env.
    result = wrapped.compare_private(expected_private)

    # Wrapper should not set any default value when trying to access a variable
    # that is not defined in the env or wrapper. It should trigger an AttributeError
    with pytest.raises(AttributeError):
        result = wrapped.nonexistant_value

    # However, should be able to intentionally assign a default value when
    # using getattr, even with a private variable.
    # Note: this works because the attempt to access _private_value
    # raises a new AttributeError from __getattr__ that causes getattr
    # to return the given default value.
    default = wrapped.env._private_value + 1  # ensure default is different
    result = getattr(wrapped, "_private_value", default)
    assert result == default, "Default value not set correctly"

    # Should be able to get any private variables owned by the wrapper,
    # even if not defined in _local_vars.
    # Note: This is not a design choice, it's a consequence the implementation.
    # FakeWrapper has _name defined on itself, but not listed in _local_vars.
    assert wrapped._name == "wrapper"


def test_wrapper_setattr() -> None:
    """Test that wrapper's setattr works properly.

    It should pass everything that isn't in _local_vars through to the
    base environment. Everything in _local vars should be stored in the
    wrapper object and not be part of the base environment.
    """
    wrapped = FakeWrapper(FakeEnv())

    # Having the wrapper directly set an env's public variable should:
    # 1) change the value in the env and 2) not set it in the wrapper.
    target_value = wrapped.public_value + 1  # ensure new value is different
    wrapped.public_value = target_value
    assert (
        wrapped.env.public_value == target_value
    ), "Wrapper didn't correctly set env value"
    assert "public_value" not in wrapped.__dict__, "Wrapper set value in wrong place"

    # Setting env's private value should only be allowed by the env.
    # Trying to directly do so from the wrapper should raise an AttributeError
    with pytest.raises(AttributeError):
        wrapped._private_value = target_value

    # Should work normally when accessed from the env
    wrapped.env._private_value = target_value

    # AECEnv._deads_step_first() currently sets _skip_agent_selection and
    # agent_selection. These should both be dispatched to the env, not set
    # on the wrapper.
    wrapped._deads_step_first()
    assert "_skip_agent_selection" in wrapped.env.__dict__, "Value not set on env"
    assert "agent_selection" in wrapped.env.__dict__, "Value not set on env"
    assert (
        "_skip_agent_selection" not in wrapped.__dict__
    ), "Wrapper set value in wrong place"
    assert "agent_selection" not in wrapped.__dict__, "Wrapper set value in wrong place"

    # All values in _local_vars that are set should go to the wrapper and
    # not the env, regardless of whether they are private or not
    for name in wrapped._local_vars:
        # should not be in either before being set
        assert (
            name not in wrapped.__dict__
        ), "test logic failure: variable should not be set"
        assert (
            name not in wrapped.env.__dict__
        ), "test logic failure: variable should not be set"
        setattr(wrapped, name, 1)
        assert name in wrapped.__dict__, "local wrapper value not set"
        assert name not in wrapped.env.__dict__, "local wrapper value set on env"

    # Not able to set any private variables, even if owned by the
    # wrapper, unless they are listed in _local_vars.
    # FakeWrapper has _name defined on itself, but not listed in _local_vars.
    with pytest.raises(AttributeError):
        wrapped._name = "changed wrapper"
