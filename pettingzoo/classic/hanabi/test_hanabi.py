from unittest import TestCase
from pettingzoo.classic.hanabi.hanabi import env
import pettingzoo.tests.api_test as api_test
import numpy as np


class HanabiTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.preset_name = "Hanabi-Small"
        cls.player_count = 4
        cls.full_config: dict = {
            "colors": 2,
            "ranks": 5,
            "players": 3,
            "hand_size": 2,
            "max_information_tokens": 3,
            "max_life_tokens": 1,
            "observation_type": 0,
            'seed': 1,
            "random_start_player": 1
        }

        cls.config_values_out_of_reach: dict = {
            "colors": 20,
            "ranks": 5,
            "players": 3,
            "hand_size": 2,
            "max_information_tokens": 3,
            "max_life_tokens": 1,
            "observation_type": 0,
            'seed': 1,
            "random_start_player": 1
        }

    def test_full_dictionary(self):
        test = env(**self.full_config)
        self.assertEqual(test.hanabi_env.__class__.__name__, 'HanabiEnv')

    def test_config_values_out_of_range(self):
        self.assertRaises(ValueError, env, **self.config_values_out_of_reach)

    def test_reset(self):
        test_env = env(**self.full_config)

        obs = test_env.reset()
        self.assertIsInstance(obs, np.ndarray)
        self.assertEqual(obs.size, test_env.hanabi_env.vectorized_observation_shape()[0])

        obs = test_env.reset(observe=False)
        self.assertIsNone(obs)

        old_state = test_env.hanabi_env.state
        test_env.reset(observe=False)
        new_state = test_env.hanabi_env.state

        self.assertNotEqual(old_state, new_state)

    def test_get_legal_moves(self):
        test_env = env(**self.full_config)
        self.assertIs(set(test_env.legal_moves).issubset(set(test_env.all_moves)), True)

    def test_observe(self):
        # Tested within test_step
        pass

    def test_step(self):
        test_env = env(**self.full_config)

        # Get current player
        old_player = test_env.agent_selection

        # Pick a legal move
        legal_moves = test_env.legal_moves

        # Assert return value
        new_obs = test_env.step(action=legal_moves[0])
        self.assertIsInstance(test_env.infos, dict)
        self.assertIsInstance(new_obs, np.ndarray)
        self.assertEqual(new_obs.size, test_env.hanabi_env.vectorized_observation_shape()[0])

        # Get new_player
        new_player = test_env.agent_selection
        # Assert player shifted
        self.assertNotEqual(old_player, new_player)

        # Assert legal moves have changed
        new_legal_moves = test_env.legal_moves
        self.assertNotEqual(legal_moves, new_legal_moves)

        # Assert return not as vector:
        new_obs = test_env.step(action=new_legal_moves[0], as_vector=False)
        self.assertIsInstance(new_obs, dict)

        # Assert no return
        new_legal_moves = test_env.legal_moves
        new_obs = test_env.step(action=new_legal_moves[0], observe=False)
        self.assertIsNone(new_obs)

        # Assert raises error if wrong input
        new_legal_moves = test_env.legal_moves
        illegal_move = list(set(test_env.all_moves) - set(new_legal_moves))[0]
        self.assertRaises(ValueError, test_env.step, illegal_move)

    def test_legal_moves(self):
        test_env = env(**self.full_config)
        legal_moves = test_env.legal_moves

        self.assertIsInstance(legal_moves, list)
        self.assertIsInstance(legal_moves[0], int)
        self.assertLessEqual(len(legal_moves), len(test_env.all_moves))
        test_env.step(legal_moves[0])

    def test_run_whole_game(self):
        test_env = env(**self.full_config)

        while not all(test_env.dones.values()):
            self.assertIs(all(test_env.dones.values()), False)
            test_env.step(test_env.legal_moves[0], observe=False)

        test_env.reset(observe=False)

        while not all(test_env.dones.values()):
            self.assertIs(all(test_env.dones.values()), False)
            test_env.step(test_env.legal_moves[0], observe=False)

        self.assertIs(all(test_env.dones.values()), True)

    def test_api(self):
        api_test.api_test(env(**self.full_config))
