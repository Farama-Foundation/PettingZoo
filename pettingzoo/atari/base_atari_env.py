from pathlib import Path

import gym
import multi_agent_ale_py
import numpy as np
from gym import spaces
from gym.utils import EzPickle, seeding

from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector, wrappers
from pettingzoo.utils.conversions import from_parallel_wrapper, parallel_wrapper_fn
from pettingzoo.utils.env import ParallelEnv

"""
The Atari environments are based off the [Arcade Learning Environment](https://github.com/mgbellemare/Arcade-Learning-Environment). This environment was instrumental in the development of modern reinforcement learning, and so we hope that our [multi-agent version](https://github.com/Farama-Foundation/Multi-Agent-ALE) of it will be useful in the development of multi-agent reinforcement learning.

### Environment Details

The ALE has been studied extensively and a few notable problems have been identified:

* **Determinism**: The Atari console is deterministic, and so agents can theoretically memorize precise sequences of actions that will maximize the end score. This is not ideal, so we encourage the use of [SuperSuit's](https://github.com/Farama-Foundation/SuperSuit) `sticky_actions` wrapper (example below). This is the recommended approach of  *"Machado et al. (2018), "Revisiting the Arcade Learning Environment: Evaluation Protocols and Open Problems for General Agents"*
* **Frame flickering**: Atari games often do not render every sprite every frame due to hardware restrictions. Instead, sprites (such as the knights in Joust) are sometimes rendered every other frame or even (in Wizard of Wor) every 3 frames. The standard way of handling this computing the pixel-wise maximum of the previous 2 observations (see example below for implementation).

### Common Parameters

All the Atari environments have the following environment parameters:

```
<atari_game>.env(obs_type='rgb_image', full_action_space=True, max_cycles=100000, auto_rom_install_path=None)
```

`obs_type`:  There are three possible values for this parameter:

* 'rgb_image' (default) - produces an RGB image like you would see as a human player.
* 'grayscale_image' - produces a grayscale image.
* 'ram' - produces an observation of the 1024 bits that comprise the RAM of the Atari console.

`full_action_space`:  the effective action space of the Atari games is often smaller than the full space of 18 moves. Setting this to `False` shrinks the available action space to that smaller space.

`max_cycles`:  the number of frames (the number of steps that each agent can take) until game terminates.

`auto_rom_install_path`: The path to your AutoROM installation, installed
with the [Farama-Foundation/AutoROM](https://github.com/Farama-Foundation/AutoROM) tool.
This is the path you specified when installing AutoROM. For example, if
you're using the boxing Atari environment, then the library will look for
the rom at
`/auto_rom_install_path/ROM/boxing/boxing.bin`.
If this is not specified (has value `None`), then the library looks for roms
installed at the default AutoROM path.
"""

def base_env_wrapper_fn(raw_env_fn):
    def env_fn(**kwargs):
        env = raw_env_fn(**kwargs)
        env = wrappers.AssertOutOfBoundsWrapper(env)
        env = wrappers.OrderEnforcingWrapper(env)
        return env
    return env_fn


def BaseAtariEnv(**kwargs):
    return from_parallel_wrapper(ParallelAtariEnv(**kwargs))


class ParallelAtariEnv(ParallelEnv, EzPickle):
    def __init__(
            self,
            game,
            num_players,
            mode_num=None,
            seed=None,
            obs_type='rgb_image',
            full_action_space=True,
            env_name=None,
            max_cycles=100000,
            auto_rom_install_path=None):
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
            env_name,
            max_cycles,
            auto_rom_install_path,
        )

        assert obs_type in ('ram', 'rgb_image', "grayscale_image"), "obs_type must  either be 'ram' or 'rgb_image' or 'grayscale_image'"
        self.obs_type = obs_type
        self.full_action_space = full_action_space
        self.num_players = num_players
        self.max_cycles = max_cycles
        if env_name is None:
            env_name = "custom_" + game
        self.metadata = {'render.modes': ['human', 'rgb_array'], 'name': env_name}

        multi_agent_ale_py.ALEInterface.setLoggerMode("error")
        self.ale = multi_agent_ale_py.ALEInterface()

        self.ale.setFloat(b'repeat_action_probability', 0.)

        if auto_rom_install_path is None:
            start = Path(multi_agent_ale_py.__file__).parent
        else:
            start = Path(auto_rom_install_path).resolve()

        # start looking in local directory
        final = start / f"{game}.bin"
        if not final.exists():
            # if that doesn't work, look in 'roms'
            final = start / "roms" / f"{game}.bin"

        if not final.exists():
            # use old AutoROM install path as backup
            final = start / "ROM" / game / f"{game}.bin"

        if not final.exists():
            raise OSError(f"rom {game} is not installed. Please install roms using AutoROM tool (https://github.com/Farama-Foundation/AutoROM) "
                          "or specify and double-check the path to your Atari rom using the `rom_path` argument.")

        self.rom_path = str(final)
        self.ale.loadROM(self.rom_path)

        all_modes = self.ale.getAvailableModes(num_players)

        if mode_num is None:
            mode = all_modes[0]
        else:
            mode = mode_num
            assert mode in all_modes, f"mode_num parameter is wrong. Mode {mode_num} selected, only {list(all_modes)} modes are supported"

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

        player_names = ["first", "second", "third", "fourth"]
        self.agents = [f"{player_names[n]}_0" for n in range(num_players)]
        self.possible_agents = self.agents[:]

        self.action_spaces = {agent: gym.spaces.Discrete(action_size) for agent in self.possible_agents}
        self.observation_spaces = {agent: observation_space for agent in self.possible_agents}

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
        self.agents = self.possible_agents[:]
        self.dones = {agent: False for agent in self.possible_agents}
        self.frame = 0

        obs = self._observe()
        return {agent: obs for agent in self.agents}

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    def _observe(self):
        if self.obs_type == 'ram':
            bytes = self.ale.getRAM()
            return bytes
        elif self.obs_type == 'rgb_image':
            return self.ale.getScreenRGB()
        elif self.obs_type == 'grayscale_image':
            return self.ale.getScreenGrayscale()

    def step(self, action_dict):
        actions = np.zeros(self.max_num_agents, dtype=np.int32)
        for i, agent in enumerate(self.possible_agents):
            if agent in action_dict:
                actions[i] = action_dict[agent]

        actions = self.action_mapping[actions]
        rewards = self.ale.act(actions)
        self.frame += 1
        if self.ale.game_over() or self.frame >= self.max_cycles:
            dones = {agent: True for agent in self.agents}
        else:
            lives = self.ale.allLives()
            # an inactive agent in ale gets a -1 life.
            dones = {agent: int(life) < 0 for agent, life in zip(self.possible_agents, lives) if agent in self.agents}

        obs = self._observe()
        observations = {agent: obs for agent in self.agents}
        rewards = {agent: rew for agent, rew in zip(self.possible_agents, rewards) if agent in self.agents}
        infos = {agent: {} for agent in self.possible_agents if agent in self.agents}
        self.agents = [agent for agent in self.agents if not dones[agent]]
        return observations, rewards, dones, infos

    def render(self, mode="human"):
        (screen_width, screen_height) = self.ale.getScreenDims()
        image = self.ale.getScreenRGB()
        if mode == "human":
            import os
            os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
            import pygame
            zoom_factor = 4
            if self._screen is None:
                pygame.init()
                self._screen = pygame.display.set_mode((screen_width * zoom_factor, screen_height * zoom_factor))

            myImage = pygame.image.fromstring(image.tobytes(), image.shape[:2][::-1], "RGB")

            myImage = pygame.transform.scale(myImage, (screen_width * zoom_factor, screen_height * zoom_factor))

            self._screen.blit(myImage, (0, 0))

            pygame.display.flip()
        elif mode == "rgb_array":
            return image
        else:
            raise ValueError("bad value for render mode")

    def close(self):
        if self._screen is not None:
            import pygame
            pygame.quit()
            self._screen = None

    def clone_state(self):
        """Clone emulator state w/o system state. Restoring this state will
        *not* give an identical environment. For complete cloning and restoring
        of the full state, see `{clone,restore}_full_state()`."""
        state_ref = self.ale.cloneState()
        state = self.ale.encodeState(state_ref)
        self.ale.deleteState(state_ref)
        return state

    def restore_state(self, state):
        """Restore emulator state w/o system state."""
        state_ref = self.ale.decodeState(state)
        self.ale.restoreState(state_ref)
        self.ale.deleteState(state_ref)

    def clone_full_state(self):
        """Clone emulator state w/ system state including pseudorandomness.
        Restoring this state will give an identical environment."""
        state_ref = self.ale.cloneSystemState()
        state = self.ale.encodeState(state_ref)
        self.ale.deleteState(state_ref)
        return state

    def restore_full_state(self, state):
        """Restore emulator state w/ system state including pseudorandomness."""
        state_ref = self.ale.decodeState(state)
        self.ale.restoreSystemState(state_ref)
        self.ale.deleteState(state_ref)
