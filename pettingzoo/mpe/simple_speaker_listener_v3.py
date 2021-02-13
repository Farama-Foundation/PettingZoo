from ._mpe_utils.simple_env import SimpleEnv, make_env
from .scenarios.simple_speaker_listener import Scenario
from pettingzoo.utils.conversions import parallel_wrapper_fn


class raw_env(SimpleEnv):
    def __init__(self, max_cycles=25):
        scenario = Scenario()
        world = scenario.make_world()
        super().__init__(scenario, world, max_cycles)
        self.metadata['name'] = "simple_speaker_listener_v3"


env = make_env(raw_env)
parallel_env = parallel_wrapper_fn(env)
