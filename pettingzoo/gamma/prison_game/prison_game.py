import pymunk.pygame_util
import pymunk
import pymunkoptions
from ray.rllib.env.multi_agent_env import MultiAgentEnv
import pygame
import os
import random
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
pymunkoptions.options["debug"] = False


def get_image(path):
    from os import path as os_path
    cwd = os_path.dirname(__file__)
    image = pygame.image.load(cwd + '/' + path)
    return image


def within(a, b, diff):
    return abs(a-b) <= diff


class Prisoner:
    def __init__(self, body, goal):
        self.body = body
        self.goal = goal
        self.last_collided = goal


class env(MultiAgentEnv):

    def __init__(self):
        # super(env, self).__init__()
        self.num_agents = 8
        self.agent_list = list(range(0, self.num_agents))

        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((750, 650))
        pymunk.pygame_util.positive_y_is_up = False

        self.background = get_image('background.png')
        self.prisoner_sprite = get_image('prisoner.png')
        self.prisoner_sprite_x = 30
        self.prisoner_sprite_y = 46

        self.space = pymunk.Space(threaded=True)
        self.space.threads = 2
        self.space.gravity = (0.0, 750.0)
        self.space.collision_bias = .0001
        self.space.iterations = 10
        self.velocity = 4

        #self.options = pymunk.pygame_util.DrawOptions(self.screen)
        #self.options.shape_outline_color = (50, 50, 50, 5)
        #self.options.shape_static_color = (100, 100, 100, 10)

        self.walls = []
        self.create_walls(self.space)

        self.prisoners = []
        prisoner_spawn_locs = [(200, 93), (550, 93), (200, 243),
                               (550, 243), (200, 383), (550, 383), (200, 533), (550, 533)]
        self.prisoner_mapping = {(0, 0): 0, (1, 0): 1, (0, 1): 2,
                                 (1, 1): 3, (0, 2): 4, (1, 2): 5, (0, 3): 6, (1, 3): 7}
        for p in prisoner_spawn_locs:
            x, y = p
            g = 0
            if x < 350:
                g = 51 + self.prisoner_sprite_x/2
            else:
                g = 699 - self.prisoner_sprite_x/2
            self.prisoners.append(self.create_prisoner(
                self.space, x + random.randint(-20, 20), y, g))

        self.screen.blit(self.background, (0, 0))

    def create_walls(self, space):
        self.walls = [(0, 0, 50, 700), (350, 0, 50, 700),
                      (700, 0, 50, 700)]
        self.vert_walls = []
        for i in range(5):
            y = 150*i
            self.walls.append((50, y, 300, 50))
            self.walls.append((400, y, 300, 50))

        for wall in self.walls:
            x, y, w, h = wall
            b = pymunk.Body(body_type=pymunk.Body.STATIC)
            b.position = x+w/2, y+h/2
            b_shape = pymunk.Poly.create_box(b, (w, h))
            b_shape.elasticity = 1
            b_shape.collision_type = 2
            space.add(b, b_shape)

    def create_prisoner(self, space, x, y, g):
        prisoner = pymunk.Body(1, pymunk.inf)
        prisoner.position = x + self.prisoner_sprite_x/2, y + self.prisoner_sprite_y/2
        shape = pymunk.Poly.create_box(
            prisoner, (self.prisoner_sprite_x, self.prisoner_sprite_y))
        shape.elasticity = 0
        shape.collision_type = 1
        space.add(prisoner, shape)
        return Prisoner(prisoner, g)

    # returns reward of hitting both sides of room, 0 if not
    def move_prisoner(self, prisoner_id, dir):
        prisoner = self.prisoners[prisoner_id]
        prisoner.body.position = (
            prisoner.body.position[0] + dir*self.velocity, prisoner.body.position[1])
        reward = 0
        if within(prisoner.body.position[0], prisoner.goal, 2):
            if prisoner.last_collided != prisoner.goal:
                reward = 1
                prisoner.last_collided = prisoner.goal
        elif within(prisoner.body.position[0], 350 - self.prisoner_sprite_x/2, 2) or within(prisoner.body.position[0], 400 + self.prisoner_sprite_x/2, 2):
            prisoner.last_collided = 0
        return reward

    def convert_coord_to_prisoner_id(self, c):
        return self.prisoner_mapping[c]

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        for k in self.walls:
            pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(k))

        for p in self.prisoners:
            x, y = p.body.position
            pnew = (x - self.prisoner_sprite_x/2, y - self.prisoner_sprite_y/2)
            self.screen.blit(self.prisoner_sprite, pnew)

        # self.space.debug_draw(self.options)

    def step(self, actions):
        # move prisoners, -1 = move left, 0 = do  nothing and 1 is move right
        reward_list = []
        action_list = list(actions.values())
        for i in range(0, 8):
            r = self.move_prisoner(i, action_list[i])
            reward_list.append(r)
        self.space.step(1/15.0)
        self.clock.tick(15)
        self.draw()

        rewards = dict(zip(self.agent_list, reward_list))
        observation = {}
        done = dict(((i, False) for i in self.agent_list))
        info = {}
        return observation, rewards, done, info

    def render(self):
        pygame.display.flip()
