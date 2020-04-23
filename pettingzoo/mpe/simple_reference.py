from ._mpe_utils.simple_env import SimpleEnv
from .scenarios.simple_reference import Scenario


class env(SimpleEnv):
    def __init__(self, seed=None, global_reward_weight=0.5, max_frames=500):
        assert 0. <= global_reward_weight <= 1., "global_reward_weight is a proportion. Must be between 0 and 1."
        scenario = Scenario()
        world = scenario.make_world()
        super(env, self).__init__(scenario, world, max_frames, seed, global_reward_weight)
