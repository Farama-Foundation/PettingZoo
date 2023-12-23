import copy
import math

import Box2D
import numpy as np
import pygame
from Box2D.b2 import (
    circleShape,
    contactListener,
    edgeShape,
    fixtureDef,
    polygonShape,
    revoluteJointDef,
)
from gymnasium import spaces
from gymnasium.utils import seeding
from pygame import gfxdraw

from pettingzoo.sisl._utils import Agent

MAX_AGENTS = 40

FPS = 50
SCALE = 30.0  # affects how fast-paced the game is, forces should be adjusted as well

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
TERRAIN_LENGTH = 200  # in steps
TERRAIN_HEIGHT = VIEWPORT_H / SCALE / 4
TERRAIN_GRASS = 10  # low long are grass spots, in steps
TERRAIN_STARTPAD = 20  # in steps
FRICTION = 2.5

WALKER_SEPERATION = 10  # in steps


class ContactDetector(contactListener):
    def __init__(self, env):
        contactListener.__init__(self)
        self.env = env

    def BeginContact(self, contact):
        # if walkers fall on ground
        for i, walker in enumerate(self.env.walkers):
            if walker.hull is not None:
                if walker.hull == contact.fixtureA.body:
                    if self.env.package != contact.fixtureB.body:
                        self.env.fallen_walkers[i] = True
                if walker.hull == contact.fixtureB.body:
                    if self.env.package != contact.fixtureA.body:
                        self.env.fallen_walkers[i] = True

        # if package is on the ground
        if self.env.package == contact.fixtureA.body:
            if contact.fixtureB.body not in [w.hull for w in self.env.walkers]:
                self.env.game_over = True
        if self.env.package == contact.fixtureB.body:
            if contact.fixtureA.body not in [w.hull for w in self.env.walkers]:
                self.env.game_over = True

        # self.env.game_over = True
        for walker in self.env.walkers:
            if walker.hull is not None:
                for leg in [walker.legs[1], walker.legs[3]]:
                    if leg in [contact.fixtureA.body, contact.fixtureB.body]:
                        leg.ground_contact = True

    def EndContact(self, contact):
        for walker in self.env.walkers:
            if walker.hull is not None:
                for leg in [walker.legs[1], walker.legs[3]]:
                    if leg in [contact.fixtureA.body, contact.fixtureB.body]:
                        leg.ground_contact = False


class BipedalWalker(Agent):
    def __init__(
        self,
        world,
        init_x=TERRAIN_STEP * TERRAIN_STARTPAD / 2,
        init_y=TERRAIN_HEIGHT + 2 * LEG_H,
        n_walkers=2,
        seed=None,
    ):
        self.world = world
        self._n_walkers = n_walkers
        self.hull = None
        self.init_x = init_x
        self.init_y = init_y
        self.walker_id = -int(self.init_x)
        self._seed(seed)

    def _destroy(self):
        if not self.hull:
            return
        self.world.DestroyBody(self.hull)
        self.hull = None
        for leg in self.legs:
            self.world.DestroyBody(leg)
        self.legs = []
        self.joints = []

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def _reset(self):
        self._destroy()
        init_x = self.init_x
        init_y = self.init_y
        self.hull = self.world.CreateDynamicBody(
            position=(init_x, init_y),
            fixtures=fixtureDef(
                shape=polygonShape(
                    vertices=[(x / SCALE, y / SCALE) for x, y in HULL_POLY]
                ),
                density=5.0,
                friction=0.1,
                groupIndex=self.walker_id,
                restitution=0.0,
            ),  # 0.99 bouncy
        )
        self.hull.color1 = (127, 51, 229)
        self.hull.color2 = (76, 76, 127)
        self.hull.ApplyForceToCenter(
            (self.np_random.uniform(-INITIAL_RANDOM, INITIAL_RANDOM), 0), True
        )

        self.legs = []
        self.joints = []
        for i in [-1, +1]:
            leg = self.world.CreateDynamicBody(
                position=(init_x, init_y - LEG_H / 2 - LEG_DOWN),
                angle=(i * 0.05),
                fixtures=fixtureDef(
                    shape=polygonShape(box=(LEG_W / 2, LEG_H / 2)),
                    density=1.0,
                    restitution=0.0,
                    groupIndex=self.walker_id,
                ),  # collide with ground only
            )
            leg.color1 = (153 - i * 25, 76 - i * 25, 127 - i * 25)
            leg.color2 = (102 - i * 25, 51 - i * 25, 76 - i * 25)
            rjd = revoluteJointDef(
                bodyA=self.hull,
                bodyB=leg,
                localAnchorA=(0, LEG_DOWN),
                localAnchorB=(0, LEG_H / 2),
                enableMotor=True,
                enableLimit=True,
                maxMotorTorque=MOTORS_TORQUE,
                motorSpeed=i,
                lowerAngle=-0.8,
                upperAngle=1.1,
            )
            self.legs.append(leg)
            self.joints.append(self.world.CreateJoint(rjd))

            lower = self.world.CreateDynamicBody(
                position=(init_x, init_y - LEG_H * 3 / 2 - LEG_DOWN),
                angle=(i * 0.05),
                fixtures=fixtureDef(
                    shape=polygonShape(box=(0.8 * LEG_W / 2, LEG_H / 2)),
                    density=1.0,
                    restitution=0.0,
                    groupIndex=self.walker_id,
                ),
            )
            lower.color1 = (153 - i * 25, 76 - i * 25, 127 - i * 25)
            lower.color2 = (102 - i * 25, 51 - i * 25, 76 - i * 25)
            rjd = revoluteJointDef(
                bodyA=leg,
                bodyB=lower,
                localAnchorA=(0, -LEG_H / 2),
                localAnchorB=(0, LEG_H / 2),
                enableMotor=True,
                enableLimit=True,
                maxMotorTorque=MOTORS_TORQUE,
                motorSpeed=1,
                lowerAngle=-1.6,
                upperAngle=-0.1,
            )
            lower.ground_contact = False
            self.legs.append(lower)
            self.joints.append(self.world.CreateJoint(rjd))

        self.drawlist = self.legs + [self.hull]

        class LidarCallback(Box2D.b2.rayCastCallback):
            def ReportFixture(self, fixture, point, normal, fraction):
                if (fixture.filterData.categoryBits & 1) == 0:
                    return -1
                self.p2 = point
                self.fraction = fraction
                return fraction

        self.lidar = [LidarCallback() for _ in range(10)]

    def apply_action(self, action):
        self.joints[0].motorSpeed = float(SPEED_HIP * np.sign(action[0]))
        self.joints[0].maxMotorTorque = float(
            MOTORS_TORQUE * np.clip(np.abs(action[0]), 0, 1)
        )
        self.joints[1].motorSpeed = float(SPEED_KNEE * np.sign(action[1]))
        self.joints[1].maxMotorTorque = float(
            MOTORS_TORQUE * np.clip(np.abs(action[1]), 0, 1)
        )
        self.joints[2].motorSpeed = float(SPEED_HIP * np.sign(action[2]))
        self.joints[2].maxMotorTorque = float(
            MOTORS_TORQUE * np.clip(np.abs(action[2]), 0, 1)
        )
        self.joints[3].motorSpeed = float(SPEED_KNEE * np.sign(action[3]))
        self.joints[3].maxMotorTorque = float(
            MOTORS_TORQUE * np.clip(np.abs(action[3]), 0, 1)
        )

    def get_observation(self):
        pos = self.hull.position
        vel = self.hull.linearVelocity

        for i in range(10):
            self.lidar[i].fraction = 1.0
            self.lidar[i].p1 = pos
            self.lidar[i].p2 = (
                pos[0] + math.sin(1.5 * i / 10.0) * LIDAR_RANGE,
                pos[1] - math.cos(1.5 * i / 10.0) * LIDAR_RANGE,
            )
            self.world.RayCast(self.lidar[i], self.lidar[i].p1, self.lidar[i].p2)

        state = [
            # Normal angles up to 0.5 here, but sure more is possible.
            self.hull.angle,
            2.0 * self.hull.angularVelocity / FPS,
            # Normalized to get -1..1 range
            0.3 * vel.x * (VIEWPORT_W / SCALE) / FPS,
            0.3 * vel.y * (VIEWPORT_H / SCALE) / FPS,
            # This will give 1.1 on high up, but it's still OK (and there should be spikes on hiting the ground, that's normal too)
            self.joints[0].angle,
            self.joints[0].speed / SPEED_HIP,
            self.joints[1].angle + 1.0,
            self.joints[1].speed / SPEED_KNEE,
            1.0 if self.legs[1].ground_contact else 0.0,
            self.joints[2].angle,
            self.joints[2].speed / SPEED_HIP,
            self.joints[3].angle + 1.0,
            self.joints[3].speed / SPEED_KNEE,
            1.0 if self.legs[3].ground_contact else 0.0,
        ]

        state += [l_dis.fraction for l_dis in self.lidar]
        assert len(state) == 24

        return state

    @property
    def observation_space(self):
        # 24 original obs (joints, etc), 2 displacement obs for each neighboring walker, 3 for package
        return spaces.Box(
            low=np.float32(-np.inf),
            high=np.float32(np.inf),
            shape=(24 + 4 + 3,),
            dtype=np.float32,
        )

    @property
    def action_space(self):
        return spaces.Box(
            low=np.float32(-1), high=np.float32(1), shape=(4,), dtype=np.float32
        )


class MultiWalkerEnv:
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": FPS}

    hardcore = False

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
        remove_on_fall=True,
        terrain_length=TERRAIN_LENGTH,
        max_cycles=500,
        render_mode=None,
    ):
        """Initializes the `MultiWalkerEnv` class.

        n_walkers: number of bipedal walkers in environment
        position_noise: noise applied to agent positional sensor observations
        angle_noise: noise applied to agent rotational sensor observations
        forward_reward: reward applied for an agent standing, scaled by agent's x coordinate
        fall_reward: reward applied when an agent falls down
        shared_reward: whether reward is distributed among all agents or allocated locally
        terminate_reward: reward applied for each fallen walker in environment
        terminate_on_fall: toggles whether agent is done if it falls down
        terrain_length: length of terrain in number of steps
        max_cycles: after max_cycles steps all agents will return done
        """
        self.n_walkers = n_walkers
        self.position_noise = position_noise
        self.angle_noise = angle_noise
        self.forward_reward = forward_reward
        self.fall_reward = fall_reward
        self.terminate_reward = terminate_reward
        self.terminate_on_fall = terminate_on_fall
        self.local_ratio = 1 - shared_reward
        self.remove_on_fall = remove_on_fall
        self.terrain_length = terrain_length
        self.seed_val = None
        self._seed()
        self.setup()
        self.screen = None
        self.last_rewards = [0 for _ in range(self.n_walkers)]
        self.last_dones = [False for _ in range(self.n_walkers)]
        self.last_obs = [None for _ in range(self.n_walkers)]
        self.max_cycles = max_cycles
        self.render_mode = render_mode
        self.frames = 0

    def get_param_values(self):
        return self.__dict__

    def setup(self):
        self.viewer = None

        self.world = Box2D.b2World()
        self.terrain = None

        init_x = TERRAIN_STEP * TERRAIN_STARTPAD / 2
        init_y = TERRAIN_HEIGHT + 2 * LEG_H
        self.start_x = [
            init_x + WALKER_SEPERATION * i * TERRAIN_STEP for i in range(self.n_walkers)
        ]
        self.walkers = [
            BipedalWalker(self.world, init_x=sx, init_y=init_y, seed=self.seed_val)
            for sx in self.start_x
        ]
        self.observation_space = [agent.observation_space for agent in self.walkers]
        self.action_space = [agent.action_space for agent in self.walkers]
        self.state_space = spaces.Box(
            low=-np.float32(np.inf),
            high=+np.float32(np.inf),
            shape=(
                self.n_walkers * 24 + 3,
            ),  # 24 is the observation space of each walker, 3 is the package observation space
            dtype=np.float32,
        )

        self.package_scale = self.n_walkers / 1.75
        self.package_length = PACKAGE_LENGTH / SCALE * self.package_scale

        self.prev_shaping = np.zeros(self.n_walkers)
        self.prev_package_shaping = 0.0

    @property
    def agents(self):
        return self.walkers

    def _seed(self, seed=None):
        self.np_random, seed_ = seeding.np_random(seed)
        self.seed_val = seed_
        for walker in getattr(self, "walkers", []):
            walker._seed(seed_)
        return [seed_]

    def _destroy(self):
        if not self.terrain:
            return
        self.world.contactListener = None
        for t in self.terrain:
            self.world.DestroyBody(t)
        self.terrain = []
        self.world.DestroyBody(self.package)
        self.package = None

        for walker in self.walkers:
            walker._destroy()

    def close(self):
        if self.screen is not None:
            pygame.quit()
            self.screen = None

    def reset(self):
        self.setup()
        self.world.contactListener_bug_workaround = ContactDetector(self)
        self.world.contactListener = self.world.contactListener_bug_workaround
        self.game_over = False
        self.fallen_walkers = np.zeros(self.n_walkers, dtype=bool)
        self.prev_shaping = np.zeros(self.n_walkers)
        self.prev_package_shaping = 0.0
        self.scroll = 0.0
        self.lidar_render = 0

        self._generate_package()
        self._generate_terrain(self.hardcore)
        self._generate_clouds()

        self.drawlist = copy.copy(self.terrain)

        self.drawlist += [self.package]

        for walker in self.walkers:
            walker._reset()
            self.drawlist += walker.legs
            self.drawlist += [walker.hull]
        r, d, o = self.scroll_subroutine()
        self.last_rewards = [0 for _ in range(self.n_walkers)]
        self.last_dones = [False for _ in range(self.n_walkers)]
        self.last_obs = o
        self.frames = 0

        return self.observe(0)

    def scroll_subroutine(self):
        xpos = np.zeros(self.n_walkers)
        obs = []
        done = False
        rewards = np.zeros(self.n_walkers)

        for i in range(self.n_walkers):
            if self.walkers[i].hull is None:
                obs.append(np.zeros_like(self.observation_space[i].low))
                continue
            pos = self.walkers[i].hull.position
            x, y = pos.x, pos.y
            xpos[i] = x

            walker_obs = self.walkers[i].get_observation()
            neighbor_obs = []
            for j in [i - 1, i + 1]:
                # if no neighbor (for edge walkers)
                if j < 0 or j == self.n_walkers or self.walkers[j].hull is None:
                    neighbor_obs.append(0.0)
                    neighbor_obs.append(0.0)
                else:
                    xm = (self.walkers[j].hull.position.x - x) / self.package_length
                    ym = (self.walkers[j].hull.position.y - y) / self.package_length
                    neighbor_obs.append(self.np_random.normal(xm, self.position_noise))
                    neighbor_obs.append(self.np_random.normal(ym, self.position_noise))
            xd = (self.package.position.x - x) / self.package_length
            yd = (self.package.position.y - y) / self.package_length
            neighbor_obs.append(self.np_random.normal(xd, self.position_noise))
            neighbor_obs.append(self.np_random.normal(yd, self.position_noise))
            neighbor_obs.append(
                self.np_random.normal(self.package.angle, self.angle_noise)
            )
            obs.append(np.array(walker_obs + neighbor_obs))

            shaping = -5.0 * abs(walker_obs[0])
            rewards[i] = shaping - self.prev_shaping[i]
            self.prev_shaping[i] = shaping

        package_shaping = self.forward_reward * 130 * self.package.position.x / SCALE
        rewards += package_shaping - self.prev_package_shaping
        self.prev_package_shaping = package_shaping

        self.scroll = (
            xpos.mean()
            - VIEWPORT_W / SCALE / 5
            - (self.n_walkers - 1) * WALKER_SEPERATION * TERRAIN_STEP
        )

        done = [False] * self.n_walkers
        for i, (fallen, walker) in enumerate(zip(self.fallen_walkers, self.walkers)):
            if fallen:
                rewards[i] += self.fall_reward
                if self.remove_on_fall:
                    walker._destroy()
                if not self.terminate_on_fall:
                    rewards[i] += self.terminate_reward
                done[i] = True
        if (
            (self.terminate_on_fall and np.sum(self.fallen_walkers) > 0)
            or self.game_over
            or self.package.position.x < 0
        ):
            rewards += self.terminate_reward
            done = [True] * self.n_walkers
        elif (
            self.package.position.x
            > (self.terrain_length - TERRAIN_GRASS) * TERRAIN_STEP
        ):
            done = [True] * self.n_walkers

        return rewards, done, obs

    def step(self, action, agent_id, is_last):
        # action is array of size 4
        action = action.reshape(4)
        assert self.walkers[agent_id].hull is not None, agent_id
        self.walkers[agent_id].apply_action(action)
        if is_last:
            self.world.Step(1.0 / FPS, 6 * 30, 2 * 30)
            rewards, done, mod_obs = self.scroll_subroutine()
            self.last_obs = mod_obs
            global_reward = rewards.mean()
            local_reward = rewards * self.local_ratio
            self.last_rewards = (
                global_reward * (1.0 - self.local_ratio)
                + local_reward * self.local_ratio
            )
            self.last_dones = done
            self.frames = self.frames + 1

        if self.render_mode == "human":
            self.render()

    def get_last_rewards(self):
        return dict(
            zip(
                list(range(self.n_walkers)),
                map(lambda r: np.float64(r), self.last_rewards),
            )
        )

    def get_last_dones(self):
        return dict(zip(list(range(self.n_walkers)), self.last_dones))

    def get_last_obs(self):
        return dict(
            zip(
                list(range(self.n_walkers)),
                [walker.get_observation() for walker in self.walkers],
            )
        )

    def observe(self, agent):
        o = self.last_obs[agent]
        o = np.array(o, dtype=np.float32)
        return o

    def state(self):
        all_walker_obs = self.get_last_obs()
        all_walker_obs = np.array(list(all_walker_obs.values())).flatten()
        package_obs = np.array(
            [
                self.package.position.x,
                self.package.position.y,
                self.package.angle,
            ]
        )
        global_state = np.concatenate((all_walker_obs, package_obs)).astype(np.float32)

        return global_state

    def render(self, close=False):
        if close:
            self.close()
            return

        offset = 200  # compensates for the negative coordinates
        render_scale = SCALE / self.package_scale / 0.75
        if self.screen is None:
            pygame.init()
            self.screen = pygame.display.set_mode((VIEWPORT_W, VIEWPORT_H))
            pygame.display.set_caption("Multiwalker")

        self.surf = pygame.Surface(
            (VIEWPORT_W + self.scroll * render_scale + offset, VIEWPORT_H)
        )

        pygame.draw.polygon(
            self.surf,
            color=(215, 215, 255),
            points=[
                (self.scroll * render_scale + offset, 0),
                (self.scroll * render_scale + VIEWPORT_W + offset, 0),
                (self.scroll * render_scale + VIEWPORT_W + offset, VIEWPORT_H),
                (self.scroll * render_scale + offset, VIEWPORT_H),
            ],
        )

        for poly, x1, x2 in self.cloud_poly:
            if x2 < self.scroll / 2:
                continue
            if x1 > self.scroll / 2 + VIEWPORT_W / SCALE * self.package_scale:
                continue
            gfxdraw.aapolygon(
                self.surf,
                [
                    (
                        p[0] * render_scale + self.scroll * render_scale / 2 + offset,
                        p[1] * render_scale,
                    )
                    for p in poly
                ],
                (255, 255, 255),
            )
            gfxdraw.filled_polygon(
                self.surf,
                [
                    (
                        p[0] * render_scale + self.scroll * render_scale / 2 + offset,
                        p[1] * render_scale,
                    )
                    for p in poly
                ],
                (255, 255, 255),
            )

        for poly, color in self.terrain_poly:
            if poly[1][0] < self.scroll:
                continue
            if poly[0][0] > self.scroll + VIEWPORT_W / SCALE * self.package_scale:
                continue
            scaled_poly = []
            for coord in poly:
                scaled_poly.append(
                    [coord[0] * render_scale + offset, coord[1] * render_scale]
                )
            gfxdraw.aapolygon(self.surf, scaled_poly, color)
            gfxdraw.filled_polygon(self.surf, scaled_poly, color)

        self.lidar_render = (self.lidar_render + 1) % 100
        i = self.lidar_render
        for walker in self.walkers:
            if i < 2 * len(walker.lidar):
                l_dis = (
                    walker.lidar[i]
                    if i < len(walker.lidar)
                    else walker.lidar[len(walker.lidar) - i - 1]
                )
                pygame.draw.line(
                    self.surf,
                    color=(255, 0, 0),
                    start_pos=(
                        l_dis.p1[0] * render_scale + offset,
                        l_dis.p1[1] * render_scale,
                    ),
                    end_pos=(
                        l_dis.p2[0] * render_scale + offset,
                        l_dis.p2[1] * render_scale,
                    ),
                    width=1,
                )

        for obj in self.drawlist:
            for f in obj.fixtures:
                trans = f.body.transform
                if type(f.shape) is circleShape:
                    pygame.draw.circle(
                        self.surf,
                        color=obj.color1,
                        center=trans * f.shape.pos * render_scale + offset,
                        radius=f.shape.radius * render_scale,
                    )
                    pygame.draw.circle(
                        self.surf,
                        color=obj.color2,
                        center=trans * f.shape.pos * render_scale + offset,
                        radius=f.shape.radius * render_scale,
                    )
                else:
                    path = [trans * v * render_scale for v in f.shape.vertices]
                    path = [[c[0] + offset, c[1]] for c in path]
                    if len(path) > 2:
                        gfxdraw.aapolygon(self.surf, path, obj.color1)
                        gfxdraw.filled_polygon(self.surf, path, obj.color1)
                        path.append(path[0])
                        gfxdraw.aapolygon(self.surf, path, obj.color2)
                    else:
                        pygame.draw.aaline(
                            self.surf,
                            start_pos=path[0],
                            end_pos=path[1],
                            color=obj.color2,
                        )

        flagy1 = TERRAIN_HEIGHT * render_scale
        flagy2 = flagy1 + 50 * render_scale / SCALE
        x = TERRAIN_STEP * 3 * render_scale + offset
        pygame.draw.aaline(
            self.surf, color=(0, 0, 0), start_pos=(x, flagy1), end_pos=(x, flagy2)
        )

        f = [
            (x, flagy2),
            (x, flagy2 - 10 * render_scale / SCALE),
            (x + 25 * render_scale / SCALE, flagy2 - 5 * render_scale / SCALE),
        ]
        pygame.draw.polygon(self.surf, color=(230, 51, 0), points=f)
        pygame.draw.lines(
            self.surf, color=(0, 0, 0), points=f + [f[0]], width=1, closed=False
        )

        self.surf = pygame.transform.flip(self.surf, False, True)
        self.screen.blit(self.surf, (-self.scroll * render_scale - offset, 0))
        if self.render_mode == "human":
            pygame.event.pump()
            pygame.display.update()
        elif self.render_mode == "rgb_array":
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(self.screen)), axes=(1, 0, 2)
            )

    def _generate_package(self):
        init_x = np.mean(self.start_x)
        init_y = TERRAIN_HEIGHT + 3 * LEG_H
        self.package = self.world.CreateDynamicBody(
            position=(init_x, init_y),
            fixtures=fixtureDef(
                shape=polygonShape(
                    vertices=[
                        (x * self.package_scale / SCALE, y / SCALE)
                        for x, y in PACKAGE_POLY
                    ]
                ),
                density=1.0,
                friction=0.5,
                categoryBits=0x004,
                # maskBits=0x001,  # collide only with ground
                restitution=0.0,
            ),  # 0.99 bouncy
        )
        self.package.color1 = (127, 102, 229)
        self.package.color2 = (76, 76, 127)

    def _generate_terrain(self, hardcore):
        GRASS, STUMP, STAIRS, PIT, _STATES_ = range(5)
        state = GRASS
        velocity = 0.0
        y = TERRAIN_HEIGHT
        counter = TERRAIN_STARTPAD
        oneshot = False
        self.terrain = []
        self.terrain_x = []
        self.terrain_y = []
        for i in range(self.terrain_length):
            x = i * TERRAIN_STEP
            self.terrain_x.append(x)

            if state == GRASS and not oneshot:
                velocity = 0.8 * velocity + 0.01 * np.sign(TERRAIN_HEIGHT - y)
                if i > TERRAIN_STARTPAD:
                    velocity += self.np_random.uniform(-1, 1) / SCALE
                y += velocity

            elif state == PIT and oneshot:
                counter = self.np_random.integers(3, 5)
                poly = [
                    (x, y),
                    (x + TERRAIN_STEP, y),
                    (x + TERRAIN_STEP, y - 4 * TERRAIN_STEP),
                    (x, y - 4 * TERRAIN_STEP),
                ]
                t = self.world.CreateStaticBody(
                    fixtures=fixtureDef(
                        shape=polygonShape(vertices=poly), friction=FRICTION
                    )
                )
                t.color1, t.color2 = (255, 255, 255), (153, 153, 153)
                self.terrain.append(t)
                t = self.world.CreateStaticBody(
                    fixtures=fixtureDef(
                        shape=polygonShape(
                            vertices=[
                                (p[0] + TERRAIN_STEP * counter, p[1]) for p in poly
                            ]
                        ),
                        friction=FRICTION,
                    )
                )
                t.color1, t.color2 = (255, 255, 255), (153, 153, 153)
                self.terrain.append(t)
                counter += 2
                original_y = y

            elif state == PIT and not oneshot:
                y = original_y
                if counter > 1:
                    y -= 4 * TERRAIN_STEP

            elif state == STUMP and oneshot:
                counter = self.np_random.integers(1, 3)
                poly = [
                    (x, y),
                    (x + counter * TERRAIN_STEP, y),
                    (x + counter * TERRAIN_STEP, y + counter * TERRAIN_STEP),
                    (x, y + counter * TERRAIN_STEP),
                ]
                t = self.world.CreateStaticBody(
                    fixtures=fixtureDef(
                        shape=polygonShape(vertices=poly), friction=FRICTION
                    )
                )
                t.color1, t.color2 = (255, 255, 255), (153, 153, 153)
                self.terrain.append(t)

            elif state == STAIRS and oneshot:
                stair_height = +1 if self.np_random.random() > 0.5 else -1
                stair_width = self.np_random.integers(4, 5)
                stair_steps = self.np_random.integers(3, 5)
                original_y = y
                for s in range(stair_steps):
                    poly = [
                        (
                            x + (s * stair_width) * TERRAIN_STEP,
                            y + (s * stair_height) * TERRAIN_STEP,
                        ),
                        (
                            x + ((1 + s) * stair_width) * TERRAIN_STEP,
                            y + (s * stair_height) * TERRAIN_STEP,
                        ),
                        (
                            x + ((1 + s) * stair_width) * TERRAIN_STEP,
                            y + (-1 + s * stair_height) * TERRAIN_STEP,
                        ),
                        (
                            x + (s * stair_width) * TERRAIN_STEP,
                            y + (-1 + s * stair_height) * TERRAIN_STEP,
                        ),
                    ]
                    t = self.world.CreateStaticBody(
                        fixtures=fixtureDef(
                            shape=polygonShape(vertices=poly), friction=FRICTION
                        )
                    )
                    t.color1, t.color2 = (255, 255, 255), (153, 153, 153)
                    self.terrain.append(t)
                counter = stair_steps * stair_width

            elif state == STAIRS and not oneshot:
                s = stair_steps * stair_width - counter - stair_height
                n = s / stair_width
                y = original_y + (n * stair_height) * TERRAIN_STEP

            oneshot = False
            self.terrain_y.append(y)
            counter -= 1
            if counter == 0:
                counter = self.np_random.integers(TERRAIN_GRASS / 2, TERRAIN_GRASS)
                if state == GRASS and hardcore:
                    state = self.np_random.integers(1, _STATES_)
                    oneshot = True
                else:
                    state = GRASS
                    oneshot = True

        self.terrain_poly = []
        for i in range(self.terrain_length - 1):
            poly = [
                (self.terrain_x[i], self.terrain_y[i]),
                (self.terrain_x[i + 1], self.terrain_y[i + 1]),
            ]
            t = self.world.CreateStaticBody(
                fixtures=fixtureDef(shape=edgeShape(vertices=poly), friction=FRICTION)
            )
            color = (76, 255 if i % 2 == 0 else 204, 76)
            t.color1 = color
            t.color2 = color
            self.terrain.append(t)
            color = (102, 153, 76)
            poly += [(poly[1][0], 0), (poly[0][0], 0)]
            self.terrain_poly.append((poly, color))
        self.terrain.reverse()

    def _generate_clouds(self):
        # Sorry for the clouds, couldn't resist
        self.cloud_poly = []
        for i in range(self.terrain_length // 20):
            x = self.np_random.uniform(0, self.terrain_length) * TERRAIN_STEP
            y = VIEWPORT_H / SCALE * 3 / 4
            poly = [
                (
                    x
                    + 15 * TERRAIN_STEP * math.sin(3.14 * 2 * a / 5)
                    + self.np_random.uniform(0, 5 * TERRAIN_STEP),
                    y
                    + 5 * TERRAIN_STEP * math.cos(3.14 * 2 * a / 5)
                    + self.np_random.uniform(0, 5 * TERRAIN_STEP),
                )
                for a in range(5)
            ]
            x1 = min(p[0] for p in poly)
            x2 = max(p[0] for p in poly)
            self.cloud_poly.append((poly, x1, x2))
