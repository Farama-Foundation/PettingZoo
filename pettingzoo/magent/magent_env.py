import math
import warnings

import magent
import numpy as np
from gym.spaces import Box, Discrete
from gym.utils import seeding

from pettingzoo import AECEnv
from pettingzoo.magent.render import Renderer
from pettingzoo.utils import agent_selector, wrappers
from pettingzoo.utils.env import ParallelEnv


def make_env(raw_env):
    def env_fn(**kwargs):
        env = raw_env(**kwargs)
        env = wrappers.AssertOutOfBoundsWrapper(env)
        env = wrappers.OrderEnforcingWrapper(env)
        return env
    return env_fn


class magent_parallel_env(ParallelEnv):
    def __init__(self, env, active_handles, names, map_size, max_cycles, reward_range, minimap_mode, extra_features):
        self.map_size = map_size
        self.max_cycles = max_cycles
        self.minimap_mode = minimap_mode
        self.extra_features = extra_features
        self.env = env
        self.handles = active_handles
        self._all_handles = self.env.get_handles()
        env.reset()
        self.generate_map()
        self.team_sizes = team_sizes = [env.get_num(handle) for handle in self.handles]
        self.agents = [f"{names[j]}_{i}" for j in range(len(team_sizes)) for i in range(team_sizes[j])]
        self.possible_agents = self.agents[:]

        num_actions = [env.get_action_space(handle)[0] for handle in self.handles]
        action_spaces_list = [Discrete(num_actions[j]) for j in range(len(team_sizes)) for i in range(team_sizes[j])]
        # may change depending on environment config? Not sure.
        team_obs_shapes = self._calc_obs_shapes()
        state_shape = self._calc_state_shape()
        observation_space_list = [Box(low=0., high=2., shape=team_obs_shapes[j], dtype=np.float32) for j in range(len(team_sizes)) for i in range(team_sizes[j])]

        self.state_space = Box(low=0., high=2., shape=state_shape, dtype=np.float32)
        reward_low, reward_high = reward_range

        if extra_features:
            for space in observation_space_list:
                idx = space.shape[2] - 3 if minimap_mode else space.shape[2] - 1
                space.low[:, :, idx] = reward_low
                space.high[:, :, idx] = reward_high
            idx_state = self.state_space.shape[2] - 3 if minimap_mode else self.state_space.shape[2] - 1
            self.state_space.low[:, :, idx_state] = reward_low
            self.state_space.high[:, :, idx_state] = reward_high

        self.action_spaces = {agent: space for agent, space in zip(self.agents, action_spaces_list)}
        self.observation_spaces = {agent: space for agent, space in zip(self.agents, observation_space_list)}

        self._zero_obs = {agent: np.zeros_like(space.low) for agent, space in self.observation_spaces.items()}
        self.base_state = np.zeros(self.state_space.shape, dtype='float32')
        walls = self.env._get_walls_info()
        wall_x, wall_y = zip(*walls)
        self.base_state[wall_x, wall_y, 0] = 1
        self._renderer = None
        self.frames = 0

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    def seed(self, seed=None):
        if seed is None:
            seed = seeding.create_seed(seed, max_bytes=4)
        self.env.set_seed(seed)

    def _calc_obs_shapes(self):
        view_spaces = [self.env.get_view_space(handle) for handle in self.handles]
        feature_spaces = [self.env.get_feature_space(handle) for handle in self.handles]
        assert all(len(tup) == 3 for tup in view_spaces)
        assert all(len(tup) == 1 for tup in feature_spaces)
        feat_size = [[fs[0]] for fs in feature_spaces]
        for feature_space in feat_size:
            if not self.extra_features:
                feature_space[0] = 2 if self.minimap_mode else 0
        obs_spaces = [(view_space[:2] + (view_space[2] + feature_space[0],)) for view_space, feature_space in zip(view_spaces, feat_size)]
        return obs_spaces

    def _calc_state_shape(self):
        feature_spaces = [
            self.env.get_feature_space(handle) for handle in self._all_handles
        ]
        self._minimap_features = 2 if self.minimap_mode else 0
        # map channel and agent pair channel. Remove global agent position when minimap mode and extra features
        state_depth = (
            (max(feature_spaces)[0] - self._minimap_features) * self.extra_features
            + 1
            + len(self._all_handles) * 2
        )

        return (self.map_size, self.map_size, state_depth)

    def render(self, mode="human"):
        if self._renderer is None:
            self._renderer = Renderer(self.env, self.map_size, mode)
        assert mode == self._renderer.mode, "mode must be consistent across render calls"
        return self._renderer.render(mode)

    def close(self):
        if self._renderer is not None:
            self._renderer.close()
            self._renderer = None

    def reset(self):
        self.agents = self.possible_agents[:]
        self.env.reset()
        self.frames = 0
        self.all_dones = {agent: False for agent in self.possible_agents}
        self.generate_map()
        return self._observe_all()

    def _observe_all(self):
        observes = [None] * self.max_num_agents
        for handle in self.handles:
            ids = self.env.get_agent_id(handle)
            view, features = self.env.get_observation(handle)

            if self.minimap_mode and not self.extra_features:
                features = features[:, -2:]
            if self.minimap_mode or self.extra_features:
                feat_reshape = np.expand_dims(np.expand_dims(features, 1), 1)
                feat_img = np.tile(feat_reshape, (1, view.shape[1], view.shape[2], 1))
                fin_obs = np.concatenate([view, feat_img], axis=-1)
            else:
                fin_obs = np.copy(view)
            for id, obs in zip(ids, fin_obs):
                observes[id] = obs

        ret_agents = set(self.agents)
        return {agent: obs if obs is not None else self._zero_obs[agent] for agent, obs in zip(self.possible_agents, observes) if agent in ret_agents}

    def _all_rewards(self):
        rewards = np.zeros(self.max_num_agents)
        for handle in self.handles:
            ids = self.env.get_agent_id(handle)
            rewards[ids] = self.env.get_reward(handle)
        ret_agents = set(self.agents)
        return {agent: float(rew) for agent, rew in zip(self.possible_agents, rewards) if agent in ret_agents}

    def _all_dones(self, step_done=False):
        dones = np.ones(self.max_num_agents, dtype=bool)
        if not step_done:
            for handle in self.handles:
                ids = self.env.get_agent_id(handle)
                dones[ids] = ~self.env.get_alive(handle)
        ret_agents = set(self.agents)
        return {agent: bool(done) for agent, done in zip(self.possible_agents, dones) if agent in ret_agents}

    def state(self):
        '''
        Returns an observation of the global environment
        '''
        state = np.copy(self.base_state)

        for handle in self._all_handles:
            view, features = self.env.get_observation(handle)

            pos = self.env.get_pos(handle)
            pos_x, pos_y = zip(*pos)
            state[pos_x, pos_y, 1 + handle.value * 2] = 1
            state[pos_x, pos_y, 2 + handle.value * 2] = view[:, view.shape[1] // 2, view.shape[2] // 2, 2]

            if self.extra_features:
                add_zeros = np.zeros(
                    (
                        features.shape[0],
                        state.shape[2]
                        - (1 + len(self.team_sizes) * 2 + features.shape[1] - self._minimap_features),
                    )
                )

                rewards = features[:, -1 - self._minimap_features]
                actions = features[:, :-1 - self._minimap_features]
                actions = np.concatenate((actions, add_zeros), axis=1)
                rewards = rewards.reshape(len(rewards), 1)
                state_features = np.hstack((actions, rewards))

                state[pos_x, pos_y, 1 + len(self.team_sizes) * 2:] = state_features
        return state

    def step(self, all_actions):
        action_list = [0] * self.max_num_agents
        for i, agent in enumerate(self.possible_agents):
            if agent in all_actions:
                action_list[i] = all_actions[agent]
        all_actions = np.asarray(action_list, dtype=np.int32)
        start_point = 0
        for i in range(len(self.handles)):
            size = self.team_sizes[i]
            self.env.set_action(self.handles[i], all_actions[start_point:(start_point + size)])
            start_point += size

        self.frames += 1
        done = self.env.step() or self.frames >= self.max_cycles

        all_infos = {agent: {} for agent in self.agents}
        all_dones = self._all_dones(done)
        all_rewards = self._all_rewards()
        all_observes = self._observe_all()
        self.all_dones = all_dones
        self.env.clear_dead()
        self.agents = [agent for agent in self.agents if not self.all_dones[agent]]
        return all_observes, all_rewards, all_dones, all_infos
