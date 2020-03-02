from ray.rllib.env.multi_agent_env import MultiAgentEnv
import pygame
import os
import random
import gym  
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'


def get_image(path):
    from os import path as os_path
    cwd = os_path.dirname(__file__)
    image = pygame.image.load(cwd + '/' + path)
    return image


def within(a, b, diff):
    return abs(a-b) <= diff


class Prisoner:
    def __init__(self, p, l, r, w):
        self.position = p
        self.left_bound = l
        self.right_bound = r
        self.window = w
        self.first_touch = -1  # rewarded on touching bound != first_touch
        self.last_touch = -1  # to track last touched wall


class env(MultiAgentEnv):

    def __init__(self, continuous=False, vector_observation=True):
        # super(env, self).__init__()
        self.num_agents = 8
        self.agents = list(range(0, self.num_agents))
        self.agent_order = self.agents
        self.agent_selection = 0

        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((750, 650))
        self.num_frames = 0
        self.done_val = False

        self.background = get_image('background.png')
        self.prisoner_sprite = get_image('prisoner.png')
        self.prisoner_sprite_x = 30
        self.prisoner_sprite_y = 46

        self.velocity = 8
        self.continuous = continuous
        self.vector_obs = vector_observation

        # self.options = pymunk.pygame_util.DrawOptions(self.screen)
        # self.options.shape_outline_color = (50, 50, 50, 5)
        # self.options.shape_static_color = (100, 100, 100, 10)

        self.walls = []
        self.create_walls()

        self.prisoners = []
        prisoner_spawn_locs = [(200, 150-self.prisoner_sprite_y, 50, 350, (50, 50, 350, 150)), (550, 150-self.prisoner_sprite_y, 400, 700, (400, 50, 700, 150)), (200, 300-self.prisoner_sprite_y, 50, 350, (50, 200, 350, 300)),
                               (550, 300-self.prisoner_sprite_y, 400, 700, (400, 200, 700, 300)), (200, 450-self.prisoner_sprite_y, 50, 350, (50, 350, 350, 450)), (550, 450-self.prisoner_sprite_y, 400, 700, (400, 350, 700, 450)), (200, 600-self.prisoner_sprite_y, 50, 350, (50, 500, 350, 600)), (550, 600-self.prisoner_sprite_y, 400, 700, (400, 500, 700, 600))]
        self.prisoner_mapping = {(0, 0): 0, (1, 0): 1, (0, 1): 2,
                                 (1, 1): 3, (0, 2): 4, (1, 2): 5, (0, 3): 6, (1, 3): 7}
        for p in prisoner_spawn_locs:
            x, y, l, r, u = p
            self.prisoners.append(self.create_prisoner(
                x + random.randint(-20, 20), y, l, r, u))

        self.screen.blit(self.background, (0, 0))

    def create_walls(self):
        self.walls = [(0, 0, 50, 700), (350, 0, 50, 700),
                      (700, 0, 50, 700)]
        self.vert_walls = []
        for i in range(5):
            y = 150*i
            self.walls.append((50, y, 300, 50))
            self.walls.append((400, y, 300, 50))

    def create_prisoner(self, x, y, l, r, u):
        return Prisoner((x, y), l, r - self.prisoner_sprite_x, u)

    # returns reward of hitting both sides of room, 0 if not
    def move_prisoner(self, prisoner_id, movement):
        prisoner = self.prisoners[prisoner_id]
        if self.continuous:
            prisoner.position = (
                prisoner.position[0] + movement, prisoner.position[1])
        else:
            prisoner.position = (
                prisoner.position[0] + movement*self.velocity, prisoner.position[1])
        reward = 0
        if prisoner.position[0] < prisoner.left_bound:
            prisoner.position = (prisoner.left_bound, prisoner.position[1])
            if prisoner.first_touch == -1:
                prisoner.first_touch = prisoner.left_bound
            if prisoner.first_touch != prisoner.left_bound and prisoner.last_touch == prisoner.right_bound:
                reward = 1
            prisoner.last_touch = prisoner.left_bound
        if prisoner.position[0] > prisoner.right_bound:
            prisoner.position = (prisoner.right_bound, prisoner.position[1])
            if prisoner.first_touch == -1:
                prisoner.first_touch = prisoner.right_bound
            if prisoner.first_touch != prisoner.right_bound and prisoner.last_touch == prisoner.left_bound:
                reward = 1
            prisoner.last_touch = prisoner.right_bound
        return reward

    def convert_coord_to_prisoner_id(self, c):
        return self.prisoner_mapping[c]

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        for k in self.walls:
            pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(k))

        for p in self.prisoners:
            self.screen.blit(self.prisoner_sprite, p.position)

        # self.space.debug_draw(self.options)

    def observe(self, agent):
        
        if self.vector_obs:
            
            p = self.prisoners[agent]
            x = p.position[0]
            obs = (x-p.left_bound,p.right_bound - x)
            return obs
        else:
            capture = pygame.surfarray.pixels3d(self.screen)
            p = self.prisoners[agent]
            x1, y1, x2, y2 = p.window
            sub_screen = capture[x1:x2,y1:y2, :]
            return sub_screen

    def reset(self, observe=True):
        self.num_frames = 0
        self.done_val = False
        prisoner_spawn_locs = [(200, 150-self.prisoner_sprite_y, 50, 350, (50, 50, 350, 150)), (550, 150-self.prisoner_sprite_y, 400, 700, (400, 50, 700, 150)), (200, 300-self.prisoner_sprite_y, 50, 350, (50, 200, 350, 300)),(550, 300-self.prisoner_sprite_y, 400, 700, (400, 200, 700, 300)), (200, 450-self.prisoner_sprite_y, 50, 350, (50, 350, 350, 450)), (550, 450-self.prisoner_sprite_y, 400, 700, (400, 350, 700, 450)), (200, 600-self.prisoner_sprite_y, 50, 350, (50, 500, 350, 600)), (550, 600-self.prisoner_sprite_y, 400, 700, (400, 500, 700, 600))]
        self.agent_selection = 0
        for i in self.agents:
            p = self.prisoners[i]
            x, y, l, r, u = prisoner_spawn_locs[i]
            p.position = (x + random.randint(-20,20), y)

        if observe:
            return self.observe(0)
        

    def step(self, action):
        # move prisoners, -1 = move left, 0 = do  nothing and 1 is move right

        # if not continuous, input must be normalized
        reward = 0
        if action != None:
            if action != 0 and not self.continuous:
                action = action/abs(action)
            reward = self.move_prisoner(self.agent_selection, action)
        
        self.clock.tick(15)
        self.draw()

        self.num_frames += 1
        if (self.num_frames >= 500):
            self.done_val = True

        self.agent_selection = (self.agent_selection + 1) % self.num_agents
        observation = self.observe(self.agent_selection)
        done = self.done_val
        info = {}

        return observation, reward, done, info

    def render(self):
        pygame.display.flip()

from .manual_test import manual_control