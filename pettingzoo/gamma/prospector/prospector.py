import pygame as pg
import pymunk as pm
from pymunk import Vec2d
from gym import spaces
from gym.utils import seeding
import numpy as np

from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
from pettingzoo.utils import wrappers
from . import constants as const
from . import utils
from .manual_control import manual_control

import math
import os
from enum import IntEnum, auto
import itertools as it


class CollisionTypes(IntEnum):
    PROSPECTOR = auto()
    BOUNDARY = auto()
    WATER = auto()
    BANK = auto()
    GOLD = auto()
    BANKER = auto()


class Prospector(pg.sprite.Sprite):
    def __init__(self, pos, space, num, *sprite_groups):
        super().__init__(sprite_groups)
        # self.image = load_image(['prospec.png'])
        self.image = utils.load_image(["prospector-pickaxe-big.png"])
        self.image = pg.transform.scale(
            self.image, (int(const.AGENT_RADIUS * 2), int(const.AGENT_RADIUS * 2))
        )

        self.id = num

        self.rect = self.image.get_rect(topleft=pos)
        self.orig_image = self.image

        # Create the physics body and shape of this object.
        # moment = pm.moment_for_poly(mass, vertices)

        moment = pm.moment_for_circle(1, 0, self.rect.width / 2)

        self.body = pm.Body(1, moment)
        self.body.nugget = None
        self.body.sprite_type = "prospector"
        # self.shape = pm.Poly(self.body, vertices, radius=3)

        self.shape = pm.Circle(self.body, const.AGENT_RADIUS)
        self.shape.elasticity = 0.0
        self.shape.collision_type = CollisionTypes.PROSPECTOR

        self.body.position = utils.flipy(pos)
        # Add them to the Pymunk space.
        self.space = space
        self.space.add(self.body, self.shape)

    def reset(self, pos):
        self.body.angle = 0
        self.image = pg.transform.rotozoom(self.orig_image, 0, 1)
        self.rect = self.image.get_rect(topleft=pos)
        self.body.position = utils.flipy(pos)
        self.body.velocity = Vec2d(0.0, 0.0)

    @property
    def center(self):
        return self.rect.x + const.AGENT_RADIUS, self.rect.y + const.AGENT_RADIUS

    def update(self, action):
        # forward/backward action
        y_vel = action[0] * const.PROSPECTOR_SPEED
        # left/right action
        x_vel = action[1] * const.PROSPECTOR_SPEED

        delta_angle = action[2] * const.MAX_SPRITE_ROTATION

        self.body.angle += delta_angle
        self.body.angular_velocity = 0

        self.body.velocity = Vec2d(x_vel, y_vel).rotated(self.body.angle)

        self.rect.center = utils.flipy(self.body.position)
        self.image = pg.transform.rotozoom(
            self.orig_image, math.degrees(self.body.angle), 1
        )
        self.rect = self.image.get_rect(center=self.rect.center)

        curr_vel = self.body.velocity

        if self.body.nugget is not None:
            self.body.nugget.update(self.body.position, self.body.angle, False)

        self.body.velocity = curr_vel

    def convert_img(self):
        self.image = self.image.convert_alpha()

    def __str__(self):
        return "prospector_%s" % self.id

    def __repr__(self):
        return self.__str__()


class Banker(pg.sprite.Sprite):
    def __init__(self, pos, space, num, *sprite_groups):
        super().__init__(sprite_groups)
        self.image = utils.load_image(["bankers", "%s-big.png" % num])
        self.image = pg.transform.scale(
            self.image, (int(const.AGENT_RADIUS * 2), int(const.AGENT_RADIUS * 2))
        )

        self.id = num

        self.rect = self.image.get_rect(topleft=pos)
        self.orig_image = self.image

        moment = pm.moment_for_circle(1, 0, self.rect.width / 2)

        self.body = pm.Body(1, moment)
        self.body.nugget = None
        self.body.sprite_type = "banker"
        self.body.nugget_offset = None

        self.shape = pm.Circle(self.body, const.AGENT_RADIUS)
        self.shape.collision_type = CollisionTypes.BANKER

        self.body.position = utils.flipy(pos)
        # Add them to the Pymunk space.
        self.space = space
        self.space.add(self.body, self.shape)

    @property
    def center(self):
        return self.rect.x + const.AGENT_RADIUS, self.rect.y + const.AGENT_RADIUS

    def reset(self, pos):
        self.body.angle = 0
        self.image = pg.transform.rotozoom(self.orig_image, 0, 1)
        self.rect = self.image.get_rect(topleft=pos)
        self.body.position = utils.flipy(pos)
        self.body.velocity = Vec2d(0.0, 0.0)

    def update(self, action):
        # up/down action
        y_vel = action[0] * const.BANKER_SPEED
        # left/right action
        x_vel = action[1] * const.BANKER_SPEED

        # Subtract math.pi / 2 because sprite starts off with math.pi / 2 rotated
        angle_radians = math.atan2(y_vel, x_vel) - (math.pi / 2)

        # Angle is determined only by current trajectory.
        self.body.angle = angle_radians
        self.body.angular_velocity = 0

        self.body.velocity = Vec2d(x_vel, y_vel)

        self.rect.center = utils.flipy(self.body.position)
        self.image = pg.transform.rotozoom(
            self.orig_image, math.degrees(self.body.angle), 1
        )
        self.rect = self.image.get_rect(center=self.rect.center)

        curr_vel = self.body.velocity

        if self.body.nugget is not None:
            self.body.nugget.update(self.body.position, self.body.angle, False)

        self.body.velocity = curr_vel

    def convert_img(self):
        self.image = self.image.convert_alpha()

    def __str__(self):
        return "banker_%s" % self.id

    def __repr__(self):
        return self.__str__()


class Fence(pg.sprite.Sprite):
    def __init__(self, w_type, sprite_pos, body_pos, verts, space, *sprite_groups):
        super().__init__(sprite_groups)

        if w_type == "top":
            # self.image = utils.load_image(["horiz-fence.png"])
            self.image = utils.load_image(["top-down-horiz-fence.png"])
        elif w_type in ["right", "left"]:
            # self.image = utils.load_image(["vert-fence.png"])
            self.image = utils.load_image(["top-down-vert-fence.png"])
        else:
            raise ValueError("Fence image not found! Check the spelling")
        # elif w_type == "left":
        #     # self.image = utils.load_image(["vert-fence.png"])
        #     self.image = utils.load_image(["top-down-vert-fence.png"])

        self.rect = self.image.get_rect(topleft=sprite_pos)

        self.body = pm.Body(body_type=pm.Body.STATIC)

        # Transform pygame vertices to fit Pymunk body
        invert_verts = utils.invert_y(verts)
        self.shape = pm.Poly(self.body, invert_verts)
        self.shape.elasticity = 0.0
        self.shape.collision_type = CollisionTypes.BOUNDARY

        self.body.position = utils.flipy(body_pos)
        space.add(self.shape)

    def convert_img(self):
        self.image = self.image.convert_alpha()


class Water(pg.sprite.Sprite):
    def __init__(self, pos, verts, space, *sprite_groups):
        super().__init__(*sprite_groups)
        # Determine the width and height of the surface.
        self.image = utils.load_image(["water.png"])
        self.image = pg.transform.scale(
            self.image, (const.SCREEN_WIDTH, const.WATER_HEIGHT)
        )

        self.rect = self.image.get_rect(topleft=pos)

        self.body = pm.Body(body_type=pm.Body.STATIC)

        # Transform pygame vertices to fit Pymunk body
        invert_verts = utils.invert_y(verts)
        self.shape = pm.Poly(self.body, invert_verts)
        self.shape.collision_type = CollisionTypes.WATER

        # self.shape.friction = 1.0
        self.body.position = utils.flipy(pos)
        self.space = space
        self.space.add(self.shape)

    def convert_img(self):
        self.image = self.image.convert_alpha()


class Bank(pg.sprite.Sprite):
    def __init__(self, pos, verts, space, *sprite_groups):
        super().__init__(sprite_groups)

        self.image = utils.load_image(["bank-2.png"])
        self.image = pg.transform.scale(self.image, (184, 100))
        self.rect = self.image.get_rect(topleft=pos)

        self.body = pm.Body(body_type=pm.Body.STATIC)

        invert_verts = utils.invert_y(verts)
        self.shape = pm.Poly(self.body, invert_verts)
        self.shape.collision_type = CollisionTypes.BANK

        self.body.position = utils.flipy(pos)
        self.space = space
        self.space.add(self.shape, self.body)

    def convert_img(self):
        self.image = self.image.convert_alpha()


class Gold(pg.sprite.Sprite):
    ids = it.count(0)

    def __init__(self, pos, body, space, *sprite_groups):
        super().__init__(sprite_groups)
        self.id = next(self.ids)

        self.image = utils.load_image(["gold", "6.png"])
        self.image = pg.transform.scale(self.image, (16, 16))
        self.orig_image = self.image

        self.rect = self.image.get_rect()

        self.moment = pm.moment_for_circle(1, 0, 8)
        self.body = pm.Body(1, self.moment)
        self.body.position = body.position

        self.shape = pm.Circle(self.body, 8)
        self.shape.collision_type = CollisionTypes.GOLD
        self.shape.id = self.id

        self.space = space
        self.space.add(self.body, self.shape)

        self.initial_angle = body.angle - Vec2d(0, -1).angle
        self.parent_body = body

    def update(self, pos, angle, banker: bool):

        if banker:
            new_angle = angle
        else:
            new_angle = angle - self.initial_angle
        new_pos = pos + Vec2d(const.AGENT_RADIUS + 9, 0).rotated(new_angle)

        self.body.position = new_pos
        self.body.angular_velocity = 0
        self.rect.center = utils.flipy(self.body.position)
        self.image = pg.transform.rotozoom(
            self.orig_image, math.degrees(self.body.angle), 1
        )
        self.rect = self.image.get_rect(center=self.rect.center)

    def convert_img(self):
        self.image = self.image.convert_alpha()


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.ClipOutOfBoundsWrapper(env)
    env = wrappers.NanNoOpWrapper(env, [0, 0, 0], "setting action to 0")
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(AECEnv):
    def __init__(
        self,
        ind_reward=0.8,
        group_reward=0.1,
        other_group_reward=0.1,
        prospec_find_gold_reward=1,
        prospec_handoff_gold_reward=1,
        banker_receive_gold_reward=1,
        banker_deposit_gold_reward=1,
        max_frames=900,
        seed=None,
    ):
        if ind_reward + group_reward + other_group_reward != 1.0:
            raise ValueError(
                "Individual reward, group reward, and other group reward should "
                "add up to 1.0"
            )

        self.num_agents = const.NUM_AGENTS
        # self.agents = list(range(0, self.num_agents))
        self.agents = []

        self.sprite_list = [
            "bankers/1-big.png",
            "bankers/2-big.png",
            "bankers/3-big.png",
            "prospector-pickaxe-big.png",
        ]
        self.rendering = False
        self.max_frames = max_frames
        self.frame = 0

        pg.init()
        self.rng, seed = seeding.np_random(seed)
        self.screen = pg.Surface(const.SCREEN_SIZE)
        self.clock = pg.time.Clock()
        self.done = False
        self.closed = False

        self.background = utils.load_image(["background-debris.png"])
        self.background_rect = pg.Rect(0, 0, *const.SCREEN_SIZE)
        self.screen.blit(self.background, self.background_rect)

        self.space = pm.Space()
        self.space.gravity = Vec2d(0.0, 0.0)
        self.space.damping = 0.0

        # self.all_sprites = pg.sprite.Group()
        self.all_sprites = pg.sprite.RenderUpdates()
        self.gold = []

        # Generate random positions for each prospector agent
        prospector_info = [
            (i, utils.rand_pos("prospector", self.rng)) for i in range(const.NUM_PROSPECTORS)
        ]
        self.prospectors = {}
        for num, pos in prospector_info:
            prospector = Prospector(pos, self.space, num, self.all_sprites)
            identifier = f"prospector_{num}"
            self.prospectors[identifier] = prospector
            self.agents.append(identifier)

        banker_info = [(i, utils.rand_pos("banker", self.rng)) for i in range(const.NUM_BANKERS)]
        self.bankers = {}
        for num, pos in banker_info:
            banker = Banker(pos, self.space, num, self.all_sprites)
            identifier = f"banker_{num}"
            self.bankers[identifier] = banker
            self.agents.append(identifier)

        self.banks = []
        for pos, verts in const.BANK_INFO:
            self.banks.append(Bank(pos, verts, self.space, self.all_sprites))

        for w_type, s_pos, b_pos, verts in const.FENCE_INFO:
            Fence(w_type, s_pos, b_pos, verts, self.space, self.all_sprites)

        Water(const.WATER_INFO[0], const.WATER_INFO[1], self.space, self.all_sprites)

        self.metadata = {"render.modes": ["human"]}

        self.action_spaces = {}
        for p in self.prospectors:
            self.action_spaces[p] = spaces.Box(low=np.float32(-1.), high=np.float32(1.), shape=(3,))

        for b in self.bankers:
            self.action_spaces[b] = spaces.Box(low=np.float32(-1.), high=np.float32(1.), shape=(3,))

        self.observation_spaces = {}
        self.last_observation = {}
        for a in self.agents:
            self.last_observation[a] = None
            # low, high for RGB values
            self.observation_spaces[a] = spaces.Box(
                low=0, high=255, shape=const.OBSERVATION_SHAPE, dtype=np.uint8
            )

        self.agent_order = self.agents[:]
        self._agent_selector = agent_selector(self.agent_order)
        self.agent_selection = self._agent_selector.next()
        self.reset()

        # Collision Handler Functions --------------------------------------------
        # Water to Prospector
        def add_gold(arbiter, space, data):
            prospec_shape = arbiter.shapes[0]
            prospec_body = prospec_shape.body

            position = arbiter.contact_point_set.points[0].point_a
            normal = arbiter.contact_point_set.normal

            prospec_body.position = position - (24 * normal)
            prospec_body.velocity = (0, 0)

            for k, v in self.prospectors.items():
                if v.body is prospec_body:
                    self.rewards[k] += ind_reward * prospec_find_gold_reward
                else:
                    self.rewards[k] += group_reward * prospec_find_gold_reward

            for k in self.bankers:
                self.rewards[k] += other_group_reward * prospec_find_gold_reward

            if prospec_body.nugget is None:
                position = arbiter.contact_point_set.points[0].point_a

                gold = Gold(position, prospec_body, self.space, self.all_sprites)
                self.gold.append(gold)
                prospec_body.nugget = gold

            return True

        # Prospector to banker
        def handoff_gold_handler(arbiter, space, data):
            banker_shape, gold_shape = arbiter.shapes[0], arbiter.shapes[1]

            gold_sprite = None
            for g in self.gold:
                if g.id == gold_shape.id:
                    gold_sprite = g

            # This collision handler is only for prospector -> banker gold handoffs
            if gold_sprite.parent_body.sprite_type != "prospector":
                return True

            banker_body = banker_shape.body
            prospec_body = gold_sprite.parent_body

            for k, v in self.prospectors.items():
                self.rewards[k] += other_group_reward * banker_receive_gold_reward
                if v.body is prospec_body:
                    self.rewards[k] += prospec_handoff_gold_reward
                else:
                    self.rewards[k] += group_reward * prospec_handoff_gold_reward

            for k, v in self.bankers.items():
                self.rewards[k] += other_group_reward * prospec_handoff_gold_reward
                if v.body is banker_body:
                    self.rewards[k] += banker_receive_gold_reward
                else:
                    self.rewards[k] += group_reward * banker_receive_gold_reward

            normal = arbiter.contact_point_set.normal
            # Correct the angle because banker's head is rotated pi/2
            corrected = utils.normalize_angle(banker_body.angle + (math.pi / 2))
            if (
                corrected - const.BANKER_HANDOFF_TOLERANCE
                <= normal.angle
                <= corrected + const.BANKER_HANDOFF_TOLERANCE
            ):
                gold_sprite.parent_body.nugget = None

                gold_sprite.parent_body = banker_body
                banker_body.nugget = gold_sprite
                banker_body.nugget_offset = normal.angle

            return True

        # Banker to bank
        def gold_score_handler(arbiter, space, data):
            gold_shape, _ = arbiter.shapes[0], arbiter.shapes[1]

            for g in self.gold:
                if g.id == gold_shape.id:
                    gold_class = g

            if gold_class.parent_body.sprite_type == "banker":
                self.space.remove(gold_shape, gold_shape.body)
                gold_class.parent_body.nugget = None
                banker_body = gold_class.parent_body

                for k, v in self.bankers.items():
                    if v.body is banker_body:
                        self.rewards[k] += banker_deposit_gold_reward
                        # banker_sprite = v
                    else:
                        self.rewards[k] += group_reward * banker_deposit_gold_reward

                for k in self.prospectors:
                    self.rewards[k] += other_group_reward * banker_deposit_gold_reward

                self.gold.remove(gold_class)
                self.all_sprites.remove(gold_class)

            return False

        # Create the collision event generators
        gold_dispenser = self.space.add_collision_handler(
            CollisionTypes.PROSPECTOR, CollisionTypes.WATER
        )

        gold_dispenser.begin = add_gold

        handoff_gold = self.space.add_collision_handler(
            CollisionTypes.BANKER, CollisionTypes.GOLD
        )

        handoff_gold.begin = handoff_gold_handler

        gold_score = self.space.add_collision_handler(
            CollisionTypes.GOLD, CollisionTypes.BANK
        )

        gold_score.begin = gold_score_handler

    def observe(self, agent):
        capture = pg.surfarray.pixels3d(self.screen)
        if agent in self.prospectors:
            ag = self.prospectors[agent]
        else:
            ag = self.bankers[agent]

        assert ag is not None

        delta = const.OBSERVATION_SIDE_LENGTH // 2
        x, y = ag.center  # Calculated property added to prospector and banker classes
        sub_screen = np.array(capture[
            max(0, x - delta): min(const.SCREEN_WIDTH, x + delta),
            max(0, y - delta): min(const.SCREEN_HEIGHT, y + delta), :], dtype=np.uint8)

        s_x, s_y, _ = sub_screen.shape
        pad_x = const.OBSERVATION_SIDE_LENGTH - s_x
        if x > const.SCREEN_WIDTH - delta:  # Right side of the screen
            sub_screen = np.pad(sub_screen, pad_width=((0, pad_x), (0, 0), (0, 0)), mode='constant')
        elif x < 0 + delta:
            sub_screen = np.pad(sub_screen, pad_width=((pad_x, 0), (0, 0), (0, 0)), mode='constant')

        pad_y = const.OBSERVATION_SIDE_LENGTH - s_y
        if y > const.SCREEN_HEIGHT - delta:  # Bottom of the screen
            sub_screen = np.pad(sub_screen, pad_width=((0, 0), (0, pad_y), (0, 0)), mode='constant')
        elif y < 0 + delta:
            sub_screen = np.pad(sub_screen, pad_width=((0, 0), (pad_y, 0), (0, 0)), mode='constant')

        self.last_observation[agent] = sub_screen

        return sub_screen

    def step(self, action, observe=True):
        agent_id = self.agent_selection

        if agent_id in self.prospectors:
            agent = self.prospectors[agent_id]
        else:
            agent = self.bankers[agent_id]

        agent.update(action)

        all_agents_updated = self._agent_selector.is_last()
        # Only take next step in game if all agents have received an action
        if all_agents_updated:
            if self.rendering:
                self.clock.tick(const.FPS)
            else:
                self.clock.tick()
            self.space.step(1 / const.FPS)

            self.draw()

            self.frame += 1
            # If we reached max frames, we're done
            if self.frame == self.max_frames:
                self.dones = dict(zip(self.agents, [True for _ in self.agents]))

        if self.rendering:
            pg.event.pump()

        self.agent_selection = self._agent_selector.next()

        if observe:
            return self.observe(self.agent_selection)

    def reward(self):
        return self.rewards

    def reset(self, observe=True):
        self.screen = pg.Surface(const.SCREEN_SIZE)
        self.screen.blit(self.background, self.background_rect)
        self.done = False

        for p in self.prospectors.values():
            p.reset(utils.rand_pos("prospector", self.rng))

        for b in self.bankers.values():
            b.reset(utils.rand_pos("banker", self.rng))

        self.rewards = dict(zip(self.agents, [0 for _ in self.agents]))
        self.dones = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [{} for _ in self.agents]))
        self.metadata = {"render.modes": ["human"]}
        self.rendering = False
        self.frame = 0

        self.agent_order = self.agents[:]
        self._agent_selector.reinit(self.agent_order)
        self.agent_selection = self._agent_selector.next()
        self.draw()
        if observe:
            return self.observe(self.agent_selection)

    def render(self, mode="human"):
        if not self.rendering:
            pg.display.init()
            self.screen = pg.display.set_mode(const.SCREEN_SIZE)
            self.background = self.background.convert_alpha()
            self.screen.blit(self.background, self.background_rect)
            for s in self.all_sprites.sprites():
                s.convert_img()
            self.rendering = True
        self.draw()
        pg.display.flip()

    def draw(self):
        self.screen.blit(self.background, self.background_rect)
        self.all_sprites.draw(self.screen)

    def close(self):
        if not self.closed:
            self.closed = True
            if self.rendering:
                pg.event.pump()
                pg.display.quit()
            pg.quit()


# class env(gym.Env):
#     def __init__(self):
#         super().__init__()
#         global agent2, agent1
#         pygame.init()

#         # Set the width and height of the screen [width, height]
#         size = (1002, 699)
#         self.screen = pygame.display.set_mode(size)
#         background = get_image("background.jpg")
#         pygame.display.set_caption("My Game")
#         self.screen.blit(background, (0, 0))
#         self.area = self.screen.get_rect()

#         # Loop until the user clicks the close button.
#         done = False

#         # Used to manage how fast the screen updates
#         clock = pygame.time.Clock()
#         agent1 = agent1(size, x=50, y=50, speed=20)
#         agent2 = agent2(size)

#         block_list, all_sprites_list = self.create_targets()

#         vis = pygame.sprite.Group()  # Visualize block that is being carried by agent 1
#         vis2 = pygame.sprite.Group()  # Visualize block that is being carried by agent 2
#         block_picked = None
#         block_transfered = None
#         flag = 0
#         blocks_hit_list = []
#         # cropped = pygame.Surface((100,100))

#         # -------- Main Program Loop -----------
#         while not done:
#             # --- Main event loop
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     done = True

#             self.screen.blit(background, (0, 0))
#             self.screen.blit(agent1.image, agent1.rect)
#             # cropped.blit(agent1.image, (agent1.rect.x,agent1.rect.y))
#             self.screen.blit(agent2.image, agent2.rect)
#             pos = pygame.mouse.get_pos()
#             agent1.update(pos, self.area, agent2)
#             agent2.update(pos)  # , self.area, agent1)
#             if flag == 0:
#                 blocks_hit_list = pygame.sprite.spritecollide(agent1, block_list, True)
#             pygame.draw.circle(self.screen, RED, agent1.rect.topleft, 5)
#             while len(blocks_hit_list) > 1:
#                 block_list.add(blocks_hit_list.pop())
#             if blocks_hit_list:
#                 # print(len(blocks_hit_list), len(block_list))
#                 vis.add(blocks_hit_list[0])
#                 block_picked = blocks_hit_list[0]
#                 flag = 1
#             if block_picked:
#                 corner = agent1.check_collision(block_picked.rect)

#                 block_picked.update(agent1.rect, corner)
#                 agent1.rotate_flag = True
#             # --- Go ahead and update the screen with what we've drawn.
#             # print(len(block_list))
#             if agent1.rect.y < 355:
#                 flag = 0
#                 block_picked = None
#                 # agent1.rotate_flag = False

#             blocks_transfer_list = pygame.sprite.spritecollide(agent2, vis, True)
#             if blocks_transfer_list:
#                 block_transfered = blocks_transfer_list[0]
#                 block_transfered.update(agent2.rect)
#                 vis2.add(block_transfered)
#                 agent2.change_command()
#                 block_picked = None
#                 flag = 0

#             if block_transfered:
#                 block_transfered.update(agent2.rect)
#             if agent2.rect.y < 105:
#                 block_transfered = None

#             block_list.draw(self.screen)
#             vis.draw(self.screen)
#             vis2.draw(self.screen)
#             pygame.display.flip()
#             clock.tick(10)

#         pygame.quit()

#     def create_targets(self):
#         block_list = pygame.sprite.Group()

#         # This is a list of every sprite.
#         # All blocks and the player block as well.
#         all_sprites_list = pygame.sprite.Group()
#         x = 20
#         for i in range(18):
#             # This represents a block
#             block = Block()
#             # Set a random location for the block
#             block.rect.x = x
#             x += 75
#             block.rect.y = 630
#             # Add the block to the list of objects
#             block_list.add(block)
#             all_sprites_list.add(block)

#         return block_list, all_sprites_list
#     def draw(self):
#         self.screen.blit(self.background, self.background_rect)
#         self.all_sprites.draw(self.screen)

#         for p in self.prospectors:
#             if p.body.nugget is not None:
#                 p.body.nugget.draw(self.screen)

#         for b in self.bankers:
#             if b.body.nugget is not None:
#                 b.body.nugget.draw(self.screen)

#     def close(self):
#         pg.event.pump()
#         pg.display.quit()
#         pg.quit()

# Except for the gold png images, all other sprite art was created by Yashas Lokesh
