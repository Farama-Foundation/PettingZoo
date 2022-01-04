from pettingzoo.utils.conversions import parallel_wrapper_fn

from ._mpe_utils.simple_env import SimpleEnv, make_env
from .scenarios.simple_push import Scenario

"""
This environment has 1 good agent, 1 adversary, and 1 landmark. The good agent is rewarded based on the distance to the landmark. The adversary is rewarded if it is close to the landmark, and if the agent is far from the landmark (the difference of the distances). Thus the adversary must learn to push the good agent away from the landmark.

Agent observation space: `[self_vel, goal_rel_position, goal_landmark_id, all_landmark_rel_positions, landmark_ids, other_agent_rel_positions]`

Adversary observation space: `[self_vel, all_landmark_rel_positions, other_agent_rel_positions]`

Agent action space: `[no_action, move_left, move_right, move_down, move_up]`

Adversary action space: `[no_action, move_left, move_right, move_down, move_up]`

### Arguments

:param max_cycles:  number of frames (a step for each agent) until game terminates
"""

class raw_env(SimpleEnv):
    def __init__(self, max_cycles=25, continuous_actions=False):
        scenario = Scenario()
        world = scenario.make_world()
        super().__init__(scenario, world, max_cycles, continuous_actions)
        self.metadata['name'] = "simple_push_v2"


env = make_env(raw_env)
parallel_env = parallel_wrapper_fn(env)
