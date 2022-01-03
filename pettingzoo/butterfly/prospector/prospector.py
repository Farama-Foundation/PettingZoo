import itertools as it
import math
import os
from enum import IntEnum, auto

import numpy as np
import pygame as pg
import pymunk as pm
from gym import spaces
from gym.utils import EzPickle, seeding
from pymunk import Vec2d

from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector, wrappers
from pettingzoo.utils.conversions import parallel_wrapper_fn

from . import constants as const
from . import utils
from .manual_control import manual_control


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

        self.rect = self.image.get_rect(center=pos)
        self.orig_image = self.image.copy()

        # Create the physics body and shape of this object.
        moment = pm.moment_for_circle(1, 0, const.AGENT_RADIUS)

        self.body = pm.Body(1, moment, body_type=pm.Body.DYNAMIC)
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
        self.body.angular_velocity = 0
        self.image = pg.transform.rotozoom(self.orig_image, 0, 1)
        self.rect = self.image.get_rect(center=pos)
        self.body.position = utils.flipy(pos)
        self.body.velocity = Vec2d(0.0, 0.0)
        self.body.force = Vec2d(0.0, 0.0)
        self.body.nugget = None

    @property
    def center(self):
        return self.rect.center

    def update(self, action):
        # These actions are performed with the agent's angle in mind
        # forward/backward action
        y_vel = action[0] * const.PROSPECTOR_SPEED
        # left/right action
        x_vel = action[1] * const.PROSPECTOR_SPEED

        delta_angle = action[2] * const.MAX_SPRITE_ROTATION

        self.body.angle += delta_angle
        self.body.angular_velocity = 0

        move = pm.Vec2d(x_vel, y_vel)
        self.body.apply_force_at_local_point(move, point=(0, 0))

    def synchronize_center(self):
        self.rect.center = utils.flipy(self.body.position)
        self.image = pg.transform.rotate(self.orig_image, math.degrees(self.body.angle))
        self.rect = self.image.get_rect(center=self.rect.center)

    def update_gold(self):
        if self.body.nugget is not None:
            self.body.nugget.update(self.body.position, self.body.angle, False)

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

        self.rect = self.image.get_rect(center=pos)
        self.orig_image = self.image.copy()

        moment = pm.moment_for_circle(1, 0, const.AGENT_RADIUS)

        self.body = pm.Body(1, moment, body_type=pm.Body.DYNAMIC)
        self.body.nugget = None
        self.body.sprite_type = "banker"

        self.shape = pm.Circle(self.body, const.AGENT_RADIUS)
        self.shape.collision_type = CollisionTypes.BANKER

        self.body.position = utils.flipy(pos)
        # Add them to the Pymunk space.
        self.space = space
        self.space.add(self.body, self.shape)

    def reset(self, pos):
        self.body.angle = 0
        self.image = pg.transform.rotozoom(self.orig_image, 0, 1)
        self.rect = self.image.get_rect(center=pos)
        self.body.position = utils.flipy(pos)
        self.body.velocity = Vec2d(0.0, 0.0)
        self.body.nugget = None

    @property
    def center(self):
        return self.rect.center

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

        # rotate movement backwards with a magnitude of self.body.angle
        #     so that sprite moves forward in chosen direction
        move = pm.Vec2d(x_vel, y_vel).rotated(-self.body.angle)
        self.body.apply_force_at_local_point(move, point=(0, 0))

    def synchronize_center(self):
        self.rect.center = utils.flipy(self.body.position)
        self.image = pg.transform.rotate(self.orig_image, math.degrees(self.body.angle))
        self.rect = self.image.get_rect(center=self.rect.center)

    def update_gold(self):
        if self.body.nugget is not None:
            self.body.nugget.update(
                self.body.position, self.body.angle + (math.pi / 2), True
            )

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
        space.add(self.body, self.shape)

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
        self.space.add(self.body, self.shape)

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

        self.moment = pm.moment_for_circle(1, 0, const.GOLD_RADIUS)
        self.body = pm.Body(1, self.moment, body_type=pm.Body.KINEMATIC)
        self.body.position = body.position

        self.shape = pm.Circle(self.body, const.GOLD_RADIUS)
        self.shape.collision_type = CollisionTypes.GOLD
        # only triggers collision callbacks, doesn't create real collisions
        self.shape.sensor = True
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


class Water:
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
        self.space.add(self.body, self.shape)

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


class Background:
    def __init__(self, rng):
        self.num_cols = math.ceil(const.SCREEN_WIDTH / const.TILE_SIZE)
        self.num_rows = (
            math.ceil((const.SCREEN_HEIGHT - const.WATER_HEIGHT) / const.TILE_SIZE) + 1
        )

        self.tile = utils.load_image(["sand_tile.png"])

        self.debris_tiles = {
            0: utils.load_image(["debris", "0.png"]),
            1: utils.load_image(["debris", "1.png"]),
            2: utils.load_image(["debris", "2.png"]),
            3: utils.load_image(["debris", "3.png"]),
        }

        # Used when updating environment and drawing
        self.dirty_rects = []

        self.rects = []
        # same as (const.TILE_SIZE, const.TILE_SIZE)
        tile_size = self.tile.get_size()
        for row in range(self.num_rows):
            new_row = []
            for col in range(self.num_cols):
                rect = pg.Rect(col * const.TILE_SIZE, row * const.TILE_SIZE, *tile_size)
                new_row.append(rect)
            self.rects.append(new_row)

    def generate_debris(self, rng):
        self.debris = {}
        for row in range(1, self.num_rows - 1, 3):
            for col in range(1, self.num_cols - 1, 3):
                y = row + rng.randint(0, 3)
                if y == self.num_rows - 2:
                    y += -1
                x = col + rng.randint(0, 3)
                choice = rng.randint(0, 4)
                self.debris[self.rects[y][x].topleft] = self.debris_tiles[choice]

    def full_draw(self, screen):
        for row in self.rects:
            for rect in row:
                screen.blit(self.tile, rect)
                debris = self.debris.get(rect.topleft, None)
                if debris is not None:
                    screen.blit(debris, rect)

    def draw(self, screen):
        # self.full_draw(screen)
        for rect in self.dirty_rects:
            screen.blit(self.tile, rect)
            debris = self.debris.get(rect.topleft, None)
            if debris is not None:
                screen.blit(debris, rect)

        self.dirty_rects.clear()

    def update(self, sprite_rect: pg.Rect):
        top_y = int(sprite_rect.top // const.TILE_SIZE)
        bottom_y = int(sprite_rect.bottom // const.TILE_SIZE)
        left_x = int(sprite_rect.left // const.TILE_SIZE)
        right_x = int(sprite_rect.right // const.TILE_SIZE)

        self.dirty_rects.append(self.rects[top_y][left_x])
        self.dirty_rects.append(self.rects[top_y][right_x])
        self.dirty_rects.append(self.rects[bottom_y][left_x])
        self.dirty_rects.append(self.rects[bottom_y][right_x])

    def convert_img(self):
        self.tile = self.tile.convert_alpha()

        for i in self.debris_tiles:
            self.debris_tiles[i].convert_alpha()


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.ClipOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


parallel_env = parallel_wrapper_fn(env)


class raw_env(AECEnv, EzPickle):
    def __init__(
        self,
        ind_reward=0.8,
        group_reward=0.1,
        other_group_reward=0.1,
        prospec_find_gold_reward=1,
        prospec_handoff_gold_reward=1,
        banker_receive_gold_reward=1,
        banker_deposit_gold_reward=1,
        max_cycles=450,
    ):
        EzPickle.__init__(
            self,
            ind_reward,
            group_reward,
            other_group_reward,
            prospec_find_gold_reward,
            prospec_handoff_gold_reward,
            banker_receive_gold_reward,
            banker_deposit_gold_reward,
            max_cycles,
        )

        total_reward_factor = ind_reward + group_reward + other_group_reward
        if not math.isclose(total_reward_factor, 1.0, rel_tol=1e-09):
            raise ValueError(
                "The sum of the individual reward, group reward, and other "
                "group reward should add up to approximately 1.0"
            )

        self.agents = []

        self.sprite_list = [
            "bankers/0.png",
            "bankers/1.png",
            "bankers/2.png",
            "prospector.png",
        ]
        self.max_cycles = max_cycles

        pg.init()
        self.seed()
        self.closed = False

        self.background = Background(self.rng)

        self.space = pm.Space()
        self.space.gravity = Vec2d(0.0, 0.0)
        self.space.iterations = 20  # for decreasing bounciness
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

        self.metadata = {
            "render.modes": ["human", "rgb_array"],
            'name': "prospector_v4",
            'is_parallelizable': True,
            'video.frames_per_second': const.FPS,
        }

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

        self.state_space = spaces.Box(low=0, high=255, shape=((const.SCREEN_HEIGHT, const.SCREEN_WIDTH, 3)), dtype=np.uint8)

        self.possible_agents = self.agents[:]
        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.next()
        self.reset()

        # Collision Handler Functions --------------------------------------------
        # Water to Prospector
        def add_gold(arbiter, space, data):
            prospec_shape = arbiter.shapes[0]
            prospec_body = prospec_shape.body

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
            banker_shape, gold_shape = arbiter.shapes

            gold_sprite = None
            for g in self.gold:
                if g.id == gold_shape.id:
                    gold_sprite = g

            # gold_sprite is None if gold was handed off to the bank right before
            #   calling this collision handler
            # This collision handler is only for prospector -> banker gold handoffs
            if (
                gold_sprite is None
                or gold_sprite.parent_body.sprite_type != "prospector"
            ):
                return True

            banker_body = banker_shape.body
            prospec_body = gold_sprite.parent_body

            normal = arbiter.contact_point_set.normal
            # Correct the angle because banker's head is rotated pi/2
            corrected = utils.normalize_angle(banker_body.angle + (math.pi / 2))
            normalized_normal = utils.normalize_angle(normal.angle)
            if (
                corrected - const.BANKER_HANDOFF_TOLERANCE
                <= normalized_normal
                <= corrected + const.BANKER_HANDOFF_TOLERANCE
            ):

                # transfer gold
                gold_sprite.parent_body.nugget = None
                gold_sprite.parent_body = banker_body
                banker_body.nugget = gold_sprite

                for k, v in self.prospectors.items():
                    self.rewards[k] += other_group_reward * banker_receive_gold_reward
                    if v.body is prospec_body:
                        self.rewards[k] += ind_reward * prospec_handoff_gold_reward
                    else:
                        self.rewards[k] += group_reward * prospec_handoff_gold_reward

                for k, v in self.bankers.items():
                    self.rewards[k] += other_group_reward * prospec_handoff_gold_reward
                    if v.body is banker_body:
                        self.rewards[k] += ind_reward * banker_receive_gold_reward
                    else:
                        self.rewards[k] += group_reward * banker_receive_gold_reward

            return True

        # Banker to bank
        def gold_score_handler(arbiter, space, data):
            gold_shape, _ = arbiter.shapes

            for g in self.gold:
                if g.id == gold_shape.id:
                    gold_class = g

            if gold_class.parent_body.sprite_type == "banker":
                self.space.remove(gold_shape, gold_shape.body)
                gold_class.parent_body.nugget = None
                banker_body = gold_class.parent_body

                for k, v in self.bankers.items():
                    if v.body is banker_body:
                        self.rewards[k] += ind_reward * banker_deposit_gold_reward
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

    def seed(self, seed=None):
        self.rng, seed = seeding.np_random(seed)

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

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    def state(self):
        '''
        Returns an observation of the global environment
        '''
        state = pg.surfarray.pixels3d(self.screen).copy()
        state = np.rot90(state, k=3)
        state = np.fliplr(state)
        return state

    def step(self, action):
        if self.dones[self.agent_selection]:
            return self._was_done_step(action)
        agent_id = self.agent_selection
        all_agents_updated = self._agent_selector.is_last()
        self.rewards = {agent: 0 for agent in self.agents}

        if agent_id in self.prospectors:
            agent = self.prospectors[agent_id]
        else:
            agent = self.bankers[agent_id]

        self.background.update(agent.rect)

        nugget = agent.body.nugget
        if nugget is not None:
            self.background.update(nugget.rect)

        agent.update(action)

        # Only take next step in game if all agents have received an action
        if all_agents_updated:
            for _ in range(const.STEPS_PER_FRAME):
                self.space.step(const.SPACE_STEP_DELTA)

            for pr in self.prospectors.values():
                pr.synchronize_center()
                pr.update_gold()
                self.background.update(pr.rect)

                nugget = pr.body.nugget
                if nugget is not None:
                    self.background.update(nugget.rect)

            for b in self.bankers.values():
                b.synchronize_center()
                b.update_gold()
                self.background.update(b.rect)

                nugget = b.body.nugget
                if nugget is not None:
                    self.background.update(nugget.rect)

            self.draw()

            self.frame += 1
            # If we reached max frames, we're done
            if self.frame == self.max_cycles:
                self.dones = dict(zip(self.agents, [True for _ in self.agents]))

        if self.rendering:
            pg.event.pump()

        self.agent_selection = self._agent_selector.next()
        self._cumulative_rewards[agent_id] = 0
        self._accumulate_rewards()

    def reset(self):
        self.screen = pg.Surface(const.SCREEN_SIZE)
        self.done = False

        self.background.generate_debris(self.rng)
        self.water.generate_debris(self.rng)

        for p in self.prospectors.values():
            p.reset(utils.rand_pos("prospector", self.rng))

        for b in self.bankers.values():
            b.reset(utils.rand_pos("banker", self.rng))

        for g in self.gold:
            self.space.remove(g.shape, g.body)
            self.all_sprites.remove(g)

        self.gold = []

        self.agents = self.possible_agents[:]
        self.rewards = dict(zip(self.agents, [0 for _ in self.agents]))
        self._cumulative_rewards = dict(zip(self.agents, [0 for _ in self.agents]))
        self.dones = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [{} for _ in self.agents]))
        self.rendering = False
        self.frame = 0
        self.background.dirty_rects.clear()

        self._agent_selector.reinit(self.agents)
        self.agent_selection = self._agent_selector.next()
        self.full_draw()

    def render(self, mode="human"):
        if mode == "human":
            if not self.rendering:
                self.rendering = True
                pg.display.init()
                self.screen = pg.display.set_mode(const.SCREEN_SIZE)
                self.background.convert_img()
                self.water.convert_img()
                for f in self.fences:
                    f.convert_img()
                for s in self.all_sprites.sprites():
                    s.convert_img()
                self.full_draw()

            pg.display.flip()

        elif mode == "rgb_array":  # no display, return whole screen as array
            observation = np.array(pg.surfarray.pixels3d(self.screen))
            transposed = np.transpose(observation, axes=(1, 0, 2))
            return transposed

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
        for f in self.fences:
            f.full_draw(self.screen)
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
