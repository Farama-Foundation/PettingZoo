from pettingzoo.utils.conversions import parallel_wrapper_fn

from ._mpe_utils.simple_env import SimpleEnv, make_env
from .scenarios.simple_spread import Scenario

"""
This environment has N agents, N landmarks (default N=3). At a high level, agents must learn to cover all the landmarks while avoiding collisions.

More specifically, all agents are globally rewarded based on how far the closest agent is to each landmark (sum of the minimum distances). Locally, the agents are penalized if they collide with other agents (-1 for each collision). The relative weights of these rewards can be controlled with the `local_ratio` parameter.

Agent observations: `[self_vel, self_pos, landmark_rel_positions, other_agent_rel_positions, communication]`

Agent action space: `[no_action, move_left, move_right, move_down, move_up]`

### Arguments

:param N:  number of agents and landmarks
:param local_ratio:  Weight applied to local reward and global reward. Global reward weight will always be 1 - local reward weight.
:param max_cycles:  number of frames (a step for each agent) until game terminates
:param continuous_actions: Whether agent action spaces are discrete(default) or continuous
"""

class raw_env(SimpleEnv):
    def __init__(self, N=3, local_ratio=0.5, max_cycles=25, continuous_actions=False):
        assert 0. <= local_ratio <= 1., "local_ratio is a proportion. Must be between 0 and 1."
        scenario = Scenario()
        world = scenario.make_world(N)
        super().__init__(scenario, world, max_cycles, continuous_actions, local_ratio)
        self.metadata['name'] = "simple_spread_v2"


env = make_env(raw_env)
parallel_env = parallel_wrapper_fn(env)
