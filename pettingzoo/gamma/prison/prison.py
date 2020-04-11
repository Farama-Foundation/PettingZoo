from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
import pygame
import os
import numpy as np
import random
from gym import spaces
from .manual_control import manual_control
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'


def get_image(path):
    from os import path as os_path
    cwd = os_path.dirname(__file__)
    image = pygame.image.load(cwd + '/' + path)
    return image


def within(a, b, diff):
    return abs(a - b) <= diff


class Prisoner:
    def __init__(self, p, l, r, w, name):
        self.position = p
        self.left_bound = l
        self.right_bound = r
        self.window = w
        self.name = name
        self.first_touch = -1  # rewarded on touching bound != first_touch
        self.last_touch = -1  # to track last touched wall
        self.still_sprite = None
        self.left_sprite = None
        self.right_sprite = None
        self.state = 0
        self.sprite_timer_on = False
        self.last_sprite_movement = 0
        self.sprite_timer = 0  # if the agent hasn't moved left or right in X frames, set sprite to "still"

    def set_sprite(self, s):
        self.still_sprite = get_image(s + "_still.png")
        self.left_sprite = get_image(s + "_left.png")
        self.right_sprite = get_image(s + "_right.png")
        self.right_bound -= self.right_sprite.get_width()

    def set_state(self, st):
        self.state = st

    def get_sprite(self):
        if self.last_sprite_movement == 0:
            return self.still_sprite
        elif self.last_sprite_movement == 1:
            return self.right_sprite
        elif self.last_sprite_movement == -1:
            return self.left_sprite
        else:
            print("INVALID STATE", self.state)
            return self.still_sprite

    def update_sprite(self, movement):
        if movement != 0:
            self.sprite_timer_on = True
            self.sprite_timer = 0
            self.last_sprite_movement = movement
        if self.sprite_timer_on:
            self.sprite_timer += 1
        if self.sprite_timer > 2:  # FIXME: change the number here if you want the left/right sprite to last longer on screen after moving to either direction
            self.sprite_timer = 0
            self.sprite_timer_on = False
            self.last_sprite_movement = 0


class env(AECEnv):

    def __init__(self, continuous=False, vector_observation=False, max_frames=900):
        # super(env, self).__init__()
        self.num_agents = 8
        self.agents = ["prisoner_" + str(s) for s in range(0, 8)]
        self.agent_order = self.agents[:]
        self._agent_selector = agent_selector(self.agent_order)
        self.sprite_list = ["sprites/alien", "sprites/drone", "sprites/glowy", "sprites/reptile", "sprites/ufo", "sprites/bunny", "sprites/robot", "sprites/tank"]
        self.metadata = {'render.modes': ['human']}
        self.rendering = False
        self.max_frames = max_frames
        pygame.init()
        self.clock = pygame.time.Clock()
        self.num_frames = 0
        self.done_val = False

        self.background = get_image('background.png')

        self.velocity = 8
        self.continuous = continuous
        self.vector_obs = vector_observation

        self.action_spaces = {}
        if continuous:
            for a in self.agents:
                self.action_spaces[a] = spaces.Box(low=np.NINF, high=np.Inf, shape=(1,), dtype=np.float32)
        else:
            for a in self.agents:
                self.action_spaces[a] = spaces.Box(low=-1, high=1, shape=(1,), dtype=np.int8)

        self.observation_spaces = {}
        self.last_observation = {}
        for a in self.agents:
            self.last_observation[a] = None
            if vector_observation:
                self.observation_spaces[a] = spaces.Box(low=-300, high=300, shape=(1,), dtype=np.float32)
            else:
                self.observation_spaces[a] = spaces.Box(low=0, high=255, shape=(100, 300, 3), dtype=np.uint8)

        self.walls = []
        self.create_walls()

        self.prisoners = {}
        prisoner_spawn_locs = [(200, 150 - 40, 50, 350, (50, 50, 350, 150)),
                               (550, 150 - 40, 400, 700, (400, 50, 700, 150)),
                               (200, 300 - 46, 50, 350, (50, 200, 350, 300)),
                               (550, 300 - 48, 400, 700, (400, 200, 700, 300)),
                               (200, 450 - 32, 50, 350, (50, 350, 350, 450)),
                               (550, 450 - 54, 400, 700, (400, 350, 700, 450)),
                               (200, 600 - 48, 50, 350, (50, 500, 350, 600)),
                               (550, 600 - 53, 400, 700, (400, 500, 700, 600))]
        self.prisoner_mapping = {(0, 0): 0, (1, 0): 1, (0, 1): 2,
                                 (1, 1): 3, (0, 2): 4, (1, 2): 5, (0, 3): 6, (1, 3): 7}
        p_count = 0
        for p in prisoner_spawn_locs:
            x, y, l, r, u = p
            self.prisoners[self.agents[p_count]] = self.create_prisoner(
                x + random.randint(-20, 20), y, l, r, u, self.agents[p_count])
            p_count += 1

        sprite = 0
        for p in self.prisoners:
            self.prisoners[p].set_sprite(self.sprite_list[sprite])
            sprite = (sprite + 1) % len(self.sprite_list)

        self.reinit()

    def create_walls(self):
        self.walls = [(0, 0, 50, 700), (350, 0, 50, 700),
                      (700, 0, 50, 700)]
        self.vert_walls = []
        for i in range(5):
            y = 150 * i
            self.walls.append((50, y, 300, 50))
            self.walls.append((400, y, 300, 50))

    def create_prisoner(self, x, y, l, r, u, nam):
        return Prisoner((x, y), l, r, u, nam)

    def reward(self):
        return dict(zip(self.agents, self.last_rewards))

    # returns reward of hitting both sides of room, 0 if not
    def move_prisoner(self, prisoner_id, movement):
        prisoner = self.prisoners[prisoner_id]
        if not np.isscalar(movement):
            movement = movement[0]
        prisoner.update_sprite(movement)
        if self.continuous:
            prisoner.position = (
                prisoner.position[0] + movement, prisoner.position[1])
        else:
            prisoner.position = (
                prisoner.position[0] + movement * self.velocity, prisoner.position[1])
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
        if self.rendering:
            pygame.event.pump()
            pygame.display.quit()
        pygame.quit()

    def draw(self):
        dynamic_background = get_image('blit_background.png')
        self.screen.blit(dynamic_background, (0, 0))
        for p in self.prisoners:
            self.screen.blit(self.prisoners[p].get_sprite(), self.prisoners[p].position)

    def observe(self, agent):
        if self.vector_obs:
            p = self.prisoners[agent]
            x = p.position[0]
            obs = [x - p.left_bound]
            return obs
        else:
            capture = pygame.surfarray.pixels3d(self.screen)
            p = self.prisoners[agent]
            x1, y1, x2, y2 = p.window
            sub_screen = np.array(capture[x1:x2, y1:y2, :])
            sub_screen = np.rot90(sub_screen, k=3)
            sub_screen = np.fliplr(sub_screen)
            return sub_screen

    def reinit(self):
        self.rewards = dict(zip(self.agents, [0 for _ in self.agents]))
        self.dones = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [{} for _ in self.agents]))
        self.done_val = False
        self.num_frames = 0
        self._agent_selector.reinit(self.agent_order)
        self.agent_selection = self._agent_selector.next()
        self.last_rewards = [0 for _ in self.agents]
        self.frames = 0
        self.rendering = False
        self.screen = pygame.Surface((750, 650))
        self.screen.blit(self.background, (0, 0))
        self.rendering = False

    def reset(self, observe=True):
        self.num_frames = 0
        self.reinit()

        prisoner_spawn_locs = [(200, 150 - 40, 50, 350, (50, 50, 350, 150)),
                               (550, 150 - 40, 400, 700, (400, 50, 700, 150)),
                               (200, 300 - 46, 50, 350, (50, 200, 350, 300)),
                               (550, 300 - 48, 400, 700, (400, 200, 700, 300)),
                               (200, 450 - 32, 50, 350, (50, 350, 350, 450)),
                               (550, 450 - 54, 400, 700, (400, 350, 700, 450)),
                               (200, 600 - 48, 50, 350, (50, 500, 350, 600)),
                               (550, 600 - 53, 400, 700, (400, 500, 700, 600))]
        p_count = 0
        for i in self.agents:
            p = self.prisoners[i]
            x, y, l, r, u = prisoner_spawn_locs[p_count]
            p.position = (x + random.randint(-20, 20), y)
            p_count += 1
        if observe:
            return self.observe(self.agent_selection)

    def step(self, action, observe=True):
        # move prisoners, -1 = move left, 0 = do  nothing and 1 is move right
        agent = self.agent_selection
        # if not continuous, input must be normalized
        reward = 0
        if action is not None:
            if action != 0 and not self.continuous:
                action = action / abs(action)
            reward = self.move_prisoner(agent, action)
        else:
            action = 0

        # set the sprite state to action normalized
        if action != 0:
            self.prisoners[agent].set_state(action / abs(action))
        else:
            self.prisoners[agent].set_state(0)

        self.rewards[agent] = reward
        if self.rendering:
            self.clock.tick(30)
        else:
            self.clock.tick()

        self.num_frames += 1
        if (self.num_frames >= self.max_frames):
            self.done_val = True
            for d in self.dones:
                self.dones[d] = True
        if self._agent_selector.is_last():
            self.draw()
        if self.rendering:
            pygame.event.pump()

        self.agent_selection = self._agent_selector.next()
        observation = self.observe(self.agent_selection)

        if observe:
            return observation

    def render(self, mode='human'):
        if not self.rendering:
            pygame.display.init()
            self.screen = pygame.display.set_mode((750, 650))
            self.screen.blit(self.background, (0, 0))
        self.rendering = True
        pygame.display.flip()

# Sprites other than bunny and tank purchased from https://nebelstern.itch.io/futura-seven
# Tank and bunny sprites commissioned from https://www.fiverr.com/jeimansutrisman
# Art other than sprites created by Niall Williams
