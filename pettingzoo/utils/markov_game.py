from ray.rllib.env.multi_agent_env import MultiAgentEnv
import numpy as np

class markov_game(MultiAgentEnv):
    def __init__(self, AECenv):
        super(markov_game, self).__init__()
        self.AECenv = AECenv
        self.agents = AECenv.agents
        self.observation_spaces = AECenv.observation_spaces
        self.action_spaces = AECenv.action_spaces
        self.dones = AECenv.dones
        self.rewards = AECenv.rewards
        self.infos = AECenv.infos
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
            self.observations[agent] = observation
            self.rewards[agent] = reward
            self.dones[agent] = done
            self.infos[agent] = info

        return self.observations, self.rewards, self.dones, self.infos
