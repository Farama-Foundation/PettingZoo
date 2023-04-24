import pytest
from pettingzoo.utils.wrappers.aec_to_gymnasium import Aec2GymnasiumEnv
from pettingzoo.classic import tictactoe_v3
from gymnasium.utils.env_checker import check_env
import numpy as np


@pytest.mark.parametrize(
    [
        "me", "other"
    ],
    [
        ("player_1", "player_2"),
        ("player_2", "player_1"),
    ]
)
def test_tictactoe(me, other):
    aec_env = tictactoe_v3.env()
    
    def pick_a_free_square(obs):
        action_mask = obs['action_mask']
        possible_actions = np.where(action_mask == 1)[0]
        return np.random.choice(possible_actions)

    other_agents_logic = {
        other: pick_a_free_square
    }

    gym_env = Aec2GymnasiumEnv(
        aec_env=aec_env,
        external_agent=me,
        act_others=lambda agent, observation: other_agents_logic[agent](observation)
    )

    check_env(gym_env)

    observation, info = gym_env.reset(seed=42)
    for _ in range(10):
        action = gym_env.action_space.sample()  # this is where you would insert your policy
        observation, reward, terminated, truncated, info = gym_env.step(action)

        if terminated or truncated:
            observation, info = gym_env.reset()
    gym_env.close()
