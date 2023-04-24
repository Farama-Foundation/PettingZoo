from pettingzoo.utils.wrappers.pz_to_gymnasium_wrapper import PZ2GymnasiumWrapper
from pettingzoo.classic import tictactoe_v3
from gymnasium.utils.env_checker import check_env


def test_tictactoe():
    pz_env = tictactoe_v3.env()
    pz_env.reset()
    
    def pick_a_free_square(obs):
        action_mask = obs['action_mask']
        return action_mask.tolist().index(1)

    other_agents_logic = {
        'player_2': pick_a_free_square
    }

    gym_env = PZ2GymnasiumWrapper(
        pz_env=pz_env,
        the_external_agent='player_1',
        act_others=lambda agent, observation: other_agents_logic[agent](observation)
    )

    check_env(gym_env)
