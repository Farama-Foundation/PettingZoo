import os

import gym
import numpy as np
import pygame
from gym.utils import EzPickle, seeding

from pettingzoo import AECEnv
from pettingzoo.utils import wrappers
from pettingzoo.utils.agent_selector import agent_selector
from pettingzoo.utils.conversions import parallel_wrapper_fn

from .ball import Ball
from .cake_paddle import CakePaddle
from .paddle import Paddle

FPS = 15


def deg_to_rad(deg):
    return deg * np.pi / 180


def get_flat_shape(width, height, kernel_window_length=2):
    return int(width * height / (kernel_window_length * kernel_window_length))


def original_obs_shape(screen_width, screen_height, kernel_window_length=2):
    return (int(screen_height * 2 / kernel_window_length), int(screen_width * 2 / (kernel_window_length)), 1)


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
    while ((angle > a1 and angle < b1) or (angle > a2 and angle < b2) or (angle > c1 and angle < d1) or (angle > c2) or (angle < d2)):
        angle = 2 * np.pi * randomizer.rand()

    return angle


class CooperativePong:
    def __init__(self, randomizer, ball_speed=9, left_paddle_speed=12, right_paddle_speed=12, cake_paddle=True, max_cycles=900, bounce_randomness=False, max_reward=100, off_screen_penalty=-10, render_ratio=2, kernel_window_length=2):
        super().__init__()

        pygame.init()
        self.num_agents = 2

        self.render_ratio = render_ratio
        self.kernel_window_length = kernel_window_length

        # Display screen
        self.s_width, self.s_height = 960 // render_ratio, 560 // render_ratio
        self.screen = pygame.Surface((self.s_width, self.s_height))  # (960, 720) # (640, 480) # (100, 200)
        self.area = self.screen.get_rect()
        self.max_reward = max_reward
        self.off_screen_penalty = off_screen_penalty

        # define action and observation spaces
        self.action_space = [gym.spaces.Discrete(3) for _ in range(self.num_agents)]
        original_shape = original_obs_shape(self.s_width, self.s_height, kernel_window_length=kernel_window_length)
        original_color_shape = (original_shape[0], original_shape[1], 3)
        self.observation_space = [gym.spaces.Box(low=0, high=255, shape=(original_color_shape), dtype=np.uint8) for _ in range(self.num_agents)]
        # define the global space of the environment or state
        self.state_space = gym.spaces.Box(low=0, high=255, shape=((self.s_height, self.s_width, 3)), dtype=np.uint8)

        self.renderOn = False

        # set speed
        self.speed = [ball_speed, left_paddle_speed, right_paddle_speed]

        self.max_cycles = max_cycles

        # paddles
        self.p0 = Paddle((20 // render_ratio, 80 // render_ratio), left_paddle_speed)
        if cake_paddle:
            self.p1 = CakePaddle(right_paddle_speed, render_ratio=render_ratio)
        else:
            self.p1 = Paddle((20 // render_ratio, 100 // render_ratio), right_paddle_speed)

        self.agents = ["paddle_0", "paddle_1"]  # list(range(self.num_agents))

        # ball
        self.ball = Ball(randomizer, (20 // render_ratio, 20 // render_ratio), ball_speed, bounce_randomness)
        self.randomizer = randomizer

        self.reinit()

    def reinit(self):
        self.rewards = dict(zip(self.agents, [0.0] * len(self.agents)))
        self.dones = dict(zip(self.agents, [False] * len(self.agents)))
        self.infos = dict(zip(self.agents, [{}] * len(self.agents)))
        self.score = 0

    def reset(self):
        # reset ball and paddle init conditions
        self.ball.rect.center = self.area.center
        # set the direction to an angle between [0, 2*np.pi)
        angle = get_valid_angle(self.randomizer)
        # angle = deg_to_rad(89)
        self.ball.speed = [int(self.ball.speed_val * np.cos(angle)), int(self.ball.speed_val * np.sin(angle))]

        self.p0.rect.midleft = self.area.midleft
        self.p1.rect.midright = self.area.midright
        self.p0.reset()
        self.p1.reset()
        self.p0.speed = self.speed[1]
        self.p1.speed = self.speed[2]

        self.done = False

        self.num_frames = 0

        self.reinit()

        self.draw()

    def close(self):
        if self.renderOn:
            pygame.event.pump()
            pygame.display.quit()
            self.renderOn = False

    def enable_render(self):
        self.screen = pygame.display.set_mode(self.screen.get_size())
        self.renderOn = True
        self.draw()

    def render(self, mode='human'):
        if not self.renderOn and mode == "human":
            # sets self.renderOn to true and initializes display
            self.enable_render()

        observation = np.array(pygame.surfarray.pixels3d(self.screen))
        if mode == "human":
            pygame.display.flip()
        return np.transpose(observation, axes=(1, 0, 2)) if mode == "rgb_array" else None

    def observe(self):
        observation = np.array(pygame.surfarray.pixels3d(self.screen))
        observation = np.rot90(observation, k=3)  # now the obs is laid out as H, W as rows and cols
        observation = np.fliplr(observation)  # laid out in the correct order
        return observation

    def state(self):
        '''
        Returns an observation of the global environment
        '''
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

            # do the rest if not done
            if not self.done:
                # update ball position
                self.done = self.ball.update2(self.area, self.p0, self.p1)

                # do the miscellaneous stuff after the last agent has moved
                # reward is the length of time ball is in play
                reward = 0
                # ball is out-of-bounds
                if self.done:
                    reward = self.off_screen_penalty
                    self.score += reward
                if not self.done:
                    self.num_frames += 1
                    reward = self.max_reward / self.max_cycles
                    self.score += reward
                    if self.num_frames == self.max_cycles:
                        self.done = True

                for ag in self.agents:
                    self.rewards[ag] = reward
                    self.dones[ag] = self.done
                    self.infos[ag] = {}

        if self.renderOn:
            pygame.event.pump()
        self.draw()


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


parallel_env = parallel_wrapper_fn(env)


class raw_env(AECEnv, EzPickle):
    # class env(MultiAgentEnv):
    metadata = {
        'render.modes': ['human', "rgb_array"],
        'name': "cooperative_pong_v5",
        'is_parallelizable': True,
        'video.frames_per_second': FPS
    }

    def __init__(self, **kwargs):
        EzPickle.__init__(self, **kwargs)
        self._kwargs = kwargs

        self.seed()

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
        self.dones = self.env.dones
        self.infos = self.env.infos

        self.score = self.env.score

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    # def convert_to_dict(self, list_of_list):
    #     return dict(zip(self.agents, list_of_list))
    def seed(self, seed=None):
        self.randomizer, seed = seeding.np_random(seed)
        self.env = CooperativePong(self.randomizer, **self._kwargs)

    def reset(self):
        self.env.reset()
        self.agents = self.possible_agents[:]
        self.agent_selection = self._agent_selector.reset()
        self.rewards = self.env.rewards
        self._cumulative_rewards = {a: 0 for a in self.agents}
        self.dones = self.env.dones
        self.infos = self.env.infos

    def observe(self, agent):
        obs = self.env.observe()
        return obs

    def state(self):
        state = self.env.state()
        return state

    def close(self):
        self.env.close()

    def render(self, mode='human'):
        return self.env.render(mode)

    def step(self, action):
        if self.dones[self.agent_selection]:
            return self._was_done_step(action)
        agent = self.agent_selection
        if not self.action_spaces[agent].contains(action):
            raise Exception('Action for agent {} must be in Discrete({}).'
                            'It is currently {}'.format(agent, self.action_spaces[agent].n, action))

        self.env.step(action, agent)
        # select next agent and observe
        self.agent_selection = self._agent_selector.next()
        self.rewards = self.env.rewards
        self.dones = self.env.dones
        self.infos = self.env.infos

        self.score = self.env.score

        self._cumulative_rewards[agent] = 0
        self._accumulate_rewards()

# This was originally created, in full, by Ananth Hari in a different repo, and was
# added in by J K Terry (which is why they're shown as the creator in the git history)
