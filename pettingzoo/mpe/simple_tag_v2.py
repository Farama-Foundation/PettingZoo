from pettingzoo.utils.conversions import parallel_wrapper_fn

from ._mpe_utils.simple_env import SimpleEnv, make_env
from .scenarios.simple_tag import Scenario

"""
This is a predator-prey environment. Good agents (green) are faster and receive a negative reward for being hit by adversaries (red) (-10 for each collision). Adversaries are slower and are rewarded for hitting good agents (+10 for each collision). Obstacles (large black circles) block the way. By default, there is 1 good agent, 3 adversaries and 2 obstacles.

Agent and adversary observations: `[self_vel, self_pos, landmark_rel_positions, other_agent_rel_positions, other_agent_velocities]`

Agent and adversary action space: `[no_action, move_left, move_right, move_down, move_up]`

### Arguments

:param num_good:  number of good agents
:param num_adversaries:  number of adversaries
:param num_obstacles:  number of obstacles
:param max_cycles:  number of frames (a step for each agent) until game terminates
:param continuous_actions: Whether agent action spaces are discrete(default) or continuous
"""

class raw_env(SimpleEnv):
    def __init__(self, num_good=1, num_adversaries=3, num_obstacles=2, max_cycles=25, continuous_actions=False):
        scenario = Scenario()
        world = scenario.make_world(num_good, num_adversaries, num_obstacles)
        super().__init__(scenario, world, max_cycles, continuous_actions)
        self.metadata['name'] = "simple_tag_v2"


env = make_env(raw_env)
parallel_env = parallel_wrapper_fn(env)
