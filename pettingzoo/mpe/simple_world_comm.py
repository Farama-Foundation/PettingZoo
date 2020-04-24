from ._mpe_utils.simple_env import SimpleEnv
from .scenarios.simple_world_comm import Scenario


class env(SimpleEnv):
    def __init__(self, seed=None, num_good=2, num_adversaries=4, num_obstacles=1, num_food=2, num_forests=2, max_frames=100):
        scenario = Scenario()
        world = scenario.make_world(num_good, num_adversaries, num_obstacles, num_food, num_forests)
        super(env, self).__init__(scenario, world, max_frames, seed)
