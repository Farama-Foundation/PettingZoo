"""Check for a problem with terminate illegal wrapper.

The problem is that env variables, including agent_selection, are set by
calls from TerminateIllegalWrapper to env functions. However, they are
called by the wrapper object, not the env so they are set in the wrapper
object rather than the base env object. When the code later tries to run,
the values get updated in the env code, but the wrapper pulls it's own
values that shadow them.

The test here confirms that is fixed.
"""

from pettingzoo.classic import tictactoe_v3
from pettingzoo.utils.wrappers import BaseWrapper, TerminateIllegalWrapper


def _do_game(env: TerminateIllegalWrapper, seed: int) -> None:
    """Run a single game with reproducible random moves."""
    assert isinstance(
        env, TerminateIllegalWrapper
    ), "test_terminate_illegal must use TerminateIllegalWrapper"
    env.reset(seed)
    for agent in env.agents:
        # make the random moves reproducible
        env.action_space(agent).seed(seed)

    for agent in env.agent_iter():
        _, _, termination, truncation, _ = env.last()

        if termination or truncation:
            env.step(None)
        else:
            action = env.action_space(agent).sample()
            env.step(action)


def test_terminate_illegal() -> None:
    """Test for error in TerminateIllegalWrapper.

    A bug caused TerminateIllegalWrapper to set values on the wrapper
    rather than the environment. This tests for a recurrence of that
    bug.
    """
    # not using env() because we need to ensure that the env is
    # wrapped by TerminateIllegalWrapper
    raw_env = tictactoe_v3.raw_env()
    env = TerminateIllegalWrapper(raw_env, illegal_reward=-1)

    _do_game(env, 42)
    # bug is triggered by a corrupted state after a game is terminated
    # due to an illegal move. So we need to run the game twice to
    # see the effect.
    _do_game(env, 42)

    # get a list of what all the agent_selection values in the wrapper stack
    unwrapped = env
    agent_selections = []
    while unwrapped != env.unwrapped:
        # the actual value for this wrapper (or None if no value)
        agent_selections.append(unwrapped.__dict__.get("agent_selection", None))
        assert isinstance(unwrapped, BaseWrapper)
        unwrapped = unwrapped.env

    # last one from the actual env
    agent_selections.append(unwrapped.__dict__.get("agent_selection", None))

    # remove None from agent_selections
    agent_selections = [x for x in agent_selections if x is not None]

    # all values must be the same, or else the wrapper and env are mismatched
    assert len(set(agent_selections)) == 1, "agent_selection mismatch"
