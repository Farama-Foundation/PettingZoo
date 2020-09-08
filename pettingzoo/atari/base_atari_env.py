import multi_agent_ale_py
import os
from pettingzoo import AECEnv
import gym
from gym.utils import seeding, EzPickle
from pettingzoo.utils import agent_selector, wrappers
from gym import spaces
import numpy as np
from pettingzoo.utils._parallel_env import _parallel_env_wrapper
from pettingzoo.utils.to_parallel import parallel_wrapper_fn
from pettingzoo.utils.env import ParallelEnv


def base_env_wrapper_fn(raw_env_fn):
    def env_fn(**kwargs):
        env = raw_env_fn(**kwargs)
        env = wrappers.AssertOutOfBoundsWrapper(env)
        env = wrappers.NanNoOpWrapper(env, 0, "doing nothing")
        env = wrappers.OrderEnforcingWrapper(env)
        return env
    return env_fn


def BaseAtariEnv(**kwargs):
    return _parallel_env_wrapper(ParallelAtariEnv(**kwargs))


class ParallelAtariEnv(ParallelEnv, EzPickle):

    metadata = {'render.modes': ['human']}

    def __init__(
            self,
            game,
            num_players,
            mode_num=None,
            seed=None,
            obs_type='rgb_image',
            full_action_space=True,
            max_frames=100000):
        """Frameskip should be either a tuple (indicating a random range to
        choose from, with the top value exclude), or an int."""
        EzPickle.__init__(
            self,
            game,
            num_players,
            mode_num,
            seed,
            obs_type,
            full_action_space,
            max_frames
        )

        assert obs_type in ('ram', 'rgb_image', "grayscale_image"), "obs_type must  either be 'ram' or 'rgb_image' or 'grayscale_image'"
        self.obs_type = obs_type
        self.full_action_space = full_action_space
        self.num_players = num_players
        self.max_frames = max_frames

        multi_agent_ale_py.ALEInterface.setLoggerMode("error")
        self.ale = multi_agent_ale_py.ALEInterface()

        self.ale.setFloat(b'repeat_action_probability', 0.)

        pathstart = os.path.dirname(multi_agent_ale_py.__file__)
        final_path = os.path.join(pathstart, "ROM", game, game + ".bin")
        if not os.path.exists(final_path):
            raise IOError("rom {} is not installed. Please install roms using AutoROM tool (https://github.com/PettingZoo-Team/AutoROM)".format(game))

        self.rom_path = final_path
        self.ale.loadROM(self.rom_path)

        all_modes = self.ale.getAvailableModes(num_players)

        if mode_num is None:
            mode = all_modes[0]
        else:
            mode = mode_num
            assert mode in all_modes, "mode_num parameter is wrong. Mode {} selected, only {} modes are supported".format(mode_num, str(list(all_modes)))

        self.mode = mode
        self.ale.setMode(self.mode)
        assert num_players == self.ale.numPlayersActive()

        if full_action_space:
            action_size = 18
            action_mapping = np.arange(action_size)
        else:
            action_mapping = self.ale.getMinimalActionSet()
            action_size = len(action_mapping)

        self.action_mapping = action_mapping

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
        player_names = ["first", "second", "third", "fourth"]
        self.agents = [f"{player_names[n]}_0" for n in range(self.num_agents)]

        self.action_spaces = {agent: gym.spaces.Discrete(action_size) for agent in self.agents}
        self.observation_spaces = {agent: observation_space for agent in self.agents}

        self._screen = None
        self.seed(seed)

    def seed(self, seed=None):
        if seed is None:
            seed = seeding.create_seed(seed, max_bytes=4)
        self.ale.setInt(b"random_seed", seed)
        self.ale.loadROM(self.rom_path)
        self.ale.setMode(self.mode)

    def reset(self):
        self.ale.reset_game()
        self.frame = 0

        obs = self._observe()
        return {agent: obs for agent in self.agents}

    def _observe(self):
        if self.obs_type == 'ram':
            bytes = self.ale.getRAM()
            return bytes
        elif self.obs_type == 'rgb_image':
            return self.ale.getScreenRGB()
        elif self.obs_type == 'grayscale_image':
            return self.ale.getScreenGrayscale()

    def step(self, action_dict):
        actions = np.zeros(self.num_agents, dtype=np.int32)
        for i, agent in enumerate(self.agents):
            actions[i] = action_dict[agent]

        actions = self.action_mapping[actions]
        rewards = self.ale.act(actions)
        if self.ale.game_over() or self.frame >= self.max_frames:
            dones = {agent: True for agent in self.agents}
        else:
            lives = self.ale.allLives()
            # an inactive agent in ale gets a -1 life.
            dones = {agent: int(life) < 0 for agent, life in zip(self.agents, lives)}

        self.frame += 1
        obs = self._observe()
        observations = {agent: obs for agent in self.agents}
        rewards = {agent: rew for agent, rew in zip(self.agents, rewards)}
        infos = {agent: {} for agent in self.agents}
        return observations, rewards, dones, infos

    def render(self):
        import pygame
        (screen_width, screen_height) = self.ale.getScreenDims()
        zoom_factor = 4
        if self._screen is None:
            pygame.init()
            self._screen = pygame.display.set_mode((screen_width * zoom_factor, screen_height * zoom_factor))

        image = self.ale.getScreenRGB()

        myImage = pygame.image.fromstring(image.tobytes(), image.shape[:2][::-1], "RGB")

        myImage = pygame.transform.scale(myImage, (screen_width * zoom_factor, screen_height * zoom_factor))

        self._screen.blit(myImage, (0, 0))

        pygame.display.flip()

        return image

    def close(self):
        if self._screen is not None:
            import pygame
            pygame.display.quit()
            self._screen = None
