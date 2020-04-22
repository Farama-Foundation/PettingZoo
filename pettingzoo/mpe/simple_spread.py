from ._mpe_utils.simple_env import SimpleEnv
from .scenarios.simple_spread import Scenario


class env(SimpleEnv):
    def __init__(self, seed=None, N=3, global_reward_weight=0.5, max_frames=500):
        assert 0. <= global_reward_weight <= 1., "global_reward_weight is a proportion. Must be between 0 and 1."
        scenario = Scenario()
        world = scenario.make_world(N)
        super(env, self).__init__(scenario, world, max_frames, seed, global_reward_weight)
