import os
import numpy as np
import gym
from gym.utils import seeding
from .cake_paddle import CakePaddle, RENDER_RATIO
from .manual_control import manual_control
from pettingzoo import AECEnv
from pettingzoo.utils import wrappers
from pettingzoo.utils.agent_selector import agent_selector
from pettingzoo.utils.to_parallel import parallel_wrapper_fn
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame
from gym.utils import EzPickle

KERNEL_WINDOW_LENGTH = 1


def get_image(path):
    image = pygame.image.load(path)
    return image


def deg_to_rad(deg):
    return deg * np.pi / 180


def get_flat_shape(width, height):
    return int(width * height / (2 * KERNEL_WINDOW_LENGTH * KERNEL_WINDOW_LENGTH))


def original_obs_shape(screen_width, screen_height):
    return (int(screen_height / KERNEL_WINDOW_LENGTH), int(screen_width / (2 * KERNEL_WINDOW_LENGTH)), 1)


def get_valid_angle(randomizer):
    # generates an angle in [0, 2*np.pi) that \
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


def get_small_random_value(randomizer):
    # generates a small random value between [0, 1/100)
    return (1 / 100) * randomizer.rand()


class PaddleSprite(pygame.sprite.Sprite):
    def __init__(self, dims, speed):
        self.surf = pygame.Surface(dims)
        self.rect = self.surf.get_rect()
        self.speed = speed

    def reset(self):
        pass

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.rect)

    def update(self, area, action):
        # action: 1 - up, 2 - down
        movepos = [0, 0]
        if action > 0:
            if action == 1:
                movepos[1] = movepos[1] - self.speed
            elif action == 2:
                movepos[1] = movepos[1] + self.speed

            # make sure the players stay inside the screen
            newpos = self.rect.move(movepos)
            if area.contains(newpos):
                self.rect = newpos

    def process_collision(self, b_rect, dx, dy, b_speed, paddle_type):
        '''

        Parameters
        ----------
        b_rect : Ball rect
        dx, dy : Ball speed along single axis
        b_speed : Ball speed

        Returns
        -------
        is_collision: 1 if ball collides with paddle
        b_rect: new ball rect
        b_speed: new ball speed

        '''
        if paddle_type == 1:
            if self.rect.colliderect(b_rect):
                is_collision = True
                if dx < 0:
                    b_rect.left = self.rect.right
                    b_speed[0] = -b_speed[0]
                # top or bottom edge
                elif dy > 0:
                    b_rect.bottom = self.rect.top
                    b_speed[1] = -b_speed[1]
                elif dy < 0:
                    b_rect.top = self.rect.bottom
                    b_speed[1] = -b_speed[1]
                return is_collision, b_rect, b_speed
        elif paddle_type == 2:
            if self.rect.colliderect(b_rect):
                is_collision = True
                if dx > 0:
                    b_rect.right = self.rect.left
                    b_speed[0] = -b_speed[0]
                # top or bottom edge
                elif dy > 0:
                    b_rect.bottom = self.rect.top
                    b_speed[1] = -b_speed[1]
                elif dy < 0:
                    b_rect.top = self.rect.bottom
                    b_speed[1] = -b_speed[1]
                return is_collision, b_rect, b_speed
        return False, b_rect, b_speed


class BallSprite(pygame.sprite.Sprite):
    def __init__(self, randomizer, dims, speed, bounce_randomness=False):  # def __init__(self, image, speed):
        # self.surf = get_image(image)
        self.surf = pygame.Surface(dims)
        self.rect = self.surf.get_rect()
        self.speed_val = speed
        self.speed = [int(self.speed_val * np.cos(np.pi / 4)), int(self.speed_val * np.sin(np.pi / 4))]
        self.bounce_randomness = bounce_randomness
        self.done = False
        self.hit = False
        self.randomizer = randomizer

    def update2(self, area, p0, p1):
        (speed_x, speed_y) = self.speed
        done_x, done_y = False, False
        if self.speed[0] != 0:
            done_x = self.move_single_axis(self.speed[0], 0, area, p0, p1)
        if self.speed[1] != 0:
            done_y = self.move_single_axis(0, self.speed[1], area, p0, p1)
        return (done_x or done_y)

    def move_single_axis(self, dx, dy, area, p0, p1):
        # returns done

        # move ball rect
        self.rect.x += dx
        self.rect.y += dy

        if not area.contains(self.rect):
            # bottom wall
            if dy > 0:
                self.rect.bottom = area.bottom
                self.speed[1] = -self.speed[1]
            # top wall
            elif dy < 0:
                self.rect.top = area.top
                self.speed[1] = -self.speed[1]
            # right or left walls
            else:
                return True
                self.speed[0] = -self.speed[0]

        else:
            # Do ball and bat collide?
            # add some randomness
            r_val = 0
            if self.bounce_randomness:
                r_val = get_small_random_value(self.randomizer)

            # ball in left half of screen
            if self.rect.center[0] < area.center[0]:
                is_collision, self.rect, self.speed = p0.process_collision(self.rect, dx, dy, self.speed, 1)
                if is_collision:
                    self.speed = [self.speed[0] + np.sign(self.speed[0]) * r_val, self.speed[1] + np.sign(self.speed[1]) * r_val]
            # ball in right half
            else:
                is_collision, self.rect, self.speed = p1.process_collision(self.rect, dx, dy, self.speed, 2)
                if is_collision:
                    self.speed = [self.speed[0] + np.sign(self.speed[0]) * r_val, self.speed[1] + np.sign(self.speed[1]) * r_val]

        return False

    def draw(self, screen):
        # screen.blit(self.surf, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect)


class CooperativePong(gym.Env):

    metadata = {'render.modes': ['human', "rgb_array"]}

    def __init__(self, randomizer, ball_speed=9, left_paddle_speed=12, right_paddle_speed=12, cake_paddle=True, max_cycles=900, bounce_randomness=False):
        super(CooperativePong, self).__init__()

        pygame.init()
        self.num_agents = 2

        # Display screen
        self.s_width, self.s_height = 960 // RENDER_RATIO, 560 // RENDER_RATIO
        self.screen = pygame.Surface((self.s_width, self.s_height))  # (960, 720) # (640, 480) # (100, 200)
        self.area = self.screen.get_rect()

        # define action and observation spaces
        self.action_space = [gym.spaces.Discrete(3) for _ in range(self.num_agents)]
        original_shape = original_obs_shape(self.s_width, self.s_height)
        original_color_shape = (original_shape[0], original_shape[1], 3)
        # self.observation_space = [gym.spaces.Box(low=0.0, high=1.0, shape=(original_shape), dtype=np.float32) for _ in range(self.num_agents)]
        self.observation_space = [gym.spaces.Box(low=0, high=255, shape=(original_color_shape), dtype=np.uint8) for _ in range(self.num_agents)]

        self.renderOn = False

        # set speed
        self.speed = [ball_speed, left_paddle_speed, right_paddle_speed]

        self.max_cycles = max_cycles

        # paddles
        self.p0 = PaddleSprite((20 // RENDER_RATIO, 80 // RENDER_RATIO), left_paddle_speed)
        if cake_paddle:
            self.p1 = CakePaddle(right_paddle_speed)
        else:
            self.p1 = PaddleSprite((20 // RENDER_RATIO, 100 // RENDER_RATIO), right_paddle_speed)

        self.agents = ["paddle_0", "paddle_1"]  # list(range(self.num_agents))

        # ball
        self.ball = BallSprite(randomizer, (20 // RENDER_RATIO, 20 // RENDER_RATIO), ball_speed, bounce_randomness)
        self.randomizer = randomizer

        self.reinit()

    def reinit(self):
        self.rewards = dict(zip(self.agents, [0.0] * len(self.agents)))
        self.dones = dict(zip(self.agents, [False] * len(self.agents)))
        self.infos = dict(zip(self.agents, [{}] * len(self.agents)))
        self.score = 0

    def reset(self):
        # does not return observations

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

        observation = pygame.surfarray.pixels3d(self.screen)
        if mode == "human":
            pygame.display.flip()
        return np.transpose(observation, axes=(1, 0, 2)) if mode == "rgb_array" else None

    def observe(self, agent):
        observation = pygame.surfarray.pixels3d(self.screen)
        observation = np.rot90(observation, k=3)  # now the obs is laid out as H, W as rows and cols
        observation = np.fliplr(observation)  # laid out in the correct order
        if agent == self.agents[0]:
            return observation[:, :int(observation.shape[1] / 2), :]
        elif agent == self.agents[1]:
            return observation[:, int(observation.shape[1] / 2):, :]

    def draw(self):
        # draw background
        # pygame.display.get_surface().fill((0, 0, 0))
        pygame.draw.rect(self.screen, (0, 0, 0), self.area)
        # draw ball and paddles
        self.p0.draw(self.screen)
        self.p1.draw(self.screen)
        self.ball.draw(self.screen)

    def step(self, action, agent):
        '''
        Does not return anything
        '''

        # update p0, p1 accordingly
        # action: 0: do nothing,
        # action: 1: p[i] move up, 2: p[i] move down
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
                    reward = -100
                    self.score += reward
                if not self.done:
                    self.num_frames += 1
                    # scaling reward so that the max reward is 100
                    reward = 100 / self.max_cycles
                    self.score += reward
                    if self.num_frames == self.max_cycles:
                        self.done = True

                for ag in self.agents:
                    self.rewards[ag] = reward / self.num_agents
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
    metadata = {'render.modes': ['human', "rgb_array"]}

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
        # dicts
        self.observations = {}
        self.rewards = self.env.rewards
        self.dones = self.env.dones
        self.infos = self.env.infos

        self.score = self.env.score
        self.display_wait = 0.0

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
        obs = self.env.observe(agent)
        return obs

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
        self._dones_step_first()

# This was originally created, in full, by Ananth Hari in a different repo, and was
# added in by Justin Terry (which is why he's shown as the creator in the git history)
