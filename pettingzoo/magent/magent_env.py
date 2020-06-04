from gym.spaces import Discrete, Box
import numpy as np
import warnings
import magent
from pettingzoo import AECEnv
import math
from pettingzoo.magent.render import Renderer
from pettingzoo.utils import agent_selector


class markov_env:
    def __init__(self, env, map_size=45):
        self.map_size = map_size
        self.env = env
        self.handles = handles = env.get_handles()
        env.reset()
        self.generate_map()

        self.team_sizes = team_sizes = [env.get_num(handle) for handle in self.handles]
        self.agents = [f"team{j}_{i}" for j in range(len(team_sizes)) for i in range(team_sizes[j])]
        self.num_agents = sum(team_sizes)

        num_actions = [env.get_action_space(handle)[0] for handle in self.handles]
        self.action_spaces = [ Discrete(num_actions[j]) for j in range(len(team_sizes)) for i in range(team_sizes[j])]
        # may change depending on environment config? Not sure.
        team_obs_shapes = self._calc_obs_shapes()
        self.observation_spaces = [ Box(low=-500.,high=500.,shape=team_obs_shapes[j],dtype=np.float32) for j in range(len(team_sizes)) for i in range(team_sizes[j])]

        self._renderer = None
        #self._observations_uniform = all(team_obs_shapes[0] == obs_shape for obs_shape in team_obs_shapes)

    def _calc_obs_shapes(self):
        view_spaces = [self.env.get_view_space(handle) for handle in self.handles]
        feature_spaces = [self.env.get_feature_space(handle) for handle in self.handles]
        assert all(len(tup) == 3 for tup in view_spaces)
        assert all(len(tup) == 1 for tup in feature_spaces)
        obs_spaces = [(view_space[:2]+(view_space[2]+feature_space[0],)) for view_space,feature_space in zip(view_spaces, feature_spaces)]
        return obs_spaces

    def render(self):
        if self._renderer is None:
            self._renderer = Renderer(self.env)
        self._renderer.render()

    def close(self):
        pygame.quit()

    def reset(self):
        print("reset")
        self.env.reset()
        self.generate_map()
        return self._observe_all()

    def _observe_all(self):
        observes = []
        for handle in self.handles:
            view,features = self.env.get_observation(handle)

            feat_reshape = np.expand_dims(np.expand_dims(features,1),1)
            feat_img = np.tile(feat_reshape,(1,view.shape[1],view.shape[2],1))
            fin_obs = np.concatenate([view,feat_img],axis=-1)
            split_obs = np.split(fin_obs,len(fin_obs))
            observes += split_obs

        observes = [np.squeeze(arr) for arr in observes]

        return observes

    def _all_rewards(self):
        return np.concatenate([self.env.get_reward(handle) for handle in self.handles],axis=0)

    def _all_dones(self):
        return (~np.concatenate([self.env.get_alive(handle) for handle in self.handles],axis=0)).tolist()

    def step(self, all_actions):
        #print("step")
        all_actions = np.asarray(all_actions,dtype=np.int32)
        assert len(all_actions) == self.num_agents
        start_point = 0
        for i in range(len(self.handles)):
            size = self.team_sizes[i]
            self.env.set_action(self.handles[i], all_actions[start_point:start_point+size])
            start_point += size

        done = self.env.step()
        all_infos = [{}]*self.num_agents
        return self._observe_all(), self._all_rewards(), self._all_dones(), all_infos
