import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame
import pymunkoptions
pymunkoptions.options["debug"] = False
import pymunk
import pymunk.pygame_util
import random
import math
import numpy as np
from skimage import measure
import gym
from ray.rllib.env.multi_agent_env import MultiAgentEnv

_image_library = {}


def get_image(path):
    from os import path as os_path
    cwd = os_path.dirname(__file__)
    image = pygame.image.load(cwd + '/' + path)
    return image


class env(MultiAgentEnv):

    metadata = {'render.modes': ['human']}

    def __init__(self, flatten_obs=True):
        super(env, self).__init__()
        self.num_agents = 20
        self.agent_ids = list(range(self.num_agents))

        self.flatten_obs = flatten_obs

        self.action_space_dict = dict(zip(self.agent_ids, [gym.spaces.Discrete(3)]*self.num_agents))
        if self.flatten_obs:
            self.observation_space_dict = dict(zip(self.agent_ids, [gym.spaces.Box(low=0.0, high=1.0, shape=(1500,), dtype=np.float32)]*self.num_agents))
        else:
            self.observation_space_dict = dict(zip(self.agent_ids, [gym.spaces.Box(low=0.0, high=1.0, shape=(50, 30, 1), dtype=np.float32)]*self.num_agents))

        pygame.init()
        pymunk.pygame_util.positive_y_is_up = False
        self.clock = pygame.time.Clock()

        self.renderOn = False
        self.screen = pygame.Surface((960, 560))

        self.pistonSprite = get_image('piston.png')
        self.background = get_image('background.png')

        self.space = pymunk.Space(threaded=True)
        self.space.threads = 2
        self.space.gravity = (0.0, 750.0)
        self.space.collision_bias = .0001
        self.space.iterations = 10  # 10 is default in PyMunk

        self.pistonList = []
        self.pistonRewards = []  # Keeps track of individual rewards
        self.recentFrameLimit = 20  # Defines what "recent" means in terms of number of frames.
        self.recentPistons = set()  # Set of pistons that have touched the ball recently
        self.global_reward_weight = 0.5
        self.local_reward_weight = 1 - self.global_reward_weight

        self.add_walls()

        self.done = False

        self.velocity = 4
        self.resolution = 16

        for i in range(20):
            piston = self.add_piston(self.space, 85+40*i, 451 - random.randrange(0, .5*self.velocity*self.resolution, self.velocity))
            self.pistonList.append(piston)

        self.offset = random.randint(-30, 30)
        self.ball = self.add_ball(800 + self.offset, 350 + random.randint(-15, 15))
        self.lastX = int(self.ball.position[0]-40)
        self.distance = self.lastX-80

        self.screen.blit(self.background, (0, 0))

        self.rect = pygame.Rect(80, 80, 800, 377)

        # blit background image if ball goes out of bounds. Ball radius is 40
        self.valid_ball_position_rect = pygame.Rect(self.rect.left + 40, self.rect.top + 40, self.rect.width - 80, self.rect.height - 80)

        self.num_frames = 0

    def observe(self):
        observation = pygame.surfarray.array3d(self.screen)
        observation = np.rot90(observation, k=3)
        observation = np.fliplr(observation)
        observation = observation[257:457, 40:920, 2]  # take blue channel only instead of doing full greyscale

        mean = lambda x, axis: np.mean(x, axis=axis, dtype=np.uint8)
        observation = measure.block_reduce(observation, block_size=(4, 4), func=mean)

        observations = {}

        for i in range(len(self.pistonList)):
            cropped = observation[:, i*10:30 + i*10]
            if self.flatten_obs:
                unscaled_obs = np.expand_dims(cropped, axis=2).flatten()
            else:
                unscaled_obs = np.expand_dims(cropped, axis=2)
            observations[self.agent_ids[i]] = np.divide(unscaled_obs, 255, dtype=np.float32)
        return observations

    def enable_render(self):
        self.screen = pygame.display.set_mode((960, 560))
        self.renderOn = True
        self.reset()

    def close(self):
        self.screen = pygame.Surface((960, 560))
        self.renderOn = False
        pygame.display.quit()

    def add_walls(self):
        walls = [pymunk.Segment(self.space.static_body, (80, 80), (880, 80), 1)
                 , pymunk.Segment(self.space.static_body, (80, 80), (80, 480), 1)
                 , pymunk.Segment(self.space.static_body, (80, 480), (880, 480), 1)
                 , pymunk.Segment(self.space.static_body, (880, 80), (880, 480), 1)]
        for wall in walls:
            wall.friction = .64
            self.space.add(wall)

    def add_ball(self, x, y):
        mass = .75
        radius = 40
        inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
        body = pymunk.Body(mass, inertia)
        body.position = x, y
        body.angular_velocity = random.uniform(-6*math.pi, 6*math.pi)  # radians per second
        shape = pymunk.Circle(body, radius, (0, 0))
        shape.friction = .3
        shape.elasticity = 1.5
        self.space.add(body, shape)
        return body

    def add_piston(self, space, x, y):
        piston = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        piston.position = x, y
        segment = pymunk.Segment(piston, (0, 0), (30, 0), 5)
        segment.friction = .64
        segment.color = pygame.color.THECOLORS["blue"]
        space.add(segment)
        return piston

    def move_piston(self, piston, v):

        def cap(y):
            if y > 451:
                y = 451
            elif y < 451 - (16*self.velocity):
                y = 451 - (16*self.velocity)
            return y

        piston.position = (piston.position[0], cap(piston.position[1] - v*self.velocity))

    def reset(self):
        for i, piston in enumerate(self.pistonList):
            piston.position = (85+40*i, 451 - random.randrange(0, .5*self.velocity*self.resolution, self.velocity))

        self.offset = random.randint(-30, 30)
        self.ball.position = (800 + self.offset, 350 + random.randint(-15, 15))
        self.lastX = int(self.ball.position[0]-40)
        self.distance = self.lastX-80
        self.screen.blit(self.background, (0, 0))
        self.draw()

        self.done = False

        self.num_frames = 0

        return self.observe()

    def draw(self):
        # redraw the background image if ball goes outside valid position
        if not self.valid_ball_position_rect.collidepoint(self.ball.position):
            self.screen.blit(self.background, (0, 0))

        pygame.draw.rect(self.screen, (255, 255, 255), self.rect)
        pygame.draw.circle(self.screen, (65, 159, 221), (int(self.ball.position[0]), int(self.ball.position[1])), 40)
        pygame.draw.line(self.screen, (58, 64, 65), (int(self.ball.position[0]), int(self.ball.position[1])), (int(self.ball.position[0]) + 39*np.cos(self.ball.angle), int(self.ball.position[1]) + 39*np.sin(self.ball.angle)), 3)  # 39 because it kept sticking over by 1 at 40

        for piston in self.pistonList:
            self.screen.blit(self.pistonSprite, (piston.position[0]-5, piston.position[1]-5))

    def get_nearby_pistons(self):
        # first piston = leftmost
        nearby_pistons = []
        ball_pos = int(self.ball.position[0]-40)
        closest = abs(self.pistonList[0].position.x - ball_pos)
        closest_piston_index = 0
        for i in range(len(self.pistonList)):
            next_distance = abs(self.pistonList[i].position.x - ball_pos)
            if next_distance < closest:
                closest = next_distance
                closest_piston_index = i

        if closest_piston_index > 0:
            nearby_pistons.append(closest_piston_index - 1)
        nearby_pistons.append(closest_piston_index)
        if closest_piston_index < len(self.pistonList) - 1:
            nearby_pistons.append(closest_piston_index + 1)

        return nearby_pistons

    def get_local_reward(self, prev_position, curr_position):
        local_reward = .5 * (prev_position - curr_position)
        return local_reward * self.local_reward_weight

    def render(self):
        if not self.renderOn:
            # sets self.renderOn to true and initializes display
            self.enable_render()
        pygame.display.flip()

    def step(self, actions):
        for i, agent_id in enumerate(self.agent_ids):
            if np.isnan(actions[agent_id]):
                actions[agent_id] = 1
            elif not self.action_space_dict[i].contains(actions[i]):
                raise Exception('Action for agent {} must be in Discrete({}).'
                                'It is currently {}'.format(i, self.action_space_dict[i].n, actions[i]))
            self.move_piston(self.pistonList[i], actions[agent_id] - 1)  # 1 is up, -1 is down, 0 is do nothing

        self.space.step(1/15.0)

        self.draw()

        newX = int(self.ball.position[0]-40)
        local_reward = self.get_local_reward(self.lastX, newX)
        global_reward = (100/self.distance)*(self.lastX - newX)  # opposite order due to moving right to left
        self.lastX = newX
        if newX <= 81:
            self.done = True
        if self.renderOn:
            self.clock.tick(15)
        else:
            self.clock.tick()

        observation = self.observe()

        total_reward = [(global_reward/self.num_agents) * self.global_reward_weight] * self.num_agents  # start with global reward
        local_pistons_to_reward = self.get_nearby_pistons()
        for index in local_pistons_to_reward:
            total_reward[index] += local_reward

        self.num_frames += 1
        if self.num_frames == 900:
            self.done = True
        if not self.done:
            global_reward -= 0.1
        # Clear the list of recent pistons for the next reward cycle
        if self.num_frames % self.recentFrameLimit == 0:
            self.recentPistons = set()

        rewardDict = dict(zip(self.agent_ids, total_reward))
        doneDict = dict(zip(self.agent_ids, [self.done]*self.num_agents))
        doneDict['__all__'] = self.done

        return observation, rewardDict, doneDict, {}
