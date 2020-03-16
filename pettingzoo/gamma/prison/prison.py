from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
import pygame
import os
import numpy as np
import random
from gym import spaces
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
        self.still_sprite = None
        self.left_sprite = None
        self.right_sprite = None
        self.state = 0

    def set_sprite(self, s):
        self.still_sprite = get_image(s+"_still.png")
        self.left_sprite = get_image(s+"_left.png")
        self.right_sprite = get_image(s+"_right.png")

    def set_state(self, st):
        self.state = st
    
    def get_sprite(self):
        if self.state == 0:
            return self.still_sprite
        elif self.state == 1:
            return self.right_sprite
        elif self.state == -1:
            return self.left_sprite
        else:
            print("INVALID STATE",self.state)
            return self.still_sprite


class env(AECEnv):

    def __init__(self, continuous=False, vector_observation=True):
        # super(env, self).__init__()
        self.num_agents = 8
        self.agents = list(range(0, self.num_agents))
        self.agent_order = self.agents[:]
        self.agent_selector_obj = agent_selector(self.agent_order)
        self.agent_selection = 0
        self.sprite_list = ["sprites/alien", "sprites/drone", "sprites/glowy", "sprites/reptile", "sprites/ufo"]
        self.rewards = dict(zip(self.agents,[0 for _ in self.agents]))
        self.dones = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [[] for _ in self.agents]))
        self.metadata = {'render.modes': ['human']} 

        pygame.init()
        pygame.display.init()
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

        self.action_spaces = {}
        if continuous:
            for a in self.agents:
                self.action_spaces[a] = spaces.Box(low=np.NINF, high=np.Inf, shape=(1,))
        else:
            for a in self.agents:
                self.action_spaces[a] = spaces.Box(low=-1, high=1, shape=(1,))

        self.observation_spaces= {}
        self.last_observation = {}
        for a in self.agents:
            self.last_observation[a] = None
            if vector_observation:
                self.observation_spaces[a] = spaces.Box(low=-300, high=300, shape=(2,))
            else:
                self.observation_spaces[a] = spaces.Box(low=0, high=255, shape=(300,100,3))

        # self.options = pymunk.pygame_util.DrawOptions(self.screen)
        # self.options.shape_outline_color = (50, 50, 50, 5)
        # self.options.shape_static_color = (100, 100, 100, 10)

        self.walls = []
        self.create_walls()

        self.prisoners = []
        prisoner_spawn_locs = [(200, 150-self.prisoner_sprite_y, 50, 350, (50, 50, 350, 150)), 
                                (550, 150-self.prisoner_sprite_y, 400, 700, (400, 50, 700, 150)), 
                                (200, 300-self.prisoner_sprite_y, 50, 350, (50, 200, 350, 300)),
                               (550, 300-self.prisoner_sprite_y, 400, 700, (400, 200, 700, 300)), 
                               (200, 450-self.prisoner_sprite_y, 50, 350, (50, 350, 350, 450)), 
                               (550, 450-self.prisoner_sprite_y, 400, 700, (400, 350, 700, 450)), 
                               (200, 600-self.prisoner_sprite_y, 50, 350, (50, 500, 350, 600)), 
                               (550, 600-self.prisoner_sprite_y, 400, 700, (400, 500, 700, 600))]
        self.prisoner_mapping = {(0, 0): 0, (1, 0): 1, (0, 1): 2,
                                 (1, 1): 3, (0, 2): 4, (1, 2): 5, (0, 3): 6, (1, 3): 7}
        for p in prisoner_spawn_locs:
            x, y, l, r, u = p
            self.prisoners.append(self.create_prisoner(
                x + random.randint(-20, 20), y, l, r, u))

        sprite = 0
        for p in self.prisoners:
            p.set_sprite(self.sprite_list[sprite])
            sprite = (sprite + 1) % len(self.sprite_list)

        self.screen.blit(self.background, (0, 0))
        self.render()
        self.render()

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

    def reward(self):
        return dict(zip(self.agents, self.last_rewards))

    # returns reward of hitting both sides of room, 0 if not
    def move_prisoner(self, prisoner_id, movement):
        prisoner = self.prisoners[prisoner_id]
        if not np.isscalar(movement):
            movement = movement[0]
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

    def close(self):
        pygame.event.pump()
        pygame.display.quit()
        pygame.quit()

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        for k in self.walls:
            pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(k))

        for p in self.prisoners:
            self.screen.blit(p.get_sprite(), p.position)

        # self.space.debug_draw(self.options)

    def observe(self, agent):
        if self.vector_obs:
            
            p = self.prisoners[agent]
            x = p.position[0]
            obs = np.array([x-p.left_bound,p.right_bound - x])
            return obs
        else:
            capture = pygame.surfarray.array3d(self.screen)
            p = self.prisoners[agent]
            x1, y1, x2, y2 = p.window
            sub_screen = np.array(capture[x1:x2,y1:y2, :])
            print(sub_screen.shape)
            return sub_screen

    def reset(self, observe=True):
        self.num_frames = 0
        self.done_val = False
        prisoner_spawn_locs = [(200, 150-self.prisoner_sprite_y, 50, 350, (50, 50, 350, 150)), (550, 150-self.prisoner_sprite_y, 400, 700, (400, 50, 700, 150)), (200, 300-self.prisoner_sprite_y, 50, 350, (50, 200, 350, 300)),(550, 300-self.prisoner_sprite_y, 400, 700, (400, 200, 700, 300)), (200, 450-self.prisoner_sprite_y, 50, 350, (50, 350, 350, 450)), (550, 450-self.prisoner_sprite_y, 400, 700, (400, 350, 700, 450)), (200, 600-self.prisoner_sprite_y, 50, 350, (50, 500, 350, 600)), (550, 600-self.prisoner_sprite_y, 400, 700, (400, 500, 700, 600))]
        self.agent_selector_obj.reinit(self.agent_order)
        self.agent_selection = self.agent_selector_obj.next()
        for i in self.agents:
            p = self.prisoners[i]
            x, y, l, r, u = prisoner_spawn_locs[i]
            p.position = (x + random.randint(-20,20), y)
        self.last_rewards = [0 for _ in self.agents]
        if observe:
            return self.observe(self.agent_selection)
        

    def step(self, action, observe=True):
        # move prisoners, -1 = move left, 0 = do  nothing and 1 is move right
        agent = self.agent_selection
        # if not continuous, input must be normalized
        reward = 0
        if action != None:
            if action != 0 and not self.continuous:
                action = action/abs(action)
            reward = self.move_prisoner(agent, action)
        else:
            print("Error, received null action")
            action = 0

        #set the sprite state to action normalized
        if action != 0:
            self.prisoners[agent].set_state(action/abs(action))
        else:
            self.prisoners[agent].set_state(0)
        
        self.rewards[agent] = reward
        self.clock.tick(15)
        #self.draw()

        self.num_frames += 1
        if (self.num_frames >= 500):
            self.done_val = True
            for d in self.dones:
                self.dones[d] = True

        self.agent_selection = self.agent_selector_obj.next()
        observation = self.observe(self.agent_selection)

        if observe:
            return observation

    def render(self, mode='human'):
        self.draw()
        pygame.display.flip()

from .manual_control import manual_control
