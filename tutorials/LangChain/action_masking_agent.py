import collections

from langchain.schema import HumanMessage, SystemMessage
from pettingzoo_agent import PettingZooAgent


class ActionMaskAgent(PettingZooAgent):
    def __init__(self, name, model, env):
        super().__init__(name, model, env)
        self.obs_buffer = collections.deque(maxlen=1)

    def random_action(self):
        obs = self.obs_buffer[-1]
        action = self.env.action_space(self.name).sample(obs["action_mask"])
        return action

    def reset(self):
        self.message_history = [
            SystemMessage(content=self.docs),
            SystemMessage(content=self.instructions),
        ]

    def observe(self, obs, rew=0, term=False, trunc=False, info=None):
        self.obs_buffer.append(obs)
        return super().observe(obs, rew, term, trunc, info)

    def _act(self):
        valid_action_instruction = "Generate a valid action given by the indices of the `action_mask` that are not 0, according to the action formatting rules."
        self.message_history.append(HumanMessage(content=valid_action_instruction))
        return super()._act()
