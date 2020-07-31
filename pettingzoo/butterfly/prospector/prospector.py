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
from gym.utils import EzPickle


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
        self.image = utils.load_image(["prospector.png"])
        self.id = num

        self.rect = self.image.get_rect(topleft=pos)
        self.orig_image = self.image

        # Create the physics body and shape of this object.
        moment = pm.moment_for_circle(1, 0, self.rect.width / 2)

        self.body = pm.Body(1, moment)
        self.body.nugget = None
        self.body.sprite_type = "prospector"

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
        self.image = pg.transform.rotate(self.orig_image, math.degrees(self.body.angle))

        self.rect = self.image.get_rect(center=self.rect.center)

        curr_vel = self.body.velocity

        if self.body.nugget is not None:
            self.body.nugget.update(self.body.position, self.body.angle, False)

        self.body.velocity = curr_vel

    def convert_img(self):
        self.image = self.image.convert_alpha()

    def __str__(self):
        return f"prospector_{self.id}"

    def __repr__(self):
        return self.__str__()


class Banker(pg.sprite.Sprite):
    def __init__(self, pos, space, num, *sprite_groups):
        super().__init__(sprite_groups)
        self.image = utils.load_image(["bankers", f"{num}.png"])

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
        if not all(a == 0 for a in action):
            self.body.angle = angle_radians
        self.body.angular_velocity = 0

        self.body.velocity = Vec2d(x_vel, y_vel)

        self.rect.center = utils.flipy(self.body.position)
        self.image = pg.transform.rotate(self.orig_image, math.degrees(self.body.angle))

        self.rect = self.image.get_rect(center=self.rect.center)

        curr_vel = self.body.velocity

        if self.body.nugget is not None:
            self.body.nugget.update(
                self.body.position, self.body.angle + (math.pi / 2), True
            )

        self.body.velocity = curr_vel

    def convert_img(self):
        self.image = self.image.convert_alpha()

    def __str__(self):
        return f"banker_{self.id}"

    def __repr__(self):
        return self.__str__()


class Fence(pg.sprite.Sprite):
    def __init__(self, w_type, sprite_pos, body_pos, verts, space, *sprite_groups):
        super().__init__(sprite_groups)

        self.rects = []
        if w_type == "top":
            self.tile = utils.load_image(["fence_horiz_tile.png"])
            size = self.tile.get_rect().size

            x = 15
            y = 0
            while x <= 1230:
                rect = pg.Rect(x, y, *size)
                self.rects.append(rect)
                x += 50

        elif w_type in ["right", "left"]:
            self.tile = utils.load_image(["fence_vert_tile.png"])
            size = self.tile.get_rect().size

            x = 6 if w_type == "left" else 1265
            y = 0
            while y <= const.VERT_FENCE_HEIGHT:
                rect = pg.Rect(x, y, *size)
                self.rects.append(rect)
                y += 33
        else:
            raise ValueError("Fence image not found! Check the spelling")

        self.body = pm.Body(body_type=pm.Body.STATIC)

        # Transform pygame vertices to fit Pymunk body
        invert_verts = utils.invert_y(verts)
        self.shape = pm.Poly(self.body, invert_verts)
        self.shape.elasticity = 0.0
        self.shape.collision_type = CollisionTypes.BOUNDARY

        self.body.position = utils.flipy(body_pos)
        space.add(self.shape)

    def full_draw(self, screen):
        for rect in self.rects:
            screen.blit(self.tile, rect)

    def convert_img(self):
        self.tile = self.tile.convert_alpha()


class Bank(pg.sprite.Sprite):
    def __init__(self, pos, verts, space, *sprite_groups):
        super().__init__(sprite_groups)

        self.image = utils.load_image(["bank.png"])
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

        self.image = utils.load_image(["gold.png"])
        self.orig_image = self.image

        self.rect = self.image.get_rect()

        self.moment = pm.moment_for_circle(1, 0, 6)
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


class Water(object):
    def __init__(self, pos, verts, space, rng):
        self.num_cols = math.ceil(const.SCREEN_WIDTH / const.TILE_SIZE)
        self.num_rows = math.ceil(const.WATER_HEIGHT / const.TILE_SIZE)

        self.top_tile = utils.load_image(["river_to_sand_tile.png"])
        self.tile = utils.load_image(["river_tile.png"])

        self.debris_tile = utils.load_image(["debris", "seaweed_water.png"])
        tile_size = self.tile.get_size()

        self.rects = []
        for row in range(self.num_rows):
            new_row = []
            for col in range(self.num_cols):
                rect = pg.Rect(
                    col * const.TILE_SIZE, pos[1] + (row * const.TILE_SIZE), *tile_size
                )
                new_row.append(rect)
            self.rects.append(new_row)

        self.body = pm.Body(body_type=pm.Body.STATIC)

        # Transform pygame vertices to fit Pymunk body
        invert_verts = utils.invert_y(verts)
        self.shape = pm.Poly(self.body, invert_verts)
        self.shape.collision_type = CollisionTypes.WATER

        self.body.position = utils.flipy(pos)
        self.space = space
        self.space.add(self.shape)

    def generate_debris(self, rng):
        self.debris = []
        for col in range(1, self.num_cols - 1, 3):
            if rng.random_sample() >= 0.5:
                y = rng.randint(0, 2)
                x = col + rng.randint(0, 3)
                rect = self.rects[y][x].copy()
                rect.x += 3
                rect.y += 9
                self.debris.append([self.debris_tile, rect])

    def full_draw(self, screen):
        for rect in self.rects[0]:
            screen.blit(self.top_tile, rect)

        for rect in self.rects[1]:
            screen.blit(self.tile, rect)

        for pair in self.debris:
            screen.blit(pair[0], pair[1])

    def draw(self, screen):
        self.full_draw()

    def convert_img(self):
        self.top_tile = self.top_tile.convert_alpha()
        self.tile = self.tile.convert_alpha()
        self.debris_tile = self.debris_tile.convert_alpha()


class Background(object):
    def __init__(self, rng):
        self.num_cols = math.ceil(const.SCREEN_WIDTH / const.TILE_SIZE)
        self.num_rows = math.ceil(
            (const.SCREEN_HEIGHT - const.WATER_HEIGHT) / const.TILE_SIZE
        ) + 1

        self.tile = utils.load_image(["sand_tile.png"])

        self.debris_tiles = {
            0: utils.load_image(["debris", "0.png"]),
            1: utils.load_image(["debris", "1.png"]),
            2: utils.load_image(["debris", "2.png"]),
            3: utils.load_image(["debris", "3.png"]),
        }

        tile_size = self.tile.get_size()

        # Used when updating environment and drawing
        self.dirty_rects = []
        self.rects = []
        for row in range(self.num_rows):
            new_row = []
            for col in range(self.num_cols):
                rect = pg.Rect(col * const.TILE_SIZE, row * const.TILE_SIZE, *tile_size)
                new_row.append(rect)
            self.rects.append(new_row)

    def generate_debris(self, rng):
        self.debris = []
        for row in range(1, self.num_rows - 1, 3):
            for col in range(1, self.num_cols - 1, 3):
                y = row + rng.randint(0, 3)
                if y == self.num_rows - 2:
                    y += -1
                x = col + rng.randint(0, 3)
                choice = rng.randint(0, 4)
                self.debris.append([self.debris_tiles[choice], self.rects[y][x]])

    def full_draw(self, screen):
        for row in self.rects:
            for rect in row:
                screen.blit(self.tile, rect)

        for pair in self.debris:
            screen.blit(pair[0], pair[1])

    def draw(self, screen):
        for rect in self.dirty_rects:
            screen.blit(self.tile, rect)

        for pair in self.debris:
            screen.blit(pair[0], pair[1])

        self.dirty_rects.clear()

    def update(self, sprite_rect: pg.Rect, dirty_fences):
        top_y = int(sprite_rect.top // 50)
        bottom_y = int(sprite_rect.bottom // 50)
        left_x = int(sprite_rect.left // 50)
        right_x = int(sprite_rect.right // 50)

        for pair in self.debris:
            self.dirty_rects.append(pair[1])

        self.dirty_rects.append(self.rects[top_y][left_x])
        self.dirty_rects.append(self.rects[top_y][right_x])
        self.dirty_rects.append(self.rects[bottom_y][left_x])
        self.dirty_rects.append(self.rects[bottom_y][right_x])

        if left_x == 1:
            dirty_fences[0] = True
        if top_y == 0:
            dirty_fences[1] = True
        if right_x == self.num_cols - 1:
            dirty_fences[2] = True

        return self.dirty_rects

    def convert_img(self):
        self.tile = self.tile.convert_alpha()
        for pair in self.debris:
            pair[0] = pair[0].convert_alpha()


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.ClipOutOfBoundsWrapper(env)
    env = wrappers.NanZerosWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(AECEnv, EzPickle):
    def __init__(
        self,
        seed=None,
        ind_reward=0.8,
        group_reward=0.1,
        other_group_reward=0.1,
        prospec_find_gold_reward=1,
        prospec_handoff_gold_reward=1,
        banker_receive_gold_reward=1,
        banker_deposit_gold_reward=1,
        max_frames=900,
    ):
        EzPickle.__init__(
            self,
            seed,
            ind_reward,
            group_reward,
            other_group_reward,
            prospec_find_gold_reward,
            prospec_handoff_gold_reward,
            banker_receive_gold_reward,
            banker_deposit_gold_reward,
            max_frames)
        if ind_reward + group_reward + other_group_reward != 1.0:
            raise ValueError(
                "Individual reward, group reward, and other group reward should "
                "add up to 1.0"
            )

        self.num_agents = const.NUM_AGENTS
        self.agents = []

        self.sprite_list = [
            "bankers/0.png",
            "bankers/1.png",
            "bankers/2.png",
            "prospector.png",
        ]
        self.max_frames = max_frames

        pg.init()
        self.rng, seed = seeding.np_random(seed)
        self.clock = pg.time.Clock()
        self.closed = False

        self.background = Background(self.rng)

        self.space = pm.Space()
        self.space.gravity = Vec2d(0.0, 0.0)
        self.space.damping = 0.0

        self.all_sprites = pg.sprite.RenderUpdates()
        self.gold = []

        self.water = Water(
            const.WATER_INFO[0], const.WATER_INFO[1], self.space, self.rng
        )

        # Generate random positions for each prospector agent
        prospector_info = [
            (i, utils.rand_pos("prospector", self.rng))
            for i in range(const.NUM_PROSPECTORS)
        ]
        self.prospectors = {}
        for num, pos in prospector_info:
            prospector = Prospector(pos, self.space, num, self.all_sprites)
            identifier = f"prospector_{num}"
            self.prospectors[identifier] = prospector
            self.agents.append(identifier)

        banker_info = [
            (i, utils.rand_pos("banker", self.rng)) for i in range(const.NUM_BANKERS)
        ]
        self.bankers = {}
        for num, pos in banker_info:
            banker = Banker(pos, self.space, num, self.all_sprites)
            identifier = f"banker_{num}"
            self.bankers[identifier] = banker
            self.agents.append(identifier)

        self.banks = []
        for pos, verts in const.BANK_INFO:
            self.banks.append(Bank(pos, verts, self.space, self.all_sprites))

        self.fences = []
        for w_type, s_pos, b_pos, verts in const.FENCE_INFO:
            f = Fence(w_type, s_pos, b_pos, verts, self.space)
            self.fences.append(f)

        self.metadata = {"render.modes": ["human"]}

        self.action_spaces = {}
        for p in self.prospectors:
            self.action_spaces[p] = spaces.Box(
                low=np.float32(-1.0), high=np.float32(1.0), shape=(3,)
            )

        for b in self.bankers:
            self.action_spaces[b] = spaces.Box(
                low=np.float32(-1.0), high=np.float32(1.0), shape=(2,)
            )

        self.observation_spaces = {}
        self.last_observation = {}

        for p in self.prospectors:
            self.last_observation[p] = None
            self.observation_spaces[p] = spaces.Box(
                low=0, high=255, shape=const.PROSPEC_OBSERV_SHAPE, dtype=np.uint8
            )

        for b in self.bankers:
            self.last_observation[b] = None
            self.observation_spaces[b] = spaces.Box(
                low=0, high=255, shape=const.BANKER_OBSERV_SHAPE, dtype=np.uint8
            )

        self._agent_selector = agent_selector(self.agents)
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

            # gold_sprite is None if gold was handed off to the bank right before
            # calling this collision handler
            # This collision handler is only for prospector -> banker gold handoffs
            if (
                gold_sprite is None
                or gold_sprite.parent_body.sprite_type != "prospector"
            ):
                return False

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
            normalized_normal = utils.normalize_angle(normal.angle)
            if (
                corrected - const.BANKER_HANDOFF_TOLERANCE
                <= normalized_normal
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
                    else:
                        self.rewards[k] += group_reward * banker_deposit_gold_reward

                for k in self.prospectors:
                    self.rewards[k] += other_group_reward * banker_deposit_gold_reward

                self.gold.remove(gold_class)
                self.all_sprites.remove(gold_class)

            return False

        # Prevent prospector motion lag from colliding with gold nugget
        def prospec_gold_handler(arbiter, space, data):
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

        prospec_gold_collision = self.space.add_collision_handler(
            CollisionTypes.PROSPECTOR, CollisionTypes.GOLD
        )

        prospec_gold_collision.begin = prospec_gold_handler

    def observe(self, agent):
        capture = pg.surfarray.pixels3d(self.screen)
        if agent in self.prospectors:
            ag = self.prospectors[agent]
            side_len = const.PROSPEC_OBSERV_SIDE_LEN
        else:
            ag = self.bankers[agent]
            side_len = const.BANKER_OBSERV_SIDE_LEN

        delta = side_len // 2
        x, y = ag.center  # Calculated property added to prospector and banker classes
        sub_screen = np.array(
            capture[
                max(0, x - delta): min(const.SCREEN_WIDTH, x + delta),
                max(0, y - delta): min(const.SCREEN_HEIGHT, y + delta), :,
            ],
            dtype=np.uint8,
        )

        s_x, s_y, _ = sub_screen.shape
        pad_x = side_len - s_x
        if x > const.SCREEN_WIDTH - delta:  # Right side of the screen
            sub_screen = np.pad(
                sub_screen, pad_width=((0, pad_x), (0, 0), (0, 0)), mode="constant"
            )
        elif x < 0 + delta:
            sub_screen = np.pad(
                sub_screen, pad_width=((pad_x, 0), (0, 0), (0, 0)), mode="constant"
            )

        pad_y = side_len - s_y
        if y > const.SCREEN_HEIGHT - delta:  # Bottom of the screen
            sub_screen = np.pad(
                sub_screen, pad_width=((0, 0), (0, pad_y), (0, 0)), mode="constant"
            )
        elif y < 0 + delta:
            sub_screen = np.pad(
                sub_screen, pad_width=((0, 0), (pad_y, 0), (0, 0)), mode="constant"
            )

        sub_screen = np.rot90(sub_screen, k=3)
        sub_screen = np.fliplr(sub_screen).astype(np.uint8)
        self.last_observation[agent] = sub_screen

        return sub_screen

    def step(self, action, observe=True):
        agent_id = self.agent_selection

        if agent_id in self.prospectors:
            agent = self.prospectors[agent_id]
        else:
            agent = self.bankers[agent_id]

        agent_pos = agent.rect.topleft
        agent_angle = agent.body.angle
        agent_bg_rects = self.background.update(agent.rect, self.dirty_fences)

        gold_bg_rects = []
        if agent.body.nugget is not None:
            gold_bg_rects = self.background.update(
                agent.body.nugget.rect, self.dirty_fences
            )
        agent.update(action)

        if agent_pos != agent.rect.topleft or agent_angle != agent.body.angle:
            self.dirty_rects.extend(agent_bg_rects)
            self.dirty_rects.extend(gold_bg_rects)
            self.dirty_rects.append(agent.rect)

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
        self.done = False

        self.background.generate_debris(self.rng)
        self.water.generate_debris(self.rng)

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
        self.dirty_rects = []
        self.dirty_fences = [False, False, False]

        self._agent_selector.reinit(self.agents)
        self.agent_selection = self._agent_selector.next()
        self.full_draw()
        if observe:
            return self.observe(self.agent_selection)

    def render(self, mode="human"):
        if not self.rendering:
            pg.display.init()
            self.screen = pg.display.set_mode(const.SCREEN_SIZE)
            self.background.convert_img()
            self.water.convert_img()
            for f in self.fences:
                f.convert_img()
            for s in self.all_sprites.sprites():
                s.convert_img()
            self.rendering = True
            self.full_draw()
            pg.display.flip()
        else:
            self.draw()
            pg.display.update(self.dirty_rects)
            self.dirty_fences = [False, False, False]
            self.dirty_rects.clear()

    def full_draw(self):
        """ Called to draw everything when first rendering """
        self.background.full_draw(self.screen)
        for f in self.fences:
            f.full_draw(self.screen)
        self.water.full_draw(self.screen)
        self.all_sprites.draw(self.screen)

    def draw(self):
        """ Called after each frame, all agents updated """
        self.background.draw(self.screen)
        for idx, dirty in enumerate(self.dirty_fences):
            if dirty:
                self.fences[idx].full_draw(self.screen)
        self.water.full_draw(self.screen)
        self.all_sprites.draw(self.screen)

    def close(self):
        if not self.closed:
            self.closed = True
            if self.rendering:
                pg.event.pump()
                pg.display.quit()
            pg.quit()


# Art by Keira Wentworth
