from gym.spaces import Discrete, Box
import numpy as np
import warnings
import magent
from pettingzoo import AECEnv
import math
from pettingzoo.magent.render import Renderer
from pettingzoo.utils import agent_selector, wrappers
from gym.utils import seeding
from pettingzoo.utils.env import ParallelEnv


def make_env(raw_env):
    def env_fn(**kwargs):
        env = raw_env(**kwargs)
        env = wrappers.AssertOutOfBoundsWrapper(env)
        backup_policy = "taking zero action (no movement, no attack)"
        env = wrappers.NanNoOpWrapper(env, 0, backup_policy)
        env = wrappers.OrderEnforcingWrapper(env)
        return env
    return env_fn


class magent_parallel_env(ParallelEnv):
    def __init__(self, env, active_handles, names, map_size, max_frames):
        self.map_size = map_size
        self.max_frames = max_frames
        self.env = env
        self.handles = active_handles
        env.reset()
        self.generate_map()

        self.team_sizes = team_sizes = [env.get_num(handle) for handle in self.handles]
        self.agents = [f"{names[j]}_{i}" for j in range(len(team_sizes)) for i in range(team_sizes[j])]
        self.num_agents = sum(team_sizes)

        num_actions = [env.get_action_space(handle)[0] for handle in self.handles]
        action_spaces_list = [Discrete(num_actions[j]) for j in range(len(team_sizes)) for i in range(team_sizes[j])]
        # may change depending on environment config? Not sure.
        team_obs_shapes = self._calc_obs_shapes()
        observation_space_list = [Box(low=0., high=2., shape=team_obs_shapes[j], dtype=np.float32) for j in range(len(team_sizes)) for i in range(team_sizes[j])]

        self.action_spaces = {agent: space for agent, space in zip(self.agents, action_spaces_list)}
        self.observation_spaces = {agent: space for agent, space in zip(self.agents, observation_space_list)}
        self._zero_obs = {agent: np.zeros_like(space.low) for agent, space in self.observation_spaces.items()}
        self._renderer = None
        self.frames = 0

    def seed(self, seed=None):
        if seed is None:
            seed = seeding.create_seed(seed, max_bytes=4)
        self.env.set_seed(seed)

    def _calc_obs_shapes(self):
        view_spaces = [self.env.get_view_space(handle) for handle in self.handles]
        feature_spaces = [self.env.get_feature_space(handle) for handle in self.handles]
        assert all(len(tup) == 3 for tup in view_spaces)
        assert all(len(tup) == 1 for tup in feature_spaces)
        obs_spaces = [(view_space[:2] + (view_space[2] + feature_space[0],)) for view_space, feature_space in zip(view_spaces, feature_spaces)]
        return obs_spaces

    def render(self):
        if self._renderer is None:
            self._renderer = Renderer(self.env, self.map_size)
        self._renderer.render()

    def close(self):
        import pygame
        pygame.quit()

    def reset(self):
        self.env.reset()
        self.frames = 0
        self.generate_map()
        return self._observe_all()

    def _observe_all(self):
        observes = [None] * self.num_agents
        for handle in self.handles:
            ids = self.env.get_agent_id(handle)
            view, features = self.env.get_observation(handle)

            feat_reshape = np.expand_dims(np.expand_dims(features, 1), 1)
            feat_img = np.tile(feat_reshape, (1, view.shape[1], view.shape[2], 1))
            fin_obs = np.concatenate([view, feat_img], axis=-1)
            for id, obs in zip(ids, fin_obs):
                observes[id] = obs

        return {agent: obs if obs is not None else self._zero_obs[agent] for agent, obs in zip(self.agents, observes)}

    def _all_rewards(self):
        rewards = np.zeros(self.num_agents)
        for handle in self.handles:
            ids = self.env.get_agent_id(handle)
            rewards[ids] = self.env.get_reward(handle)
        return {agent: float(rew) for agent, rew in zip(self.agents, rewards)}

    def _all_dones(self, step_done=False):
        dones = np.ones(self.num_agents, dtype=np.bool)
        if not step_done:
            for handle in self.handles:
                ids = self.env.get_agent_id(handle)
                dones[ids] = ~self.env.get_alive(handle)
        return {agent: bool(done) for agent, done in zip(self.agents, dones)}

    def step(self, all_actions):
        action_list = [0] * self.num_agents
        for i, agent in enumerate(self.agents):
            if agent in all_actions:
                action_list[i] = all_actions[agent]
        all_actions = np.asarray(action_list, dtype=np.int32)
        start_point = 0
        for i in range(len(self.handles)):
            size = self.team_sizes[i]
            self.env.set_action(self.handles[i], all_actions[start_point:(start_point + size)])
            start_point += size

        done = self.env.step() or self.frames >= self.max_frames

        all_infos = {agent: {} for agent in self.agents}
        result = self._observe_all(), self._all_rewards(), self._all_dones(done), all_infos
        self.env.clear_dead()

        self.frames += 1
        return result
