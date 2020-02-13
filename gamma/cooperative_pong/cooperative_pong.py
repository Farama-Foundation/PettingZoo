import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame
import numpy as np
from skimage import measure
import gym
import matplotlib.pyplot as plt
from .cake_paddle import CakePaddle

from ray.rllib.env.multi_agent_env import MultiAgentEnv

KERNEL_WINDOW_LENGTH = 10

def get_image(path):
    image = pygame.image.load(path)
    return image


def deg_to_rad(deg):
    return deg*np.pi/180


def get_flat_shape(width, height):
    return int(width * height/ (2*KERNEL_WINDOW_LENGTH*KERNEL_WINDOW_LENGTH))

def original_obs_shape(screen_width, screen_height):
    return (int(screen_height/KERNEL_WINDOW_LENGTH), int(screen_width/(2*KERNEL_WINDOW_LENGTH)), 1)


def get_valid_angle():
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
    while ((angle > a1 and angle < b1) or (angle > a2 and angle < b2) or \
        (angle > c1 and angle < d1) or (angle > c2) or (angle < d2)):
        angle = 2 * np.pi * np.random.rand()

    return angle


def get_small_random_value():
    # generates a small random value between [0, 1/100)
    return (1/100) * np.random.rand()


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
    def __init__(self, dims, speed, bounce_randomness = 0): # def __init__(self, image, speed):
        # self.surf = get_image(image)
        self.surf = pygame.Surface(dims)
        self.rect = self.surf.get_rect()
        self.speed_val = speed
        self.speed = [int(self.speed_val*np.cos(np.pi/4)), int(self.speed_val*np.sin(np.pi/4))]
        self.bounce_randomness = bounce_randomness
        self.done = False
        self.hit = False

    def update2(self, area, p1, p2):
        (speed_x, speed_y) = self.speed
        done_x, done_y = False, False
        if self.speed[0] != 0:
            done_x = self.move_single_axis(self.speed[0], 0, area, p1, p2)
        if self.speed[1] != 0:
            done_y = self.move_single_axis(0, self.speed[1], area, p1, p2)
        return (done_x or done_y)

    def move_single_axis(self, dx, dy, area, p1, p2):
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
                r_val = get_small_random_value()

            # ball in left half of screen
            if self.rect.center[0] < area.center[0]:
                is_collision, self.rect, self.speed = p1.process_collision(self.rect, dx, dy, self.speed, 1)
                if is_collision:
                    self.speed = [self.speed[0] + np.sign(self.speed[0]) * r_val, self.speed[1] + np.sign(self.speed[1]) * r_val]
            # ball in right half
            else:
                is_collision, self.rect, self.speed = p2.process_collision(self.rect, dx, dy, self.speed, 2)
                if is_collision:
                    self.speed = [self.speed[0] + np.sign(self.speed[0]) * r_val, self.speed[1] + np.sign(self.speed[1]) * r_val]

        return False

    def draw(self, screen):
        # screen.blit(self.surf, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect)


class CooperativePong(gym.Env):

    metadata = {'render.modes': ['human']}

    # ball_speed = [3,3], p1_speed = 3, p2_speed = 3
    def __init__(self, ball_speed=18, p1_speed=25, p2_speed=25, is_cake=1, bounce_randomness=0, flatten_obs=True):
        super(CooperativePong, self).__init__()

        pygame.init()
        self.num_agents = 2

        # Display screen
        self.s_width, self.s_height = 960, 560
        self.screen = pygame.Surface((self.s_width, self.s_height))  # (960, 720) # (640, 480) # (100, 200)
        self.area = self.screen.get_rect()

        # define action and observation spaces
        self.flatten_obs = flatten_obs
        self.action_space = [gym.spaces.Discrete(3) for _ in range(self.num_agents)]
        if self.flatten_obs:
            flattened_shape = get_flat_shape(self.s_width, self.s_height)
            self.observation_space = [gym.spaces.Box(low=0.0, high=1.0, shape=(flattened_shape,), dtype=np.float32) for _ in range(self.num_agents)]
        else:
            original_shape = original_obs_shape(self.s_width, self.s_height)
            self.observation_space = [gym.spaces.Box(low=0.0, high=1.0, shape=(original_shape), dtype=np.float32) for _ in range(self.num_agents)]

        self.clock = pygame.time.Clock()

        self.renderOn = False

        # set speed
        self.speed = [ball_speed, p1_speed, p2_speed]

        # paddles
        self.p1 = PaddleSprite((20, 80), p1_speed)
        if is_cake:
            self.p2 = CakePaddle(p2_speed)
        else:
            self.p2 = PaddleSprite((20, 100), p2_speed)

        # ball
        self.ball = BallSprite((20,20), ball_speed, bounce_randomness)

        self.reset()

    def reset(self):
        # reset ball and paddle init conditions
        self.ball.rect.center = self.area.center
        # set the direction to an angle between [0, 2*np.pi)
        angle = get_valid_angle()
        # angle = deg_to_rad(89)
        self.ball.speed = [int(self.ball.speed_val*np.cos(angle)), int(self.ball.speed_val*np.sin(angle))]

        self.p1.rect.midleft = self.area.midleft
        self.p2.rect.midright = self.area.midright
        self.p1.reset()
        self.p2.reset()
        self.p1.speed = self.speed[1]
        self.p2.speed = self.speed[2]

        self.done = False

        self.score = 0
        self.num_frames = 0

        self.draw()
        return self.observe()

    def close(self):
        if self.renderOn:
            pygame.display.quit()
            self.renderOn = False

    def enable_render(self):
        self.screen = pygame.display.set_mode(self.screen.get_size())
        self.renderOn = True

    def render(self):
        if not self.renderOn:
            # sets self.renderOn to true and initializes display
            self.enable_render()
        pygame.display.flip()

    def observe(self):
        observation = pygame.surfarray.array3d(self.screen)
        observation = np.rot90(observation, k=3)  # now the obs is laid out as H, W as rows and cols
        observation = np.fliplr(observation)  # laid out in the correct order
        observation = observation[:, :, 2]  # take blue channel only instead of doing full greyscale

        mean = lambda x, axis: np.mean(x, axis=axis, dtype=np.uint8)

        # Fixed: Uses mean
        observation = measure.block_reduce(observation, block_size=(KERNEL_WINDOW_LENGTH, KERNEL_WINDOW_LENGTH), func=mean)

        height, width = observation.shape

        # partition the entire screen into 2 halves for observing the state
        obs = [observation[:, 0:int(width/2)], observation[:, int(width/2):]]
        # exapnd dims to 3
        observation = []
        for i in obs:
            if self.flatten_obs:
                unscaled_obs = np.expand_dims(i, axis=2).flatten()
            else:
                unscaled_obs = np.expand_dims(i, axis=2)
            observation.append(np.divide(unscaled_obs, 255, dtype=np.float32))
        return observation

    def draw(self):
        # draw background
        # pygame.display.get_surface().fill((0, 0, 0))
        pygame.draw.rect(self.screen, (0, 0, 0), self.area)
        # draw ball and paddles
        self.p1.draw(self.screen)
        self.p2.draw(self.screen)
        self.ball.draw(self.screen)

    def step(self, actions):
        # returns a list of observations, list of rewards, list of dones, list of info.
        # Size of each list = num_agents

        # update p1, p2
        # actions[i]: 0: do nothing,
        # actions[i]: 1: p[i] move up, 2: p[i] move down
        self.p1.update(self.area, actions[0])
        self.p2.update(self.area, actions[1])
        # update ball position
        # self.done = self.ball.update(self.area, self.p1.rect, self.p2.rect)
        self.done = self.ball.update2(self.area, self.p1, self.p2)

        self.draw()

        observation = self.observe()

        # reward is the length of time ball is in play
        reward = 0
        # ball is out-of-bounds
        if self.done:
            reward = -100
            self.score += reward
        if not self.done:
            self.num_frames += 1
            # scaling reward so that the max reward is 100
            reward = 1/9
            self.score += reward
            if self.num_frames == 900:
                self.done = True
                print("score = {}, frames = {}".format(self.score, self.num_frames))

        # let the clock tick
        if self.renderOn:
            self.clock.tick(15)
        else:
            self.clock.tick()

        reward = [reward/self.num_agents] * self.num_agents
        done = [self.done] * self.num_agents
        info = [{}] * self.num_agents

        return observation, reward, done, info

    def plot_obs(self, observation, fname):
        # shrink observation dims
        shape = original_obs_shape(self.s_width, self.s_height)
        for i in range(len(observation)):
            observation[i] = observation[i].reshape(shape)
            observation[i] = np.squeeze(observation[i])
        fig = plt.figure()
        # plt.imsave('test.png', observation[0], cmap = plt.cm.gray)
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)
        ax1.imshow(observation[0], cmap=plt.cm.gray)
        ax2.imshow(observation[1], cmap=plt.cm.gray)
        ax1.set_title("Observation[0]")
        ax2.set_title("Observation[1]")
        plt.savefig(fname)


class env(MultiAgentEnv):
    metadata = {'render.modes': ['human']}

    def __init__(self, **kwargs):
        super(env, self).__init__()
        self.env = CooperativePong(**kwargs)

        self.num_agents = 2
        self.agent_ids = list(range(self.num_agents))
        # spaces
        self.action_space_dict = dict(zip(self.agent_ids, self.env.action_space))
        self.observation_space_dict = dict(zip(self.agent_ids, self.env.observation_space))
        
        self.score = self.env.score
        
        self.reset()
        
    def convert_to_dict(self, list_of_list):
        return dict(zip(self.agent_ids, list_of_list))
    
    def reset(self):
        obs = self.env.reset()
        return self.convert_to_dict(obs)

    def close(self):
        self.env.close()

    def render(self):
        self.env.render()

    def step(self, actions):
        for agent_id in self.agent_ids:
            if np.isnan(actions[agent_id]):
                actions[agent_id] = 0
            elif not self.action_space_dict[agent_id].contains(actions[agent_id]):
                raise Exception('Action for agent {} must be in Discrete({}).'
                                'It is currently {}'.format(agent_id, self.action_space_dict[agent_id].n, actions[agent_id]))

        observation, reward, done, info = self.env.step(actions)

        observation_dict = self.convert_to_dict(observation)
        reward_dict = self.convert_to_dict(reward)
        info_dict = self.convert_to_dict(info)
        done_dict = self.convert_to_dict(done)
        done_dict["__all__"] = done[0]
        
        self.score = self.env.score

        return observation_dict, reward_dict, done_dict, info_dict
