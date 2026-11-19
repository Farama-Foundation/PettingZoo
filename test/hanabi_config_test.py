import pytest

from pettingzoo.classic import hanabi_v5


@pytest.mark.parametrize(
    "colors, ranks, players, hand_size",
    [
        # deck of 2 * colors * ranks cards is too small for the initial deal
        (2, 2, 2, 5),
        (3, 2, 3, 5),
        (5, 2, 5, 5),
        (2, 2, 3, 3),
        (2, 3, 5, 3),
    ],
)
def test_config_deck_too_small(colors, ranks, players, hand_size):
    with pytest.raises(ValueError, match="initial deal"):
        hanabi_v5.raw_env(
            colors=colors, ranks=ranks, players=players, hand_size=hand_size
        )


@pytest.mark.parametrize(
    "colors, ranks, players, hand_size",
    [
        (2, 2, 2, 4),  # initial deal uses the whole deck
        (2, 2, 4, 2),
        (2, 5, 3, 2),
        (2, 5, 5, 4),
        (3, 3, 5, 3),
    ],
)
def test_config_valid(colors, ranks, players, hand_size):
    pytest.importorskip("pyspiel")
    env = hanabi_v5.env(
        colors=colors, ranks=ranks, players=players, hand_size=hand_size
    )
    env.reset(seed=0)
    assert len(env.agents) == players
    for agent in env.agent_iter(20):
        observation, _, termination, truncation, _ = env.last()
        if termination or truncation:
            action = None
        else:
            action = env.action_space(agent).sample(observation["action_mask"])
        env.step(action)
    env.close()
