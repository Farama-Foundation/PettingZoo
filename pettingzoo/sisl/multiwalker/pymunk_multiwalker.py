"""Experimental Pymunk physics core for Multiwalker.

This module is intentionally not wired into ``multiwalker_v9``.  It is a
prototype for reviewing the Box2D-to-Pymunk mapping before a versioned public
environment is introduced.  The reward and observation skeleton mirrors the
current environment, while rendering, hardcore terrain, fallen-agent removal,
and physics parity calibration remain follow-up work.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pymunk
from gymnasium.utils import seeding

FPS = 50
SCALE = 30.0

MOTORS_TORQUE = 80
SPEED_HIP = 4
SPEED_KNEE = 6
LIDAR_RANGE = 160 / SCALE
INITIAL_RANDOM = 5

HULL_POLY = [(-30, +9), (+6, +9), (+34, +1), (+34, -8), (-30, -8)]
LEG_DOWN = -8 / SCALE
LEG_W, LEG_H = 8 / SCALE, 34 / SCALE
PACKAGE_POLY = [(-120, 5), (120, 5), (120, -5), (-120, -5)]
PACKAGE_LENGTH = 240

VIEWPORT_W = 600
VIEWPORT_H = 400
TERRAIN_STEP = 14 / SCALE
TERRAIN_LENGTH = 200
TERRAIN_HEIGHT = VIEWPORT_H / SCALE / 4
TERRAIN_GRASS = 10
TERRAIN_STARTPAD = 20
FRICTION = 2.5
WALKER_SEPARATION = 10

TERRAIN_CATEGORY = 0b0001
WALKER_CATEGORY = 0b0010
PACKAGE_CATEGORY = 0b0100


def _scaled_vertices(vertices, *, x_scale=1.0):
    return [(x * x_scale / SCALE, y / SCALE) for x, y in vertices]


def _body_with_poly(space, vertices, density, position, *, friction, shape_filter):
    body = pymunk.Body()
    body.position = position
    shape = pymunk.Poly(body, vertices)
    shape.density = density
    shape.friction = friction
    shape.elasticity = 0.0
    shape.filter = shape_filter
    space.add(body, shape)
    return body, shape


def _body_with_box(space, size, density, position, angle, *, shape_filter):
    body = pymunk.Body()
    body.position = position
    body.angle = angle
    shape = pymunk.Poly.create_box(body, size)
    shape.density = density
    shape.friction = 0.0
    shape.elasticity = 0.0
    shape.filter = shape_filter
    space.add(body, shape)
    return body, shape


@dataclass
class _Joint:
    motor: pymunk.SimpleMotor
    limit: pymunk.RotaryLimitJoint

    @property
    def angle(self):
        return self.limit.b.angle - self.limit.a.angle

    @property
    def speed(self):
        return self.limit.b.angular_velocity - self.limit.a.angular_velocity


class PymunkWalker:
    """One articulated walker in the experimental Pymunk world."""

    def __init__(self, space, init_x, init_y, walker_id, seed=None):
        self.space = space
        self.init_x = init_x
        self.init_y = init_y
        self.walker_id = walker_id
        self.np_random, _ = seeding.np_random(seed)
        self.hull = None
        self.hull_shape = None
        self.legs = []
        self.leg_shapes = []
        self.joints = []
        self.ground_contacts = [False, False]
        self.lidar = np.ones(10, dtype=np.float64)
        self._create()

    def _create(self):
        walker_filter = pymunk.ShapeFilter(
            group=self.walker_id, categories=WALKER_CATEGORY
        )
        self.hull, self.hull_shape = _body_with_poly(
            self.space,
            _scaled_vertices(HULL_POLY),
            5.0,
            (self.init_x, self.init_y),
            friction=0.1,
            shape_filter=walker_filter,
        )
        self.hull.apply_force_at_world_point(
            (self.np_random.uniform(-INITIAL_RANDOM, INITIAL_RANDOM), 0),
            self.hull.position,
        )

        for side in (-1, +1):
            upper, upper_shape = _body_with_box(
                self.space,
                (LEG_W, LEG_H),
                1.0,
                (self.init_x, self.init_y - LEG_H / 2 - LEG_DOWN),
                side * 0.05,
                shape_filter=walker_filter,
            )
            hip = self._add_joint(
                self.hull,
                upper,
                (self.init_x, self.init_y + LEG_DOWN),
                lower=-0.8,
                upper=1.1,
                rate=side,
            )

            lower_leg, lower_shape = _body_with_box(
                self.space,
                (0.8 * LEG_W, LEG_H),
                1.0,
                (self.init_x, self.init_y - LEG_H * 3 / 2 - LEG_DOWN),
                side * 0.05,
                shape_filter=walker_filter,
            )
            knee = self._add_joint(
                upper,
                lower_leg,
                (self.init_x, self.init_y - LEG_H - LEG_DOWN),
                lower=-1.6,
                upper=-0.1,
                rate=1,
            )
            self.legs.extend((upper, lower_leg))
            self.leg_shapes.extend((upper_shape, lower_shape))
            self.joints.extend((hip, knee))

    def _add_joint(self, body_a, body_b, pivot, *, lower, upper, rate):
        pivot_joint = pymunk.PivotJoint(body_a, body_b, pivot)
        limit = pymunk.RotaryLimitJoint(body_a, body_b, lower, upper)
        motor = pymunk.SimpleMotor(body_a, body_b, rate)
        motor.max_force = MOTORS_TORQUE
        self.space.add(pivot_joint, limit, motor)
        return _Joint(motor=motor, limit=limit)

    def apply_action(self, action):
        action = np.asarray(action, dtype=np.float64).reshape(4)
        speeds = (SPEED_HIP, SPEED_KNEE, SPEED_HIP, SPEED_KNEE)
        for command, speed, joint in zip(action, speeds, self.joints):
            joint.motor.rate = float(speed * np.sign(command))
            joint.motor.max_force = float(
                MOTORS_TORQUE * np.clip(abs(command), 0.0, 1.0)
            )

    def update_contacts(self, terrain_shapes):
        terrain_shapes = set(terrain_shapes)
        for foot_index, leg_index in enumerate((1, 3)):
            contacts = self.space.shape_query(self.leg_shapes[leg_index])
            self.ground_contacts[foot_index] = any(
                result.shape in terrain_shapes for result in contacts
            )

    def touches_non_package_shape(self, package_shape):
        return any(
            result.shape is not package_shape
            for result in self.space.shape_query(self.hull_shape)
        )

    def get_observation(self):
        terrain_filter = pymunk.ShapeFilter(mask=TERRAIN_CATEGORY)
        for index in range(10):
            start = self.hull.position
            end = start + (
                np.sin(1.5 * index / 10.0) * LIDAR_RANGE,
                -np.cos(1.5 * index / 10.0) * LIDAR_RANGE,
            )
            hit = self.space.segment_query_first(start, end, 0.0, terrain_filter)
            self.lidar[index] = 1.0 if hit is None else hit.alpha

        velocity = self.hull.velocity
        state = [
            self.hull.angle,
            2.0 * self.hull.angular_velocity / FPS,
            0.3 * velocity.x * (VIEWPORT_W / SCALE) / FPS,
            0.3 * velocity.y * (VIEWPORT_H / SCALE) / FPS,
            self.joints[0].angle,
            self.joints[0].speed / SPEED_HIP,
            self.joints[1].angle + 1.0,
            self.joints[1].speed / SPEED_KNEE,
            float(self.ground_contacts[0]),
            self.joints[2].angle,
            self.joints[2].speed / SPEED_HIP,
            self.joints[3].angle + 1.0,
            self.joints[3].speed / SPEED_KNEE,
            float(self.ground_contacts[1]),
            *self.lidar,
        ]
        return np.asarray(state, dtype=np.float32)


class PymunkMultiWalkerPrototype:
    """Standalone physics prototype preserving Multiwalker's state skeleton."""

    def __init__(
        self,
        n_walkers=3,
        position_noise=1e-3,
        angle_noise=1e-3,
        forward_reward=1.0,
        terminate_reward=-100.0,
        fall_reward=-10.0,
        shared_reward=True,
        terminate_on_fall=True,
        terrain_length=TERRAIN_LENGTH,
        seed=None,
    ):
        self.n_walkers = n_walkers
        self.position_noise = position_noise
        self.angle_noise = angle_noise
        self.forward_reward = forward_reward
        self.terminate_reward = terminate_reward
        self.fall_reward = fall_reward
        self.local_ratio = 1.0 - shared_reward
        self.terminate_on_fall = terminate_on_fall
        self.terrain_length = terrain_length
        self.seed(seed)
        self.reset()

    def seed(self, seed=None):
        self.np_random, self.seed_value = seeding.np_random(seed)
        return [self.seed_value]

    def reset(self):
        self.space = pymunk.Space(threaded=False)
        self.space.gravity = (0.0, -10.0)
        self.space.iterations = 180
        self.terrain_shapes = self._create_flat_terrain()

        initial_x = TERRAIN_STEP * TERRAIN_STARTPAD / 2
        initial_y = TERRAIN_HEIGHT + 2 * LEG_H
        self.start_x = [
            initial_x + WALKER_SEPARATION * index * TERRAIN_STEP
            for index in range(self.n_walkers)
        ]
        self.walkers = [
            PymunkWalker(
                self.space,
                init_x,
                initial_y,
                walker_id=index + 1,
                seed=self.seed_value,
            )
            for index, init_x in enumerate(self.start_x)
        ]
        self.package_scale = self.n_walkers / 1.75
        self.package_length = PACKAGE_LENGTH / SCALE * self.package_scale
        self.package, self.package_shape = _body_with_poly(
            self.space,
            _scaled_vertices(PACKAGE_POLY, x_scale=self.package_scale),
            1.0,
            (np.mean(self.start_x), TERRAIN_HEIGHT + 3 * LEG_H),
            friction=0.5,
            shape_filter=pymunk.ShapeFilter(categories=PACKAGE_CATEGORY),
        )
        self.previous_shaping = np.zeros(self.n_walkers, dtype=np.float64)
        self.previous_package_shaping = 0.0
        self.fallen_walkers = np.zeros(self.n_walkers, dtype=bool)
        self.game_over = False
        self.frames = 0
        self._update_contacts()
        self.previous_shaping = np.asarray(
            [-5.0 * abs(walker.hull.angle) for walker in self.walkers],
            dtype=np.float64,
        )
        self.previous_package_shaping = (
            self.forward_reward * 130 * self.package.position.x / SCALE
        )
        return self.observations()

    def _create_flat_terrain(self):
        shapes = []
        terrain_filter = pymunk.ShapeFilter(categories=TERRAIN_CATEGORY)
        for index in range(self.terrain_length - 1):
            start = (index * TERRAIN_STEP, TERRAIN_HEIGHT)
            end = ((index + 1) * TERRAIN_STEP, TERRAIN_HEIGHT)
            segment = pymunk.Segment(self.space.static_body, start, end, 0.0)
            segment.friction = FRICTION
            segment.elasticity = 0.0
            segment.filter = terrain_filter
            shapes.append(segment)
        self.space.add(*shapes)
        return shapes

    def _update_contacts(self):
        for index, walker in enumerate(self.walkers):
            walker.update_contacts(self.terrain_shapes)
            self.fallen_walkers[index] |= walker.touches_non_package_shape(
                self.package_shape
            )
        package_contacts = self.space.shape_query(self.package_shape)
        allowed_shapes = {walker.hull_shape for walker in self.walkers}
        self.game_over = any(
            result.shape not in allowed_shapes for result in package_contacts
        )

    def observations(self):
        observations = []
        for index, walker in enumerate(self.walkers):
            base = walker.get_observation().tolist()
            relative = []
            for neighbor_index in (index - 1, index + 1):
                if neighbor_index < 0 or neighbor_index >= self.n_walkers:
                    relative.extend((0.0, 0.0))
                else:
                    neighbor = self.walkers[neighbor_index]
                    dx = (neighbor.hull.position.x - walker.hull.position.x) / (
                        self.package_length
                    )
                    dy = (neighbor.hull.position.y - walker.hull.position.y) / (
                        self.package_length
                    )
                    relative.extend(
                        (
                            self.np_random.normal(dx, self.position_noise),
                            self.np_random.normal(dy, self.position_noise),
                        )
                    )
            package_dx = (
                self.package.position.x - walker.hull.position.x
            ) / self.package_length
            package_dy = (
                self.package.position.y - walker.hull.position.y
            ) / self.package_length
            relative.extend(
                (
                    self.np_random.normal(package_dx, self.position_noise),
                    self.np_random.normal(package_dy, self.position_noise),
                    self.np_random.normal(self.package.angle, self.angle_noise),
                )
            )
            observations.append(np.asarray(base + relative, dtype=np.float32))
        return np.asarray(observations, dtype=np.float32)

    def step(self, actions):
        actions = np.asarray(actions, dtype=np.float64)
        if actions.shape != (self.n_walkers, 4):
            raise ValueError(
                f"expected actions with shape {(self.n_walkers, 4)}, "
                f"got {actions.shape}"
            )
        for walker, action in zip(self.walkers, actions):
            walker.apply_action(action)
        self.space.step(1.0 / FPS)
        self.frames += 1
        self._update_contacts()

        rewards = np.zeros(self.n_walkers, dtype=np.float64)
        for index, walker in enumerate(self.walkers):
            shaping = -5.0 * abs(walker.hull.angle)
            rewards[index] = shaping - self.previous_shaping[index]
            self.previous_shaping[index] = shaping

        package_shaping = self.forward_reward * 130 * self.package.position.x / SCALE
        rewards += package_shaping - self.previous_package_shaping
        self.previous_package_shaping = package_shaping
        rewards[self.fallen_walkers] += self.fall_reward

        failed = bool(
            (self.terminate_on_fall and self.fallen_walkers.any())
            or self.game_over
            or self.package.position.x < 0
        )
        dones = np.full(self.n_walkers, failed, dtype=bool)
        if failed:
            rewards += self.terminate_reward
        elif (
            self.package.position.x
            > (self.terrain_length - TERRAIN_GRASS) * TERRAIN_STEP
        ):
            dones[:] = True

        global_reward = rewards.mean()
        local_reward = rewards * self.local_ratio
        rewards = (
            global_reward * (1.0 - self.local_ratio) + local_reward * self.local_ratio
        )
        return self.observations(), rewards, dones

    def state(self):
        walker_state = np.concatenate(
            [walker.get_observation() for walker in self.walkers]
        )
        package_state = np.asarray(
            (self.package.position.x, self.package.position.y, self.package.angle),
            dtype=np.float32,
        )
        return np.concatenate((walker_state, package_state)).astype(np.float32)
