import gym
from gym.spaces import Discrete
from ray.rllib.env.multi_agent_env import MultiAgentEnv

# Game originally from RLlib: https://github.com/ray-project/ray/blob/master/rllib/examples/rock_paper_scissors_multiagent.py

rock = 0
paper = 1
scissors = 2
lizard = 3
spock = 4


class rockpaperscissorsEnv(MultiAgentEnv):
    """Two-player environment for rock paper scissors lizard spock.
    The observation is simply the last opponent action."""

    def __init__(self, _):
        self.action_space = Discrete(5)
        self.observation_space = Discrete(5)
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
            (rock, lizard): (1, -1),
            (rock, spock): (-1, 1),

            (paper, rock): (1, -1),
            (paper, paper): (0, 0),
            (paper, scissors): (-1, 1),
            (paper, lizard): (-1, 1),
            (paper, spock): (1, -1),

            (scissors, rock): (-1, 1),
            (scissors, paper): (1, -1),
            (scissors, scissors): (0, 0),
            (scissors, lizard): (1, -1),
            (scissors, spock): (-1, 1),

            (lizard, rock): (-1, 1),
            (lizard, paper): (1, -1),
            (lizard, scissors): (-1, 1),
            (lizard, lizard): (0, 0),
            (lizard, spock): (1, -1),

            (spock, rock): (1, -1),
            (spock, paper): (-1, 1),
            (spock, scissors): (1, -1),
            (spock, lizard): (-1, 1),
            (spock, spock): (0, 0),

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
