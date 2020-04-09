import pygame as pg
import pygame.locals as locals
import pymunk as pm
from pymunk import Vec2d
from gym import spaces
import numpy as np

from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
import pettingzoo.gamma.prospector.constants as const
import pettingzoo.gamma.prospector.utils as utils

import math
import os
from enum import IntEnum, auto
import itertools as it
from random import randint


class CollisionTypes(IntEnum):
    PROSPECTOR = auto()
    BOUNDARY = auto()
    WATER = auto()
    CHEST = auto()
    GOLD = auto()
    BANKER = auto()


class Prospector(pg.sprite.Sprite):
    def __init__(self, pos, space, *sprite_groups):
        super().__init__(sprite_groups)
        # self.image = load_image(['prospec.png'])
        self.image = utils.load_image(["prospector-pickaxe-big.png"])
        self.image = pg.transform.scale(
            self.image, (int(const.AGENT_RADIUS * 2), int(const.AGENT_RADIUS * 2))
        )

        self.rect = self.image.get_rect()
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

    @property
    def center(self):
        return self.rect.x + const.AGENT_RADIUS, self.rect.y + const.AGENT_RADIUS

    def _update(self, action):
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

    def update(self, keys):
        x = y = 0
        if keys[locals.K_w]:
            y = 1
        if keys[locals.K_s]:
            y = -1
        if keys[locals.K_d]:
            x = 1
        if keys[locals.K_a]:
            x = -1
        if keys[locals.K_q]:
            self.body.angle += 0.1
            self.body.angular_velocity = 0
        if keys[locals.K_e]:
            self.body.angle -= 0.1
            self.body.angular_velocity = 0

        if x != 0 and y != 0:
            self.body.velocity = Vec2d(x, y).rotated(self.body.angle) * (
                const.PROSPECTOR_SPEED / math.sqrt(2)
            )
        else:
            self.body.velocity = (
                Vec2d(x, y).rotated(self.body.angle) * const.PROSPECTOR_SPEED
            )

        # Rotate the image of the sprite.
        self.rect.center = utils.flipy(self.body.position)
        self.image = pg.transform.rotozoom(
            self.orig_image, math.degrees(self.body.angle), 1
        )
        self.rect = self.image.get_rect(center=self.rect.center)

        curr_vel = self.body.velocity

        if self.body.nugget is not None:
            self.body.nugget.update(self.body.position, self.body.angle, False)

        self.body.velocity = curr_vel


class Banker(pg.sprite.Sprite):
    def __init__(self, pos, space, num, *sprite_groups):
        super().__init__(sprite_groups)
        self.image = utils.load_image(["bankers", "%s-big.png" % num])
        self.image = pg.transform.scale(
            self.image, (int(const.AGENT_RADIUS * 2), int(const.AGENT_RADIUS * 2))
        )

        self.rect = self.image.get_rect()
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

    def update(self, keys):
        move = 0
        if any(
            keys[key]
            for key in (locals.K_UP, locals.K_DOWN, locals.K_RIGHT, locals.K_LEFT,)
        ):
            move = 1

        if keys[locals.K_UP]:
            self.body.angle = 0
        elif keys[locals.K_DOWN]:
            self.body.angle = math.pi
        elif keys[locals.K_RIGHT]:
            self.body.angle = -math.pi / 2
        elif keys[locals.K_LEFT]:
            self.body.angle = math.pi / 2

        self.body.velocity = (
            Vec2d(0, move).rotated(self.body.angle) * const.BANKER_SPEED
        )

        # Rotate the image of the sprite.
        self.rect.center = utils.flipy(self.body.position)
        self.image = pg.transform.rotozoom(
            self.orig_image, math.degrees(self.body.angle), 1
        )

        self.rect = self.image.get_rect(center=self.rect.center)

        curr_vel = self.body.velocity

        if self.body.nugget is not None:
            corrected = utils.normalize_angle(self.body.angle + (math.pi / 2))
            self.body.nugget.update(self.body.position, corrected, True)

        self.body.velocity = curr_vel

    def _update(self, action):
        # left/right action
        x_vel = action[0] * const.PROSPECTOR_SPEED
        # up/down action
        y_vel = action[1] * const.PROSPECTOR_SPEED

        # Add math.pi / 2 because sprite is facing upwards at the start
        angle_radians = math.atan2(x_vel, y_vel) + (math.pi / 2)

        # Angle is determined only by current trajectory.
        self.body.angle = angle_radians
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


class Bank(pg.sprite.Sprite):
    def __init__(self, pos, verts, space, *sprite_groups):
        super().__init__(sprite_groups)

        self.image = utils.load_image(["bank-2.png"])
        self.image = pg.transform.scale(self.image, (184, 100))
        self.rect = self.image.get_rect(topleft=pos)

        self.body = pm.Body(body_type=pm.Body.STATIC)
        self.body.score = 0

        invert_verts = utils.invert_y(verts)
        self.shape = pm.Poly(self.body, invert_verts)
        self.shape.collision_type = CollisionTypes.CHEST

        self.body.position = utils.flipy(pos)
        self.space = space
        self.space.add(self.shape, self.body)

    def __str__(self):
        return str(self.body.score)


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

    def draw(self, surf):
        surf.blit(self.image, self.rect)


class Game:
    def __init__(self):
        self.done = False
        self.screen = pg.display.set_mode(const.SCREEN_SIZE)
        self.clock = pg.time.Clock()

        self.background = utils.load_image(["background-debris.png"])
        # self.background_rect = pg.Rect(0, 0, *const.SCREEN_SIZE)
        self.background_rect = self.background.get_rect(topleft=(0, 0))

        self.space = pm.Space()
        self.space.gravity = Vec2d(0.0, 0.0)
        # self.space.damping = 0.5
        self.space.damping = 0.0

        self.all_sprites = pg.sprite.Group()
        self.gold = []

        prospec_info = [utils.rand_pos("prospector") for _ in range(3)]
        self.prospectors = []
        for pos in prospec_info:
            self.prospectors.append(Prospector(pos, self.space, self.all_sprites))

        banker_info = (
            (1, utils.rand_pos("banker")),
            (2, utils.rand_pos("banker")),
            (3, utils.rand_pos("banker")),
        )
        self.bankers = []
        for num, pos in banker_info:
            self.bankers.append(Banker(pos, self.space, num, self.all_sprites))

        chest_verts = (
            (0, 0),
            (184, 0),
            (184, 100),
            (0, 100),
        )

        chest_info = [
            ([184 * 1, 50], chest_verts),
            ([184 * 3, 50], chest_verts),
            ([184 * 5, 50], chest_verts),
        ]

        self.chests = []
        for pos, verts in chest_info:
            self.chests.append(Bank(pos, verts, self.space, self.all_sprites))

        for w_type, s_pos, b_pos, verts in const.FENCE_INFO:
            Fence(w_type, s_pos, b_pos, verts, self.space, self.all_sprites)

        water_info = {
            "pos": (0, const.SCREEN_HEIGHT - const.WATER_HEIGHT),
            "verts": (
                (0, 0),
                (const.SCREEN_WIDTH, 0),
                (const.SCREEN_WIDTH, const.WATER_HEIGHT),
                (0, const.WATER_HEIGHT),
            ),
        }

        Water(water_info["pos"], water_info["verts"], self.space, self.all_sprites)

        def add_gold(arbiter, space, data):
            prospec = arbiter.shapes[0]
            prospec_body = prospec.body

            position = arbiter.contact_point_set.points[0].point_a
            normal = arbiter.contact_point_set.normal

            prospec_body.position = position - (24 * normal)
            prospec_body.velocity = (0, 0)

            if prospec_body.nugget is None:

                position = arbiter.contact_point_set.points[0].point_a

                gold = Gold(position, prospec_body, self.space)
                self.gold.append(gold)

                prospec_body.nugget = gold

            return True

        gold_dispenser = self.space.add_collision_handler(
            CollisionTypes.PROSPECTOR, CollisionTypes.WATER
        )

        gold_dispenser.begin = add_gold

        def handoff_gold_handler(arbiter, space, data):
            banker, gold = arbiter.shapes[0], arbiter.shapes[1]

            gold_class = None
            for g in self.gold:
                if g.id == gold.id:
                    gold_class = g

            if gold_class.parent_body.sprite_type == "prospector":

                banker_body = banker.body

                normal = arbiter.contact_point_set.normal

                corrected = utils.normalize_angle(banker_body.angle + (math.pi / 2))

                if (
                    corrected - const.BANKER_HANDOFF_TOLERANCE
                    <= normal.angle
                    <= corrected + const.BANKER_HANDOFF_TOLERANCE
                ):

                    gold_class.parent_body.nugget = None

                    gold_class.parent_body = banker_body
                    banker_body.nugget = gold_class
                    banker_body.nugget_offset = normal.angle

            return True

        handoff_gold = self.space.add_collision_handler(
            CollisionTypes.BANKER, CollisionTypes.GOLD
        )

        handoff_gold.begin = handoff_gold_handler

        def gold_score_handler(arbiter, space, data):
            gold, chest = arbiter.shapes[0], arbiter.shapes[1]

            gold_class = None
            for g in self.gold:
                if g.id == gold.id:
                    gold_class = g

            if gold_class.parent_body.sprite_type == "banker":

                chest.body.score += 1

                self.space.remove(gold, gold.body)

                gold_class.parent_body.nugget = None

                # total_score = ", ".join(
                #     [
                #         "Chest %d: %d" % (i, c.body.score)
                #         for i, c in enumerate(self.chests)
                #     ]
                # )

                # print(total_score)

                self.gold.remove(gold_class)
                self.all_sprites.remove(gold_class)

            return False

        gold_score = self.space.add_collision_handler(
            CollisionTypes.GOLD, CollisionTypes.CHEST
        )

        gold_score.begin = gold_score_handler

    def run(self):
        while not self.done:
            for event in pg.event.get():
                if event.type == locals.QUIT or (
                    event.type == locals.KEYDOWN and event.key in [locals.K_ESCAPE]
                ):
                    self.done = True

            self.dt = self.clock.tick(15)

            self.space.step(1 / 15)
            self.all_sprites.update(pg.key.get_pressed())

            self.draw()

    def draw(self):
        # self.screen.fill(BACKGROUND_COLOR)
        # self.background.blit(self.screen)
        self.screen.blit(self.background, self.background_rect)
        self.all_sprites.draw(self.screen)

        for p in self.prospectors:
            if p.body.nugget is not None:
                p.body.nugget.draw(self.screen)

        for b in self.bankers:
            if b.body.nugget is not None:
                b.body.nugget.draw(self.screen)

        pg.display.flip()


class env(AECEnv):
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
    ):
        if ind_reward + group_reward + other_group_reward != 1.0:
            raise ValueError(
                "Individual reward, group reward, and other group reward should "
                "add up to 1.0"
            )

        self.num_agents = 7
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

        # TODO: Setup game data here
        pg.init()
        self.clock = pg.time.Clock()
        self.done = False

        self.background = utils.load_image(["test.png"])
        self.background_rect = pg.Rect(0, 0, *const.SCREEN_SIZE)

        self.space = pm.Space()
        self.space.gravity = Vec2d(0.0, 0.0)
        self.space.damping = 0.0

        self.all_sprites = pg.sprite.Group()
        self.gold = []

        # Generate random positions for each prospector agent
        prospector_info = [utils.rand_pos("prospector") for _ in range(4)]
        self.prospectors = []
        for pos in prospector_info:
            prospector = Prospector(pos, self.space, self.all_sprites)
            self.prospectors.append(prospector)
            self.agents.append(prospector)

        banker_info = [(i + 1, utils.rand_pos("banker")) for i in range(3)]
        self.bankers = []
        for num, pos in banker_info:
            banker = Banker(pos, self.space, num, self.all_sprites)
            self.bankers.append(banker)
            self.agents.append(banker)

        # Create these dictionaries after self.agents is populated
        self.rewards = dict(zip(self.agents, [0 for _ in self.agents]))
        self.dones = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [[] for _ in self.agents]))
        self.metadata = {"render.modes": ["human"]}

        # TODO: Setup action spaces
        self.action_spaces = {}
        for a in self.agents:
            num_actions = 0
            if type(a) is Prospector:
                num_actions = 6
            else:
                num_actions = 4
            self.action_spaces[a] = spaces.Discrete(num_actions + 1)

        # TODO: Setup observation spaces
        self.observation_spaces = {}
        self.last_observation = {}
        for a in self.agents:
            self.last_observation[a] = None
            # low, high for RGB values
            self.observation_spaces[a] = spaces.Box(
                low=0, high=255, shape=const.OBSERVATION_SHAPE
            )

        """ Finish setting up environment agents """
        self.agent_order = self.agents[:]
        self._agent_selector = agent_selector(self.agent_order)
        self.agent_selection = self._agent_selector.next()

        self.banks = []
        for pos, verts in const.BANK_INFO:
            self.banks.append(Bank(pos, verts, self.space, self.all_sprites))

        for w_type, pos, verts in const.BOUNDARY_INFO:
            Fence(w_type, pos, verts, self.space, self.all_sprites)

        Water(const.WATER_INFO[0], const.WATER_INFO[1], self.space, self.all_sprites)

        # Collision Handler Functions --------------------------------------------
        # Water to Prospector
        def add_gold(arbiter, space, data):
            prospec_shape = arbiter.shapes[0]
            prospec_body = prospec_shape.body

            position = arbiter.contact_point_set.points[0].point_a
            normal = arbiter.contact_point_set.normal

            prospec_body.position = position - (24 * normal)
            prospec_body.velocity = (0, 0)

            prospec_sprite = None
            for p in self.prospectors:
                if p.body is prospec_body:
                    prospec_sprite = p
            self.rewards[prospec_sprite] += ind_reward * prospec_find_gold_reward

            for a in self.agents:
                if isinstance(a, Prospector) and a is not prospec_sprite:
                    self.rewards[a] += group_reward * prospec_find_gold_reward
                elif isinstance(a, Banker):
                    self.rewards[a] += other_group_reward * prospec_find_gold_reward

            if prospec_body.nugget is None:
                position = arbiter.contact_point_set.points[0].point_a

                gold = Gold(position, prospec_body, self.space)
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

            if gold_sprite.parent_body.sprite_type == "prospector":
                banker_body = banker_shape.body
                prospec_body = gold_sprite.parent_body

                prospec_sprite = None
                for p in self.prospectors:
                    if p.body is prospec_body:
                        prospec_sprite = p
                self.rewards[prospec_sprite] += prospec_handoff_gold_reward

                for a in self.agents:
                    if isinstance(a, Prospector) and a is not prospec_sprite:
                        self.rewards[a] += group_reward * prospec_handoff_gold_reward
                    elif isinstance(a, Banker):
                        self.rewards[a] += (
                            other_group_reward * prospec_handoff_gold_reward
                        )

                banker_sprite = None
                for b in self.bankers:
                    if b.shape is banker_shape:
                        banker_sprite = b
                self.rewards[banker_sprite] += banker_receive_gold_reward

                for a in self.agents:
                    if isinstance(a, Prospector):
                        self.rewards[a] += (
                            other_group_reward * banker_receive_gold_reward
                        )
                    elif isinstance(a, Banker) and a is not banker_sprite:
                        self.rewards[a] += group_reward * banker_receive_gold_reward

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

        # Banker to chest
        def gold_score_handler(arbiter, space, data):
            gold_shape, chest = arbiter.shapes[0], arbiter.shapes[1]

            gold_class = None
            for g in self.gold:
                if g.id == gold_shape.id:
                    gold_class = g

            if gold_class.parent_body.sprite_type == "banker":
                chest.body.score += 1
                self.space.remove(gold_shape, gold_shape.body)
                gold_class.parent_body.nugget = None
                banker_body = gold_class.parent_body

                banker_sprite = None
                for b in self.bankers:
                    if b.body is banker_body:
                        banker_sprite = b
                self.rewards[banker_sprite] += banker_deposit_gold_reward

                for a in self.agents:
                    if isinstance(a, Prospector):
                        self.rewards[a] += (
                            other_group_reward * banker_deposit_gold_reward
                        )
                    elif isinstance(a, Banker) and a is not banker_sprite:
                        self.rewards[a] += group_reward * banker_deposit_gold_reward

                # total_score = ", ".join(
                #     [
                #         "Chest %d: %d" % (i, c.body.score)
                #         for i, c in enumerate(self.chests)
                #     ]
                # )

                # print(total_score)
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
            CollisionTypes.GOLD, CollisionTypes.CHEST
        )

        gold_score.begin = gold_score_handler

    def observe(self, agent):
        capture = pg.surfarray.array3d(self.screen)
        a = self.agents[agent]

        delta = const.OBSERVATION_SIDE_LENGTH // 2
        center = a.center  # Calculated property added to prospector and banker classes
        x, y = center
        sub_screen = capture[x - delta: x + delta, y - delta: y + delta, :]

        return sub_screen

    def step(self, action, observe=True):
        agent = self.agent_selection
        # TODO: Figure out rewards
        if action is None:
            print("Error: NoneType received as action")
        else:
            agent.update(action)

        all_agents_updated = self._agent_selector.is_last()
        # Only take next step in game if all agents have received an action
        if all_agents_updated:
            self.frame += 1
            # If we reached max frames, we're done
            if self.frame == self.max_frames:
                self.dones = dict(zip(self.agents, [True for _ in self.agents]))

            if self.rendering:
                self.clock.tick(const.FPS)
            else:
                self.clock.tick()
            self.space.step(1 / 15)

        self.agent_selection = self._agent_selector.next()
        observation = self.observe(self.agent_selection)

        pg.event.pump()
        if observe:
            return observation

    def reward(self):
        return self.rewards

    def reset(self, observe=True):
        self.done = False
        self.agents = []

        # Re-create all agents and Pymunk space
        self.space = pm.Space()
        self.space.gravity = Vec2d(0.0, 0.0)
        self.space.damping = 0.0

        self.all_sprites = pg.sprite.Group()
        self.gold = []

        prospector_info = [utils.rand_pos("prospector") for _ in range(4)]
        self.prospectors = []
        for pos in prospector_info:
            prospector = Prospector(pos, self.space, self.all_sprites)
            self.prospectors.append(prospector)
            self.agents.append(prospector)

        banker_info = [(i + 1, utils.rand_pos("banker")) for i in range(3)]
        self.bankers = []
        for num, pos in banker_info:
            banker = Banker(pos, self.space, num, self.all_sprites)
            self.bankers.append(banker)
            self.agents.append(banker)

        self.banks = []
        for pos, verts in const.BANK_INFO:
            self.banks.append(Bank(pos, verts, self.space, self.all_sprites))

        for w_type, pos, verts in const.BOUNDARY_INFO:
            Fence(w_type, pos, verts, self.space, self.all_sprites)

        Water(const.WATER_INFO[0], const.WATER_INFO[1], self.space, self.all_sprites)

        self.rewards = dict(zip(self.agents, [0 for _ in self.agents]))
        self.dones = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [[] for _ in self.agents]))
        self.metadata = {"render.modes": ["human"]}

        self.rendering = False
        self.frame = 0
        self._agent_selector.reinit(self.agent_order)
        self.agent_selection = self._agent_selector.next()

        if observe:
            return self.observe(self.agent_selection)

    def render(self, mode="human"):
        if not self.rendering:
            pg.display.init()
            self.screen = pg.display.set_mode(const.SCREEN_SIZE)
            self.rendering = True
        self.draw()
        pg.display.flip()

    def draw(self):
        self.screen.blit(self.background, self.background_rect)
        self.all_sprites.draw(self.screen)

        for p in self.prospectors:
            if p.body.nugget is not None:
                p.body.nugget.draw(self.screen)

        for b in self.bankers:
            if b.body.nugget is not None:
                b.body.nugget.draw(self.screen)

    def close(self):
        pg.event.pump()
        pg.display.quit()
        pg.quit()


if __name__ == "__main__":
    pg.init()
    game = Game()
    game.run()
