from unittest import TestCase

from typing import Dict

from pettingzoo.classic.hanabi.hanabi import env

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
            'seed': 1 ,
            "random_start_player": 1
        }

        cls.incomplete_config: dict = {
            "colors": 5,
            "ranks": 5,
            "players": 3,
            "max_information_tokens": 8,
        }

        cls.config_values_out_of_reach: dict = {
            "colors": 20,
            "ranks": 5,
            "players": 3,
            "hand_size": 2,
            "max_information_tokens": 3,
            "max_life_tokens": 1,
            "observation_type": 0,
            'seed': 1 ,
            "random_start_player": 1
        }

    def test_preset(self):
        test = env(preset_name=self.preset_name)
        self.assertEqual(test.hanabi_env.__class__.__name__, 'HanabiEnv')

    def test_preset_with_players(self):
        test = env(preset_name=self.preset_name, players=self.player_count)
        self.assertEqual(test.hanabi_env.__class__.__name__, 'HanabiEnv')

    def test_full_dictionary(self):
        test = env(**self.full_config)
        self.assertEqual(test.hanabi_env.__class__.__name__, 'HanabiEnv')

    def test_incomplete_dictionary(self):
        self.assertRaises(KeyError, env, **self.incomplete_config)

    def test_config_values_out_of_range(self):
        self.assertRaises(ValueError, env, **self.config_values_out_of_reach)

    # ToDo:
    def test_step(self):
        pass

    def test_reset(self):
        test_env = env(**self.full_config)

        obs = test_env.reset()
        self.assertIsInstance(obs, Dict)

        obs = test_env.reset(observe=False)
        self.assertIsNone(obs)

    def test_observe(self):
        pass

    def test_last(self):
        pass

    def test_render(self):
        pass

    def test_close(self):
        pass
