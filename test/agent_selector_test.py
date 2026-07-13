import pytest

from pettingzoo.classic import tictactoe_v3
from pettingzoo.test.example_envs import generated_agents_env_v0
from pettingzoo.utils import AgentSelector


def test_reinit_copies_the_order():
    """The selector owns its order; mutating the caller's list must not move it."""
    agents = ["player_1", "player_2"]
    selector = AgentSelector(agents)

    agents.remove("player_1")

    assert selector.agent_order == ["player_1", "player_2"]
    assert selector.reset() == "player_1"


def test_add_and_remove_agent():
    selector = AgentSelector(["a", "b"])
    selector.add_agent("c")
    assert selector.agent_order == ["a", "b", "c"]

    selector.remove_agent("b")
    assert selector.agent_order == ["a", "c"]


def test_remove_absent_agent_is_a_noop():
    """Envs that already dropped an agent themselves can still call this."""
    selector = AgentSelector(["a", "b"])
    selector.remove_agent("not_an_agent")
    assert selector.agent_order == ["a", "b"]


def test_dead_step_removes_agent_from_the_cycle():
    """_was_dead_step() keeps the selector in sync when it drops an agent."""
    env = tictactoe_v3.env()
    env.reset(seed=0)
    unwrapped = env.unwrapped

    # An illegal move terminates both players, so both get dead-stepped out.
    env.step(0)
    env.step(0)

    dead = env.agent_selection
    env.step(None)

    assert dead not in unwrapped.agents
    assert dead not in unwrapped._agent_selector.agent_order


def test_reset_after_partial_dead_step_restores_every_agent():
    """Regression test for the case raised in #1229 / #1332.

    Resetting while an agent is still missing from .agents must bring the whole
    cycle back, rather than leaving that agent unselectable forever.
    """
    env = tictactoe_v3.env()
    env.reset(seed=0)
    unwrapped = env.unwrapped

    env.step(0)  # player_1 plays a legal move
    env.step(0)  # player_2 plays an illegal one, terminating both
    env.step(None)  # dead-step only player_1, so .agents is short

    assert unwrapped.agents == ["player_2"]

    env.reset(seed=0)

    assert unwrapped.agents == ["player_1", "player_2"]
    assert unwrapped._agent_selector.agent_order == ["player_1", "player_2"]
    assert env.agent_selection == "player_1"


def test_agents_added_mid_episode_join_the_cycle():
    """Dynamic-agent envs register new agents with the selector explicitly."""
    env = generated_agents_env_v0.raw_env()
    env.reset(seed=0)

    agent = env.add_agent(env.types[0])

    assert agent in env.agents
    assert agent in env._agent_selector.agent_order


def test_selector_order_does_not_leak_across_resets():
    env = generated_agents_env_v0.raw_env()
    env.reset(seed=0)
    first = list(env._agent_selector.agent_order)

    env.reset(seed=0)

    assert env._agent_selector.agent_order == first
    assert env._agent_selector.agent_order == env.agents


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_generated_agents_env_cycles_cleanly(seed):
    """The selector and .agents stay consistent through a full dynamic episode."""
    env = generated_agents_env_v0.env()
    env.reset(seed=seed)

    for agent in env.agent_iter(200):
        _, _, termination, truncation, _ = env.last()
        action = None if termination or truncation else env.action_space(agent).sample()
        env.step(action)

    assert env.unwrapped._agent_selector.agent_order == env.unwrapped.agents
