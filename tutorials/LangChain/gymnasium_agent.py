import tenacity
from langchain.output_parsers import RegexParser
from langchain.schema import HumanMessage, SystemMessage


class GymnasiumAgent:
    @classmethod
    def get_docs(cls, env):
        return env.unwrapped.__doc__

    def __init__(self, model, env):
        self.model = model
        self.env = env
        self.docs = self.get_docs(env)

        self.instructions = """
Your goal is to maximize your return, i.e. the sum of the rewards you receive.
I will give you an observation, reward, terminiation flag, truncation flag, and the return so far, formatted as:

Observation: <observation>
Reward: <reward>
Termination: <termination>
Truncation: <truncation>
Return: <sum_of_rewards>

You will respond with an action, formatted as:

Action: <action>

where you replace <action> with your actual action.
Do nothing else but return the action.
"""
        self.action_parser = RegexParser(
            regex=r"Action: (.*)", output_keys=["action"], default_output_key="action"
        )

        self.message_history = []
        self.ret = 0

    def random_action(self):
        action = self.env.action_space.sample()
        return action

    def reset(self):
        self.message_history = [
            SystemMessage(content=self.docs),
            SystemMessage(content=self.instructions),
        ]

    def observe(self, obs, rew=0, term=False, trunc=False, info=None):
        self.ret += rew

        obs_message = f"""
Observation: {obs}
Reward: {rew}
Termination: {term}
Truncation: {trunc}
Return: {self.ret}
        """
        self.message_history.append(HumanMessage(content=obs_message))
        return obs_message

    def _act(self):
        act_message = self.model(self.message_history)
        self.message_history.append(act_message)
        action = int(self.action_parser.parse(act_message.content)["action"])
        return action

    def act(self):
        try:
            for attempt in tenacity.Retrying(
                stop=tenacity.stop_after_attempt(2),
                wait=tenacity.wait_none(),  # No waiting time between retries
                retry=tenacity.retry_if_exception_type(ValueError),
                before_sleep=lambda retry_state: print(
                    f"ValueError occurred: {retry_state.outcome.exception()}, retrying..."
                ),
            ):
                with attempt:
                    action = self._act()
        except tenacity.RetryError as e:  # noqa: F841
            action = self.random_action()
        return action
