from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
import os
import numpy as np
from gym import spaces
from .manual_control import manual_control
from pettingzoo.utils import wrappers
from gym.utils import seeding
from pettingzoo.utils.conversions import parallel_wrapper_fn
from gym.utils import EzPickle
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame


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
        elif self.last_sprite_movement > 0:
            return self.right_sprite
        elif self.last_sprite_movement < 0:
            return self.left_sprite

    def update_sprite(self, movement):
        if movement != 0:
            self.sprite_timer_on = True
            self.sprite_timer = 0
            self.last_sprite_movement = movement
        if self.sprite_timer_on:
            self.sprite_timer += 1
        if self.sprite_timer > 2:
            self.sprite_timer = 0
            self.sprite_timer_on = False
            self.last_sprite_movement = 0


def env(**kwargs):
    env = raw_env(**kwargs)

    if env.continuous:
        env = wrappers.ClipOutOfBoundsWrapper(env)
    else:
        env = wrappers.AssertOutOfBoundsWrapper(env)

    env = wrappers.OrderEnforcingWrapper(env)
    return env


parallel_env = parallel_wrapper_fn(env)


class raw_env(AECEnv, EzPickle):

    def __init__(self, continuous=False, vector_observation=False, max_cycles=150, num_floors=4, synchronized_start=False, identical_aliens=False, random_aliens=False):
        EzPickle.__init__(self, continuous, vector_observation, max_cycles, num_floors, synchronized_start, identical_aliens, random_aliens)
        num_agents = 2 * num_floors
        self.agents = ["prisoner_" + str(s) for s in range(0, num_agents)]
        self.possible_agents = self.agents[:]
        self._agent_selector = agent_selector(self.agents)
        self.sprite_list = ["sprites/alien", "sprites/drone", "sprites/glowy", "sprites/reptile", "sprites/ufo", "sprites/bunny", "sprites/robot", "sprites/tank"]
        self.sprite_img_heights = [40, 40, 46, 48, 32, 54, 48, 53]
        self.metadata = {'render.modes': ['human', "rgb_array"], 'name': "prison_v3"}
        self.infos = {}
        self.rendering = False
        self.max_cycles = max_cycles
        pygame.init()
        self.clock = pygame.time.Clock()
        self.num_frames = 0
        self.done_val = False
        self.num_floors = num_floors
        self.background = get_image('background.png')
        self.background_append = get_image('background_append.png')
        self.dynamic_background = get_image('blit_background.png')
        self.dynamic_background_append = get_image('blit_background_append.png')
        self.velocity = 24
        self.continuous = continuous
        self.vector_obs = vector_observation
        self.synchronized_start = synchronized_start
        self.identical_aliens = identical_aliens
        if (self.identical_aliens):
            self.random_aliens = False
        else:
            self.random_aliens = random_aliens
        self.seed()
        self.closed = False

        self.action_spaces = {}
        if continuous:
            for a in self.agents:
                self.action_spaces[a] = spaces.Box(low=-self.velocity, high=self.velocity, shape=(1,), dtype=np.float32)
        else:
            for a in self.agents:
                self.action_spaces[a] = spaces.Discrete(3)

        self.observation_spaces = {}
        self.last_observation = {}
        for a in self.agents:
            self.last_observation[a] = None
            if vector_observation:
                self.observation_spaces[a] = spaces.Box(low=-300, high=300, shape=(1,), dtype=np.float32)
            else:
                self.observation_spaces[a] = spaces.Box(low=0, high=255, shape=(100, 300, 3), dtype=np.uint8)
        self.state_space = spaces.Box(low=0, high=255, shape=(650, 750, 3), dtype=np.uint8)

        self.walls = []
        self.create_walls(num_floors)

        self.spawn_prisoners()
        self.has_reset = False

        self.reinit()

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)

    def create_walls(self, num_floors):
        self.walls = [(0, 0, 50, 700), (350, 0, 50, 700),
                      (700, 0, 50, 700)]
        # roof of prison
        self.walls.append((50, 0, 300, 50))
        self.walls.append((400, 0, 300, 50))
        for i in range(num_floors):
            y = 150 * (i + 1)
            self.walls.append((50, y, 300, 50))
            self.walls.append((400, y, 300, 50))

    def spawn_prisoners(self):

        chosen_sprites_imgs = []
        chosen_sprites_heights = []
        # possible sprite configurations are, identical_aliens, random_aliens or neither
        if self.identical_aliens:
            # randomly chosen sprite used for all aliens
            sprite_id = self.np_random.randint(0, len(self.sprite_list))
            for s in range(self.num_agents):
                chosen_sprites_imgs.append(self.sprite_list[sprite_id])
                chosen_sprites_heights.append(self.sprite_img_heights[sprite_id])
        elif self.random_aliens:
            # randomly choose sprite for each agent
            for s in range(self.num_agents):
                sprite_id = self.np_random.randint(0, len(self.sprite_list))
                chosen_sprites_imgs.append(self.sprite_list[sprite_id])
                chosen_sprites_heights.append(self.sprite_img_heights[sprite_id])
        else:
            # cycle through each sprite and assign to agent
            p = 0
            for s in range(self.num_agents):
                chosen_sprites_imgs.append(self.sprite_list[p])
                chosen_sprites_heights.append(self.sprite_img_heights[p])
                p = (p + 1) % len(self.sprite_list)

        self.prisoners = {}
        prisoner_spawn_locs = []
        self.prisoner_mapping = {}
        map_count = 0
        for f in range(self.num_floors):
            spawn_y = 150 * (f + 1)
            first_view_window = (50, 50 + 150 * f, 350, 150 + 150 * f)
            second_view_window = (400, 50 + 150 * f, 700, 150 + 150 * f)
            prisoner_spawn_locs.append((200, spawn_y, 50, 350, first_view_window))
            prisoner_spawn_locs.append((550, spawn_y, 400, 700, second_view_window))
            map_tuple_0 = (0, f)
            map_tuple_1 = (1, f)
            self.prisoner_mapping[map_tuple_0] = map_count
            self.prisoner_mapping[map_tuple_1] = map_count + 1
            prisoner0_name = "prisoner_" + str(map_count)
            prisoner1_name = "prisoner_" + str((map_count + 1))
            self.infos[prisoner0_name] = {"map_tuple": map_tuple_0}
            self.infos[prisoner1_name] = {"map_tuple": map_tuple_1}
            map_count += 2
        p_count = 0
        for p in prisoner_spawn_locs:
            agent_name = self.agents[p_count]
            x_pos, y_pos, l_bound, r_bound, view_window = p
            x_noise = 0
            if not self.synchronized_start:
                x_noise = self.np_random.randint(-20, 20 + 1)
            self.prisoners[agent_name] = self.create_prisoner(
                x_pos + x_noise, y_pos - chosen_sprites_heights[p_count], l_bound, r_bound, view_window, agent_name)
            self.prisoners[agent_name].set_sprite(chosen_sprites_imgs[p_count])
            p_count += 1

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
        if not self.closed:
            self.closed = True
            if self.rendering:
                pygame.event.pump()
                pygame.display.quit()
            pygame.quit()

    def draw(self):
        for k in range(self.num_floors):
            h = 50 + 150 * k
            self.screen.blit(self.dynamic_background_append, (50, h))
        for p in self.prisoners:
            self.screen.blit(self.prisoners[p].get_sprite(), self.prisoners[p].position)

    def observe(self, agent):
        if self.vector_obs:
            p = self.prisoners[agent]
            x = p.position[0]
            obs = [x - p.left_bound]
            return np.array(obs, dtype=np.float32)
        else:
            capture = pygame.surfarray.pixels3d(self.screen)
            p = self.prisoners[agent]
            x1, y1, x2, y2 = p.window
            sub_screen = np.array(capture[x1:x2, y1:y2, :])
            sub_screen = np.rot90(sub_screen, k=3)
            sub_screen = np.fliplr(sub_screen)
            return sub_screen

    def state(self):
        '''
        Returns an observation of the global environment
        '''
        state = pygame.surfarray.pixels3d(self.screen).copy()
        state = np.rot90(state, k=3)
        state = np.fliplr(state)
        return state

    def reinit(self):
        self.done_val = False
        self.num_frames = 0
        self.last_rewards = [0 for _ in self.agents]
        self.frames = 0
        self.rendering = False
        self.screen = pygame.Surface((750, 50 + 150 * self.num_floors))
        self.screen.blit(self.background, (0, 0))
        self.rendering = False

    def reset(self):
        self.has_reset = True
        self.agents = self.possible_agents[:]
        self.rewards = dict(zip(self.agents, [0 for _ in self.agents]))
        self._cumulative_rewards = dict(zip(self.agents, [0 for _ in self.agents]))
        self.dones = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [{} for _ in self.agents]))
        self._agent_selector.reinit(self.agents)
        self.agent_selection = self._agent_selector.next()
        self.num_frames = 0
        self.reinit()
        self.spawn_prisoners()
        self.draw()

    def step(self, action):
        if self.dones[self.agent_selection]:
            return self._was_done_step(action)
        # move prisoners, -1 = move left, 0 = do  nothing and 1 is move right
        if not isinstance(action, int):
            action = np.asarray(action)
        agent = self.agent_selection
        reward = 0
        if self.continuous:
            reward = self.move_prisoner(agent, action)
        else:
            reward = self.move_prisoner(agent, action - 1)

        # set the sprite state to action normalized
        if action != 0:
            self.prisoners[agent].set_state(action / abs(action))
        else:
            self.prisoners[agent].set_state(0)

        self._clear_rewards()
        self.rewards[agent] = reward

        if self._agent_selector.is_last():
            self.num_frames += 1

        if (self.num_frames >= self.max_cycles):
            self.done_val = True
            for d in self.dones:
                self.dones[d] = True
        if self._agent_selector.is_last():
            self.draw()
        if self.rendering:
            pygame.event.pump()

        self.agent_selection = self._agent_selector.next()
        self._cumulative_rewards[agent] = 0
        self._accumulate_rewards()

    def render(self, mode='human'):
        if not self.rendering and mode == "human":
            pygame.display.init()
            old_screen = self.screen
            self.screen = pygame.display.set_mode((750, 50 + 150 * self.num_floors))
            self.screen.blit(old_screen, (0, 0))
            self.screen.blit(self.background, (0, 0))
            if self.num_floors > 4:
                min_rows = self.num_floors - 4
                for k in range(min_rows):
                    h = 650 + 150 * k
                    self.screen.blit(self.background_append, (0, h))
            self.rendering = True

        observation = np.array(pygame.surfarray.pixels3d(self.screen))
        if mode == "human":
            pygame.display.flip()
        return np.transpose(observation, axes=(1, 0, 2)) if mode == "rgb_array" else None


# Sprites other than bunny and tank purchased from https://nebelstern.itch.io/futura-seven
# Tank and bunny sprites commissioned from https://www.fiverr.com/jeimansutrisman
# Art other than sprites created by Niall Williams
