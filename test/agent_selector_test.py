import numpy as np
import pytest

from pettingzoo.butterfly import cooperative_pong_v6
from pettingzoo.classic import connect_four_v3, rps_v2, tictactoe_v3
from pettingzoo.utils import AgentSelector


def test_reset_rewinds_to_first_agent():
    selector = AgentSelector(["a", "b", "c"])
    assert selector.reset() == "a"
    assert selector.next() == "b"
    assert selector.next() == "c"

    assert selector.reset() == "a"
    assert selector.next() == "b"


def test_reset_after_partial_dead_step_restores_every_agent():
    """The case reported in #1229 and checked in #1332.

    Resetting while one agent has already been dead stepped out of .agents must
    bring both agents back into the cycle.
    """
    env = tictactoe_v3.env()
    env.reset(seed=0)
    unwrapped = env.unwrapped

    env.step(0)  # player_1 plays a legal move
    env.step(0)  # player_2 plays an illegal one, terminating both
    env.step(None)  # dead step only player_1, so .agents is short

    assert unwrapped.agents == ["player_2"]

    env.reset(seed=0)

    assert unwrapped.agents == ["player_1", "player_2"]
    assert unwrapped._agent_selector.agent_order == ["player_1", "player_2"]
    assert env.agent_selection == "player_1"


def _play_episode(env, seed):
    env.reset(seed=seed)
    for agent in env.agent_iter(10_000):
        obs, _, termination, truncation, info = env.last()
        if termination or truncation:
            action = None
        else:
            mask = None
            if isinstance(obs, dict):
                mask = obs.get("action_mask")
            mask = info.get("action_mask", mask)
            if mask is not None:
                mask = np.asarray(mask, dtype=np.int8)
            action = env.action_space(agent).sample(mask)
        env.step(action)
    assert not env.agents


@pytest.mark.parametrize(
    "make_env",
    [
        tictactoe_v3.env,
        connect_four_v3.env,
        lambda: rps_v2.env(num_actions=3, max_cycles=5),
        # builds its selector once in __init__ and only calls reset() on it
        lambda: cooperative_pong_v6.env(max_cycles=50),
    ],
    ids=["tictactoe", "connect_four", "rps", "cooperative_pong"],
)
def test_reset_after_finished_episode_restores_the_cycle(make_env):
    env = make_env()

    for seed in range(3):
        _play_episode(env, seed)

        env.reset(seed=seed)
        unwrapped = env.unwrapped
        assert unwrapped.agents == unwrapped.possible_agents
        assert list(unwrapped._agent_selector.agent_order) == unwrapped.agents
        assert env.agent_selection == unwrapped.agents[0]
