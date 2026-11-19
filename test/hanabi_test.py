import numpy as np
import pytest

from pettingzoo.classic import hanabi_v5


@pytest.mark.parametrize("random_start_player", [False, True])
def test_start_player(random_start_player):
    start_players = set()
    for seed in range(20):
        env = hanabi_v5.env(random_start_player=random_start_player)
        env.reset(seed=seed)
        start_players.add(env.agent_selection)
        rng = np.random.default_rng(seed)
        returns = dict.fromkeys(env.possible_agents, 0.0)
        for agent in env.agent_iter():
            observation, reward, termination, truncation, _ = env.last()
            returns[agent] += reward
            if termination or truncation:
                action = None
            else:
                # the agent on turn always has legal moves
                mask = observation["action_mask"]
                assert mask.any()
                action = int(rng.choice(np.flatnonzero(mask)))
            env.step(action)
        # the return of a game of legal moves is the final score (0 if all
        # lives are lost), an illegal move would end the game with -1
        assert all(r >= 0 for r in returns.values())
        env.close()

    if random_start_player:
        assert start_players == {"player_0", "player_1"}
    else:
        assert start_players == {"player_0"}
