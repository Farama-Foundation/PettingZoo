from PettingZoo import MarkovEnv
import numpy as np

class markov_game(MarkovEnv):
    def __init__(self, AECEnv):
        super(markov_game, self).__init__()
        self.AECenv = AECEnv
        self.agents = AECEnv.agents
        self.observation_spaces = AECEnv.observation_spaces
        self.action_spaces = AECEnv.action_spaces

    def reset(self):
        self.AECenv.reset(observe=False)
        self.observations = {}
        for agent in self.agents:
            self.observations[agent] = self.AECenv.observe(agent)
        return self.observations

    def render(self):
        self.AECenv.render()

    def close(self):
        self.AECenv.close()

    def step(self, actions):
        for _ in self.agents:
            agent = self.AECenv.agent_selection
            self.AECenv.step(actions[agent], observe=False)

        for agent in self.agents:
            self.observations[agent] = self.AECEnv.observe(agent)

        return self.observations, self.AECEnv.rewards, self.AECEnv.dones, self.AECEnv.infos
