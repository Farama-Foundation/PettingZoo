from ray.rllib.env.multi_agent_env import MultiAgentEnv
import numpy as np

class markov_game(MultiAgentEnv):
    def __init__(self, AECEnv):
        super(markov_game, self).__init__()
        self.AECenv = AECEnv
        self.agents = AECEnv.agents
        self.observation_spaces = AECEnv.observation_spaces
        self.action_spaces = AECEnv.action_spaces
        self.observations = dict(zip(self.agents, len(self.agents)*[np.array([0])]))

    def reset(self):
        self.AECenv.reset(observe=False)
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
            self.observations[agent] = AECEnv.observe(agent)

        return self.observations, self.AECEnv.rewards, self.AECEnv.dones, self.AECEnv.infos
