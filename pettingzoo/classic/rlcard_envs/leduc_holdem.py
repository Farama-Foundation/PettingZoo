import gym
from rlcard.utils.utils import print_card

from pettingzoo.utils import wrappers

from .rlcard_base import RLCardBase


def env(**kwargs):
    render_mode = kwargs.get("render_mode")
    if render_mode == "ansi":
        kwargs["render_mode"] = "human"
        env = raw_env(**kwargs)
        env = wrappers.CaptureStdoutWrapper(env)
    else:
        env = raw_env(**kwargs)
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(RLCardBase):

    metadata = {
        "render_modes": ["human"],
        "name": "leduc_holdem_v4",
        "is_parallelizable": False,
        "render_fps": 1,
    }

    def __init__(self, num_players=2, render_mode=None):
        super().__init__("leduc-holdem", num_players, (36,))
        self.render_mode = render_mode

    def render(self):
        if self.render_mode is None:
            gym.logger.WARN(
                "You are calling render method without specifying any render mode."
            )
            return

        for player in self.possible_agents:
            state = self.env.game.get_state(self._name_to_int(player))
            print(f"\n=============== {player}'s Hand ===============")
            print_card(state["hand"])
            print("\n{}'s Chips: {}".format(player, state["my_chips"]))
        print("\n================= Public Cards =================")
        print_card(state["public_card"]) if state["public_card"] is not None else print(
            "No public cards."
        )
        print("\n")
