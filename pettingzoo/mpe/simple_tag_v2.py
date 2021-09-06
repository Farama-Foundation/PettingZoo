from pettingzoo.utils.conversions import parallel_wrapper_fn

from ._mpe_utils.simple_env import SimpleEnv, make_env
from .scenarios.simple_tag import Scenario


class raw_env(SimpleEnv):
    def __init__(self, num_good=1, num_adversaries=3, num_obstacles=2, max_cycles=25, continuous_actions=False):
        scenario = Scenario()
        world = scenario.make_world(num_good, num_adversaries, num_obstacles)
        super().__init__(scenario, world, max_cycles, continuous_actions)
        self.metadata['name'] = "simple_tag_v2"


env = make_env(raw_env)
parallel_env = parallel_wrapper_fn(env)
