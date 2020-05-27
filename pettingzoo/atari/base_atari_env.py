import multi_agent_ale_py
import os
from pettingzoo.utils import wrappers
from pettingzoo import AECEnv
import gym
from gym.utils import seeding
from pettingzoo.utils import agent_selector, wrappers
from gym import spaces
import numpy as np


def base_env_wrapper_fn(raw_env_fn):
    def env_fn(**kwargs):
        env = raw_env_fn(**kwargs)
        env = wrappers.AssertOutOfBoundsWrapper(env)
        env = wrappers.NanNoOpWrapper(env, 0, "doing nothing")
        env = wrappers.OrderEnforcingWrapper(env)
        return env
    return env_fn


class BaseAtariEnv(AECEnv):

    metadata = {'render.modes': ['human']}

    def __init__(
            self,
            game,
            num_players,
            mode_num=None,
            seed=None,
            obs_type='rgb_image',
            frameskip=4,
            repeat_action_probability=0.25,
            full_action_space=True):
        """Frameskip should be either a tuple (indicating a random range to
        choose from, with the top value exclude), or an int."""

        assert obs_type in ('ram', 'rgb_image', "grayscale_image"), "obs_type must  either be 'ram' or 'rgb_image' or 'grayscale_image'"
        self.obs_type = obs_type
        self.full_action_space = full_action_space
        self.num_players = num_players
        self.np_random = seeding.np_random(seed)

        self.ale = multi_agent_ale_py.ALEInterface()

        if seed is None:
            seed = seeding.create_seed(seed, max_bytes=4)

        self.ale.setInt(b"random_seed", seed)
        self.ale.setInt(b"frame_skip", frameskip)
        self.ale.setFloat(b'repeat_action_probability', repeat_action_probability)

        pathstart = os.path.dirname(multi_agent_ale_py.__file__)
        final_path = os.path.join(pathstart, "ROM", game, game + ".bin")
        if not os.path.exists(final_path):
            raise IOError("rom {} is not installed. Please install roms using AutoROM tool (https://github.com/PettingZoo-Team/AutoROM)".format(game))

        self.ale.loadROM(final_path)

        all_modes = self.ale.getAvailableModes(num_players)

        if mode_num is None:
            mode = all_modes[0]
        else:
            mode = mode_num
            assert mode in all_modes, "mode_num parameter is wrong. Mode {} selected, only {} modes are supported".format(mode_num, str(list(all_modes)))

        self.ale.setMode(mode)
        assert num_players == self.ale.numPlayersActive()

        if full_action_space:
            action_size = 18
        else:
            action_size = len(self.ale.getMinimalActionSet())

        if obs_type == 'ram':
            observation_space = gym.spaces.Box(low=0, high=255, dtype=np.uint8, shape=(128,))
        else:
            (screen_width, screen_height) = self.ale.getScreenDims()
            if obs_type == 'rgb_image':
                num_channels = 3
            elif obs_type == 'grayscale_image':
                num_channels = 1
            observation_space = spaces.Box(low=0, high=255, shape=(screen_height, screen_width, num_channels), dtype=np.uint8)

        self.num_agents = num_players
        player_names = ["first","second","third","fourth"]
        self.agents = [f"{player_names[n]}_0" for n in range(self.num_agents)]
        self.agent_order = list(self.agents)

        self.action_spaces = {agent: gym.spaces.Discrete(action_size) for agent in self.agents}
        self.observation_spaces =  {agent: observation_space for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}

        self._agent_selector = agent_selector(self.agent_order)

        self._screen = None

    def reset(self, observe=True):
        self.ale.reset_game()
        self.agent_selection = self._agent_selector.reset()

        self.rewards = {a: 0 for a in self.agents}
        self.dones = {a: False for a in self.agents}
        self.infos = {a: {} for a in self.agents}

        self._actions = []

        return self.observe(self.agent_selection) if observe else None

    def observe(self, agent):
        if self.obs_type == 'ram':
            bytes = self.ale.getRAM()
            return bytes
        elif self.obs_type == 'rgb_image':
            return self.ale.getScreenRGB()
        elif self.obs_type == 'grayscale_image':
            return self.ale.getScreenGrayscale()

    def step(self, action, observe=True):
        self._actions.append(action)
        if len(self._actions) == self.num_players:
            rewards = self.ale.act(self._actions)
            self.rewards = {a: rew for a, rew in zip(self.agents, rewards)}
            if self.ale.game_over():
                self.dones = {a: True for a in self.agents}
            self._actions = []

        self.agent_selection = self._agent_selector.next()

        return self.observe(self.agent_selection) if observe else None

    def render(self, mode='human'):
        import pygame
        (screen_width, screen_height) = self.ale.getScreenDims()
        zoom_factor = 4
        if self._screen is None:
            pygame.init()
            self._screen = pygame.display.set_mode((screen_width*zoom_factor, screen_height*zoom_factor))

        image = self.ale.getScreenRGB()

        myImage = pygame.image.fromstring(image.tobytes(), image.shape[:2][::-1], "RGB")

        myImage = pygame.transform.scale(myImage,(screen_width*zoom_factor, screen_height*zoom_factor))

        self._screen.blit(myImage, (0, 0))

        pygame.display.flip()

        return image

    def close(self):
        pygame.display.quit()
        self._screen = None
