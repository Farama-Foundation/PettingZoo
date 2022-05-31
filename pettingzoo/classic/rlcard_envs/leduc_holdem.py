from rlcard.utils.utils import print_card

from pettingzoo.utils import wrappers

from .rlcard_base import RLCardBase


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.CaptureStdoutWrapper(env)
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

    def __init__(self, num_players=2):
        super().__init__("leduc-holdem", num_players, (36,))

    def render(self, mode="human"):
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
