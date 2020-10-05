from ._mpe_utils.simple_env import SimpleEnv, make_env
from .scenarios.simple_world_comm import Scenario
from pettingzoo.utils.to_parallel import parallel_wrapper_fn


class raw_env(SimpleEnv):
    def __init__(self, num_good=2, num_adversaries=4, num_obstacles=1, num_food=2, max_frames=25):
        scenario = Scenario()
        num_forests = 2  # crahes with any other number of forrests
        world = scenario.make_world(num_good, num_adversaries, num_obstacles, num_food, num_forests)
        super().__init__(scenario, world, max_frames)


env = make_env(raw_env)
parallel_env = parallel_wrapper_fn(env)
