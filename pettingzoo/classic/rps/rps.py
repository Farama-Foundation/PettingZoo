import gym
from gym.spaces import Discrete
# from ray.rllib.env.multi_agent_env import MultiAgentEnv

# Game originally from RLlib: https://github.com/ray-project/ray/blob/master/rllib/examples/rock_paper_scissors_multiagent.py

rock = 0
paper = 1
scissors = 2


# class rockpaperscissorsEnv(MultiAgentEnv):
class rockpaperscissorsEnv():
    """Two-player environment for rock paper scissors.
    The observation is simply the last opponent action."""

    def __init__(self):
        self.num_agents = 2
        self.agent_order = list(range(0, self.num_agents))
        self.agent_selection = 1

        self.action_space = Discrete(3)
        self.observation_space = Discrete(3)
        self.player1 = 0
        self.player2 = 1
        self.last_obs = None
        self.agent1_obs = None
        self.num_moves = 0

    def last(self):
        agent = self.agent_selection
        rew = self.last_reward[agent]
        done = self.last_done[agent]
        info = {}
        self.agent_selection = (self.agent_selection + 1) % self.num_agents
        return rew, done, info

    def reset(self):
        self.last_obs = (0, 0)
        self.num_moves = 0
        self.last_reward = {self.player1: 0,
                            self.player2: 0
                            }
        self.last_done = {self.player1: False,
                          self.player2: False}
        return {
            self.player1: self.last_obs[1],
            self.player2: self.last_obs[0],
        }

    def step(self, action):
        if self.agent_selection == 0: # first agent take action
            move1 = action 
            self.agent1_obs = move1
        else: # secound agent take action
            move1 = self.agent1_obs
            move2 = action 
            self.last_obs = (move1, move2)
            obs = {
                self.player1: self.last_obs[1],
                self.player2: self.last_obs[0],
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
            self.last_reward = rew 
            self.num_moves += 1
            self.last_done = {
                self.player1: self.num_moves >= 10,
                self.player2: self.num_moves >= 10,
            }
        return self.last_obs, self.last_reward, self.last_done, {}



env = rockpaperscissorsEnv()
observation = env.reset()
print(observation)
done = False
while not done:
    i = 1
    for _ in env.agent_order:
        reward, done, info = env.last()
        print(reward, done)
        # action = policy(observation)
        action = i
        i = (i+1) % 3
        observation = env.step(action)
