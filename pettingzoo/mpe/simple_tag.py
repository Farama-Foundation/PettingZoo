from ._mpe_utils.simple_env import SimpleEnv, make_env
from .scenarios.simple_tag import Scenario


class raw_env(SimpleEnv):

    def __init__(self, seed=None, num_good=1, num_adversaries=3, num_obstacles=2, max_frames=100):
        scenario = Scenario()
        world = scenario.make_world(num_good, num_adversaries, num_obstacles)
        super().__init__(scenario, world, max_frames, seed)


env = make_env(raw_env)
