# noqa: D212, D415
"""
# Cooperative Pong

```{figure} butterfly_cooperative_pong.gif
:width: 200px
:name: cooperative_pong
```

This environment is part of the <a href='..'>butterfly environments</a>. Please read that page first for general information.

| Import               | `from pettingzoo.butterfly import cooperative_pong_v5` |
|----------------------|--------------------------------------------------------|
| Actions              | Discrete                                               |
| Parallel API         | Yes                                                    |
| Manual Control       | Yes                                                    |
| Agents               | `agents= ['paddle_0', 'paddle_1']`                     |
| Agents               | 2                                                      |
| Action Shape         | Discrete(3)                                            |
| Action Values        | [0, 1]                                                 |
| Observation Shape    | (280, 480, 3)                                          |
| Observation Values   | [0, 255]                                               |
| State Shape          | (560, 960, 3)                                          |
| State Values         | (0, 255)                                               |


Cooperative pong is a game of simple pong, where the objective is to keep the ball in play for the longest time. The game is over when the ball goes out of bounds from either the left or right edge of the screen. There are two agents (paddles), one that moves along the left edge and the other that
moves along the right edge of the screen. All collisions of the ball are elastic. The ball always starts moving in a random direction from the center of the screen with each reset. To make learning a little more challenging, the right paddle is tiered cake-shaped by default.
The observation space of each agent is its own half of the screen. There are two possible actions for the agents (_move up/down_). If the ball stays within bounds, each agent receives a reward of `max_reward / max_cycles` (default 0.11) at each timestep. Otherwise, each agent receives a reward of
`off_screen_penalty` (default -10) and the game ends.


### Manual Control

Move the left paddle using the 'W' and 'S' keys. Move the right paddle using 'UP' and 'DOWN' arrow keys.

### Arguments

``` python
cooperative_pong_v5.env(ball_speed=9, left_paddle_speed=12,
right_paddle_speed=12, cake_paddle=True, max_cycles=900, bounce_randomness=False, max_reward=100, off_screen_penalty=-10)
```

`ball_speed`: Speed of ball (in pixels)

`left_paddle_speed`: Speed of left paddle (in pixels)

`right_paddle_speed`: Speed of right paddle (in pixels)

`cake_paddle`: If True, the right paddle cakes the shape of a 4 tiered wedding cake

`max_cycles`:  after max_cycles steps all agents will return done

`bounce_randomness`: If True, each collision of the ball with the paddles adds a small random angle to the direction of the ball, with the speed of the ball remaining unchanged.

`max_reward`:  Total reward given to each agent over max_cycles timesteps

`off_screen_penalty`:  Negative reward penalty for each agent if the ball goes off the screen

### Version History

* v5: Fixed ball teleporting bugs
* v4: Added max_reward and off_screen_penalty arguments and changed default, fixed glitch where ball would occasionally teleport, reward redesign (1.14.0)
* v3: Change observation space to include entire screen (1.10.0)
* v2: Misc fixes (1.4.0)
* v1: Fixed bug in how `dones` were computed (1.3.1)
* v0: Initial versions release (1.0.0)

"""

import gymnasium
import numpy as np
import pygame
from gymnasium.utils import EzPickle, seeding

from pettingzoo import AECEnv
from pettingzoo.butterfly.cooperative_pong.ball import Ball
from pettingzoo.butterfly.cooperative_pong.cake_paddle import CakePaddle
from pettingzoo.butterfly.cooperative_pong.manual_policy import ManualPolicy
from pettingzoo.butterfly.cooperative_pong.paddle import Paddle
from pettingzoo.utils import wrappers
from pettingzoo.utils.agent_selector import agent_selector
from pettingzoo.utils.conversions import parallel_wrapper_fn

FPS = 15


__all__ = ["ManualPolicy", "env", "raw_env", "parallel_env"]


def deg_to_rad(deg):
    return deg * np.pi / 180


def get_flat_shape(width, height, kernel_window_length=2):
    return int(width * height / (kernel_window_length * kernel_window_length))


def original_obs_shape(screen_width, screen_height, kernel_window_length=2):
    return (
        int(screen_height * 2 / kernel_window_length),
        int(screen_width * 2 / (kernel_window_length)),
        1,
    )


def get_valid_angle(randomizer):
    # generates an angle in [0, 2*np.pi) that
    # excludes (90 +- ver_deg_range), (270 +- ver_deg_range), (0 +- hor_deg_range), (180 +- hor_deg_range)
    # (65, 115), (245, 295), (170, 190), (0, 10), (350, 360)
    ver_deg_range = 25
    hor_deg_range = 10
    a1 = deg_to_rad(90 - ver_deg_range)
    b1 = deg_to_rad(90 + ver_deg_range)
    a2 = deg_to_rad(270 - ver_deg_range)
    b2 = deg_to_rad(270 + ver_deg_range)
    c1 = deg_to_rad(180 - hor_deg_range)
    d1 = deg_to_rad(180 + hor_deg_range)
    c2 = deg_to_rad(360 - hor_deg_range)
    d2 = deg_to_rad(0 + hor_deg_range)

    angle = 0
    while (
        (a1 < angle < b1)
        or (a2 < angle < b2)
        or (c1 < angle < d1)
        or (angle > c2)
        or (angle < d2)
    ):
        angle = 2 * np.pi * randomizer.random()

    return angle


class CooperativePong:
    def __init__(
        self,
        randomizer,
        ball_speed=9,
        left_paddle_speed=12,
        right_paddle_speed=12,
        cake_paddle=True,
        max_cycles=900,
        bounce_randomness=False,
        max_reward=100,
        off_screen_penalty=-10,
        render_mode=None,
        render_ratio=2,
        kernel_window_length=2,
        render_fps=15,
    ):
        super().__init__()

        pygame.init()
        self.num_agents = 2

        self.render_ratio = render_ratio
        self.kernel_window_length = kernel_window_length

        # Display screen
        self.s_width, self.s_height = 960 // render_ratio, 560 // render_ratio
        self.area = pygame.Rect(0, 0, self.s_width, self.s_height)
        self.max_reward = max_reward
        self.off_screen_penalty = off_screen_penalty

        # define action and observation spaces
        self.action_space = [
            gymnasium.spaces.Discrete(3) for _ in range(self.num_agents)
        ]
        original_shape = original_obs_shape(
            self.s_width, self.s_height, kernel_window_length=kernel_window_length
        )
        original_color_shape = (original_shape[0], original_shape[1], 3)
        self.observation_space = [
            gymnasium.spaces.Box(
                low=0, high=255, shape=(original_color_shape), dtype=np.uint8
            )
            for _ in range(self.num_agents)
        ]
        # define the global space of the environment or state
        self.state_space = gymnasium.spaces.Box(
            low=0, high=255, shape=((self.s_height, self.s_width, 3)), dtype=np.uint8
        )

        self.render_mode = render_mode
        self.screen = None

        # set speed
        self.speed = [ball_speed, left_paddle_speed, right_paddle_speed]

        self.max_cycles = max_cycles

        # paddles
        self.p0 = Paddle((20 // render_ratio, 80 // render_ratio), left_paddle_speed)
        if cake_paddle:
            self.p1 = CakePaddle(right_paddle_speed, render_ratio=render_ratio)
        else:
            self.p1 = Paddle(
                (20 // render_ratio, 100 // render_ratio), right_paddle_speed
            )

        self.agents = ["paddle_0", "paddle_1"]  # list(range(self.num_agents))

        # ball
        self.ball = Ball(
            randomizer,
            (20 // render_ratio, 20 // render_ratio),
            ball_speed,
            bounce_randomness,
        )
        self.randomizer = randomizer

        self.reinit()

        self.render_fps = render_fps
        if self.render_mode == "human":
            self.clock = pygame.time.Clock()

    def reinit(self):
        self.rewards = dict(zip(self.agents, [0.0] * len(self.agents)))
        self.terminations = dict(zip(self.agents, [False] * len(self.agents)))
        self.truncations = dict(zip(self.agents, [False] * len(self.agents)))
        self.infos = dict(zip(self.agents, [{}] * len(self.agents)))
        self.score = 0

    def reset(self, seed=None, options=None):
        # reset ball and paddle init conditions
        self.ball.rect.center = self.area.center
        # set the direction to an angle between [0, 2*np.pi)
        angle = get_valid_angle(self.randomizer)
        # angle = deg_to_rad(89)
        self.ball.speed = [
            int(self.ball.speed_val * np.cos(angle)),
            int(self.ball.speed_val * np.sin(angle)),
        ]

        self.p0.rect.midleft = self.area.midleft
        self.p1.rect.midright = self.area.midright
        self.p0.reset()
        self.p1.reset()
        self.p0.speed = self.speed[1]
        self.p1.speed = self.speed[2]

        self.terminate = False
        self.truncate = False

        self.num_frames = 0

        self.reinit()

        # Pygame surface required even for render_mode == None, as observations are taken from pixel values
        # Observe
        if self.render_mode != "human":
            self.screen = pygame.Surface((self.s_width, self.s_height))

        self.render()

    def close(self):
        if self.screen is not None:
            pygame.quit()
            self.screen = None

    def render(self):
        if self.render_mode is None:
            gymnasium.logger.warn(
                "You are calling render method without specifying any render mode."
            )
            return

        if self.screen is None:
            if self.render_mode == "human":
                self.screen = pygame.display.set_mode((self.s_width, self.s_height))
                pygame.display.set_caption("Cooperative Pong")
        self.draw()

        observation = np.array(pygame.surfarray.pixels3d(self.screen))
        if self.render_mode == "human":
            pygame.display.flip()
            self.clock.tick(self.render_fps)
        return (
            np.transpose(observation, axes=(1, 0, 2))
            if self.render_mode == "rgb_array"
            else None
        )

    def observe(self):
        observation = np.array(pygame.surfarray.pixels3d(self.screen))
        observation = np.rot90(
            observation, k=3
        )  # now the obs is laid out as H, W as rows and cols
        observation = np.fliplr(observation)  # laid out in the correct order
        return observation

    def state(self):
        """Returns an observation of the global environment."""
        state = pygame.surfarray.pixels3d(self.screen).copy()
        state = np.rot90(state, k=3)
        state = np.fliplr(state)
        return state

    def draw(self):
        pygame.draw.rect(self.screen, (0, 0, 0), self.area)
        self.p0.draw(self.screen)
        self.p1.draw(self.screen)
        self.ball.draw(self.screen)

    def step(self, action, agent):
        # update p0, p1 accordingly
        # action: 0: do nothing,
        # action: 1: p[i] move up
        # action: 2: p[i] move down
        if agent == self.agents[0]:
            self.rewards = {a: 0 for a in self.agents}
            self.p0.update(self.area, action)
        elif agent == self.agents[1]:
            self.p1.update(self.area, action)

            # do the rest if not terminated
            if not self.terminate:
                # update ball position
                self.terminate = self.ball.update2(self.area, self.p0, self.p1)

                # do the miscellaneous stuff after the last agent has moved
                # reward is the length of time ball is in play
                reward = 0
                # ball is out-of-bounds
                if self.terminate:
                    reward = self.off_screen_penalty
                    self.score += reward
                if not self.terminate:
                    self.num_frames += 1
                    reward = self.max_reward / self.max_cycles
                    self.score += reward
                    self.truncate = self.num_frames >= self.max_cycles

                for ag in self.agents:
                    self.rewards[ag] = reward
                    self.terminations[ag] = self.terminate
                    self.truncations[ag] = self.truncate
                    self.infos[ag] = {}

        self.render()


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


parallel_env = parallel_wrapper_fn(env)


class raw_env(AECEnv, EzPickle):
    # class env(MultiAgentEnv):
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "name": "cooperative_pong_v5",
        "is_parallelizable": True,
        "render_fps": FPS,
        "has_manual_policy": True,
    }

    def __init__(self, **kwargs):
        EzPickle.__init__(self, **kwargs)
        self._kwargs = kwargs

        self._seed()

        self.agents = self.env.agents[:]
        self.possible_agents = self.agents[:]
        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.reset()
        # spaces
        self.action_spaces = dict(zip(self.agents, self.env.action_space))
        self.observation_spaces = dict(zip(self.agents, self.env.observation_space))
        self.state_space = self.env.state_space
        # dicts
        self.observations = {}
        self.rewards = self.env.rewards
        self.terminations = self.env.terminations
        self.truncations = self.env.truncations
        self.infos = self.env.infos

        self.score = self.env.score

        self.render_mode = self.env.render_mode
        self.screen = None

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    # def convert_to_dict(self, list_of_list):
    #     return dict(zip(self.agents, list_of_list))

    def _seed(self, seed=None):
        self.randomizer, seed = seeding.np_random(seed)
        self.env = CooperativePong(self.randomizer, **self._kwargs)

    def reset(self, seed=None, options=None):
        if seed is not None:
            self._seed(seed=seed)
        self.env.reset()
        self.agents = self.possible_agents[:]
        self.agent_selection = self._agent_selector.reset()
        self.rewards = self.env.rewards
        self._cumulative_rewards = {a: 0 for a in self.agents}
        self.terminations = self.env.terminations
        self.truncations = self.env.truncations
        self.infos = self.env.infos

    def observe(self, agent):
        obs = self.env.observe()
        return obs

    def state(self):
        state = self.env.state()
        return state

    def close(self):
        self.env.close()

    def render(self):
        return self.env.render()

    def step(self, action):
        if (
            self.terminations[self.agent_selection]
            or self.truncations[self.agent_selection]
        ):
            self._was_dead_step(action)
            return
        agent = self.agent_selection
        if not self.action_spaces[agent].contains(action):
            raise Exception(
                "Action for agent {} must be in Discrete({})."
                "It is currently {}".format(agent, self.action_spaces[agent].n, action)
            )

        self.env.step(action, agent)
        # select next agent and observe
        self.agent_selection = self._agent_selector.next()
        self.rewards = self.env.rewards
        self.terminations = self.env.terminations
        self.truncations = self.env.truncations
        self.infos = self.env.infos

        self.score = self.env.score

        self._cumulative_rewards[agent] = 0
        self._accumulate_rewards()


# This was originally created, in full, by Ananth Hari in a different repo, and was
# added in by J K Terry (which is why they're shown as the creator in the git history)
