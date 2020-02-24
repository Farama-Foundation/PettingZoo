import gym
from gym.spaces import Discrete
from ray.rllib.env.multi_agent_env import MultiAgentEnv

# Game originally from RLlib: https://github.com/ray-project/ray/blob/master/rllib/examples/rock_paper_scissors_multiagent.py

rock = 0
paper = 1
scissors = 2


class rockpaperscissorsEnv(MultiAgentEnv):
    """Two-player environment for rock paper scissors.
    The observation is simply the last opponent action."""

    def __init__(self, _):
        self.action_space = Discrete(3)
        self.observation_space = Discrete(3)
        self.player1 = "player1"
        self.player2 = "player2"
        self.last_move = None
        self.num_moves = 0

    def reset(self):
        self.last_move = (0, 0)
        self.num_moves = 0
        return {
            self.player1: self.last_move[1],
            self.player2: self.last_move[0],
        }

    def step(self, action_dict):
        move1 = action_dict[self.player1]
        move2 = action_dict[self.player2]
        self.last_move = (move1, move2)
        obs = {
            self.player1: self.last_move[1],
            self.player2: self.last_move[0],
        }
        r1, r2 = {
            (rock, rock): (0, 0),
            (rock, paper): (-1, 1),
            (rock, scissors): (1, -1),
            (paper, rock): (1, -1),
            (paper, paper): (0, 0),
            (paper, scissors): (-1, 1),
            (scissors, rock): (-1, 1),
            (scissors, paper): (1, -1),
            (scissors, scissors): (0, 0),
        }[move1, move2]
        rew = {
            self.player1: r1,
            self.player2: r2,
        }
        self.num_moves += 1
        done = {
            "__all__": self.num_moves >= 10,
        }
        return obs, rew, done, {}

# temp = rockpaperscissorsEnv()
# action_dict = {"player1": 1,
#                 "player2": 2}
# print(temp.reset())
# print(temp.step(action_dict))
# print(temp.num_moves)