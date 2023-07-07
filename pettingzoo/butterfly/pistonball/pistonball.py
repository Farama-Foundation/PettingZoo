# noqa: D212, D415
"""
# Pistonball

```{figure} butterfly_pistonball.gif
:width: 200px
:name: pistonball
```

This environment is part of the <a href='..'>butterfly environments</a>. Please read that page first for general information.

| Import               | `from pettingzoo.butterfly import pistonball_v6`     |
|----------------------|------------------------------------------------------|
| Actions              | Either                                               |
| Parallel API         | Yes                                                  |
| Manual Control       | Yes                                                  |
| Agents               | `agents= ['piston_0', 'piston_1', ..., 'piston_19']` |
| Agents               | 20                                                   |
| Action Shape         | (1,)                                                 |
| Action Values        | [-1, 1]                                              |
| Observation Shape    | (457, 120, 3)                                        |
| Observation Values   | (0, 255)                                             |
| State Shape          | (560, 880, 3)                                        |
| State Values         | (0, 255)                                             |


This is a simple physics based cooperative game where the goal is to move the ball to the left wall of the game border by activating the vertically moving pistons. Each piston agent's observation is an RGB image of the two pistons (or the wall) next to the agent and the space above them. Every
piston can be acted on in any given time. The action space in discrete mode is 0 to move down, 1 to stay still, and 2 to move up. In continuous mode, the value in the range [-1, 1] is proportional to the amount that the pistons are raised or lowered by. Continuous actions are scaled by a factor
of 4, so that in both the discrete and continuous action space, the action 1 will move a piston 4 pixels up, and -1 will move pistons 4 pixels down.

Accordingly, pistons must learn highly coordinated emergent behavior to achieve an optimal policy for the environment. Each agent gets a reward that is a combination of how much the ball moved left overall and how much the ball moved left if it was close to the piston (i.e. movement the piston
contributed to). A piston is considered close to the ball if it is directly below any part of the ball. Balancing the ratio between these local and global rewards appears to be critical to learning this environment, and as such is an environment parameter. The local reward applied is 0.5 times
the change in the ball's x-position. Additionally, the global reward is change in x-position divided by the starting position, times 100, plus the `time_penalty` (default -0.1). For each piston, the reward is `local_ratio` * local_reward + (1-`local_ratio`) * global_reward. The local reward is
applied to pistons surrounding the ball while the global reward is provided to all pistons.

Pistonball uses the chipmunk physics engine, and are thus the physics are about as realistic as in the game Angry Birds.

Keys *a* and *d* control which piston is selected to move (initially the rightmost piston is selected) and keys *w* and *s* move the piston in the vertical direction.


### Arguments


``` python
pistonball_v6.env(n_pistons=20, time_penalty=-0.1, continuous=True,
random_drop=True, random_rotate=True, ball_mass=0.75, ball_friction=0.3,
ball_elasticity=1.5, max_cycles=125)
```

`n_pistons`: The number of pistons (agents) in the environment.

`time_penalty`: Amount of reward added to each piston each time step. Higher values mean higher weight towards getting the ball across the screen to terminate the game.

`continuous`:  If true, piston action is a real value between -1 and 1 which is added to the piston height. If False, then action is a discrete value to move a unit up or down.

`random_drop`:  If True, ball will initially spawn in a random x value. If False, ball will always spawn at x=800

`random_rotate`:  If True, ball will spawn with a random angular momentum

`ball_mass`:  Sets the mass of the ball physics object

`ball_friction`:  Sets the friction of the ball physics object

`ball_elasticity`:  Sets the elasticity of the ball physics object

`max_cycles`:  after max_cycles steps all agents will return done


### Version History

* v6: Fix ball bouncing off of left wall.
* v5: Ball moving into the left column due to physics engine imprecision no longer gives additional reward
* v4: Changed default arguments for `max_cycles` and `continuous`, bumped PyMunk version (1.6.0)
* v3: Refactor, added number of pistons argument, minor visual changes (1.5.0)
* v2: Misc fixes, bumped PyGame and PyMunk version (1.4.0)
* v1: Fix to continuous mode (1.0.1)
* v0: Initial versions release (1.0.0)

"""

import math

import gymnasium
import numpy as np
import pygame
import pymunk
import pymunk.pygame_util
from gymnasium.utils import EzPickle, seeding

from pettingzoo import AECEnv
from pettingzoo.butterfly.pistonball.manual_policy import ManualPolicy
from pettingzoo.utils import agent_selector, wrappers
from pettingzoo.utils.conversions import parallel_wrapper_fn

_image_library = {}

FPS = 20

__all__ = ["ManualPolicy", "env", "parallel_env", "raw_env"]


def get_image(path):
    from os import path as os_path

    cwd = os_path.dirname(__file__)
    image = pygame.image.load(cwd + "/" + path)
    sfc = pygame.Surface(image.get_size(), flags=pygame.SRCALPHA)
    sfc.blit(image, (0, 0))
    return sfc


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
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "name": "pistonball_v6",
        "is_parallelizable": True,
        "render_fps": FPS,
        "has_manual_policy": True,
    }

    def __init__(
        self,
        n_pistons=20,
        time_penalty=-0.1,
        continuous=True,
        random_drop=True,
        random_rotate=True,
        ball_mass=0.75,
        ball_friction=0.3,
        ball_elasticity=1.5,
        max_cycles=125,
        render_mode=None,
    ):
        EzPickle.__init__(
            self,
            n_pistons=n_pistons,
            time_penalty=time_penalty,
            continuous=continuous,
            random_drop=random_drop,
            random_rotate=random_rotate,
            ball_mass=ball_mass,
            ball_friction=ball_friction,
            ball_elasticity=ball_elasticity,
            max_cycles=max_cycles,
            render_mode=render_mode,
        )
        self.dt = 1.0 / FPS
        self.n_pistons = n_pistons
        self.piston_head_height = 11
        self.piston_width = 40
        self.piston_height = 40
        self.piston_body_height = 23
        self.piston_radius = 5
        self.wall_width = 40
        self.ball_radius = 40
        self.screen_width = (2 * self.wall_width) + (self.piston_width * self.n_pistons)
        self.screen_height = 560
        y_high = self.screen_height - self.wall_width - self.piston_body_height
        y_low = self.wall_width
        obs_height = y_high - y_low

        assert (
            self.piston_width == self.wall_width
        ), "Wall width and piston width must be equal for observation calculation"
        assert self.n_pistons > 1, "n_pistons must be greater than 1"

        self.agents = ["piston_" + str(r) for r in range(self.n_pistons)]
        self.possible_agents = self.agents[:]
        self.agent_name_mapping = dict(zip(self.agents, list(range(self.n_pistons))))
        self._agent_selector = agent_selector(self.agents)

        self.observation_spaces = dict(
            zip(
                self.agents,
                [
                    gymnasium.spaces.Box(
                        low=0,
                        high=255,
                        shape=(obs_height, self.piston_width * 3, 3),
                        dtype=np.uint8,
                    )
                ]
                * self.n_pistons,
            )
        )
        self.continuous = continuous
        if self.continuous:
            self.action_spaces = dict(
                zip(
                    self.agents,
                    [gymnasium.spaces.Box(low=-1, high=1, shape=(1,))] * self.n_pistons,
                )
            )
        else:
            self.action_spaces = dict(
                zip(self.agents, [gymnasium.spaces.Discrete(3)] * self.n_pistons)
            )
        self.state_space = gymnasium.spaces.Box(
            low=0,
            high=255,
            shape=(self.screen_height, self.screen_width, 3),
            dtype=np.uint8,
        )

        pygame.init()
        pymunk.pygame_util.positive_y_is_up = False

        self.render_mode = render_mode
        self.renderOn = False
        self.screen = pygame.Surface((self.screen_width, self.screen_height))
        self.max_cycles = max_cycles

        self.piston_sprite = get_image("piston.png")
        self.piston_body_sprite = get_image("piston_body.png")
        self.background = get_image("background.png")
        self.random_drop = random_drop
        self.random_rotate = random_rotate

        self.pistonList = []
        self.pistonRewards = []  # Keeps track of individual rewards
        self.recentFrameLimit = (
            20  # Defines what "recent" means in terms of number of frames.
        )
        self.recentPistons = set()  # Set of pistons that have touched the ball recently
        self.time_penalty = time_penalty
        # TODO: this was a bad idea and the logic this uses should be removed at some point
        self.local_ratio = 0
        self.ball_mass = ball_mass
        self.ball_friction = ball_friction
        self.ball_elasticity = ball_elasticity

        self.terminate = False
        self.truncate = False

        self.pixels_per_position = 4
        self.n_piston_positions = 16

        self.screen.fill((0, 0, 0))
        self.draw_background()
        # self.screen.blit(self.background, (0, 0))

        self.render_rect = pygame.Rect(
            self.wall_width,  # Left
            self.wall_width,  # Top
            self.screen_width - (2 * self.wall_width),  # Width
            self.screen_height
            - (2 * self.wall_width)
            - self.piston_body_height,  # Height
        )

        # Blit background image if ball goes out of bounds. Ball radius is 40
        self.valid_ball_position_rect = pygame.Rect(
            self.render_rect.left + self.ball_radius,  # Left
            self.render_rect.top + self.ball_radius,  # Top
            self.render_rect.width - (2 * self.ball_radius),  # Width
            self.render_rect.height - (2 * self.ball_radius),  # Height
        )

        self.frames = 0

        self._seed()

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)

    def observe(self, agent):
        observation = pygame.surfarray.pixels3d(self.screen)
        i = self.agent_name_mapping[agent]
        # Set x bounds to include 40px left and 40px right of piston
        x_high = self.wall_width + self.piston_width * (i + 2)
        x_low = self.wall_width + self.piston_width * (i - 1)
        y_high = self.screen_height - self.wall_width - self.piston_body_height
        y_low = self.wall_width
        cropped = np.array(observation[x_low:x_high, y_low:y_high, :])
        observation = np.rot90(cropped, k=3)
        observation = np.fliplr(observation)
        return observation

    def state(self):
        """Returns an observation of the global environment."""
        state = pygame.surfarray.pixels3d(self.screen).copy()
        state = np.rot90(state, k=3)
        state = np.fliplr(state)
        return state

    def enable_render(self):
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Pistonball")

        self.renderOn = True
        # self.screen.blit(self.background, (0, 0))
        self.draw_background()
        self.draw()

    def close(self):
        if self.screen is not None:
            pygame.quit()
            self.screen = None

    def add_walls(self):
        top_left = (self.wall_width, self.wall_width)
        top_right = (self.screen_width - self.wall_width, self.wall_width)
        bot_left = (self.wall_width, self.screen_height - self.wall_width)
        bot_right = (
            self.screen_width - self.wall_width,
            self.screen_height - self.wall_width,
        )
        walls = [
            pymunk.Segment(self.space.static_body, top_left, top_right, 1),  # Top wall
            pymunk.Segment(self.space.static_body, top_left, bot_left, 1),  # Left wall
            pymunk.Segment(
                self.space.static_body, bot_left, bot_right, 1
            ),  # Bottom wall
            pymunk.Segment(self.space.static_body, top_right, bot_right, 1),  # Right
        ]
        for wall in walls:
            wall.friction = 0.64
            self.space.add(wall)

    def add_ball(self, x, y, b_mass, b_friction, b_elasticity):
        mass = b_mass
        radius = 40
        inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
        body = pymunk.Body(mass, inertia)
        body.position = x, y
        # radians per second
        if self.random_rotate:
            body.angular_velocity = self.np_random.uniform(-6 * math.pi, 6 * math.pi)
        shape = pymunk.Circle(body, radius, (0, 0))
        shape.friction = b_friction
        shape.elasticity = b_elasticity
        self.space.add(body, shape)
        return body

    def add_piston(self, space, x, y):
        piston = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        piston.position = x, y
        segment = pymunk.Segment(
            piston,
            (0, 0),
            (self.piston_width - (2 * self.piston_radius), 0),
            self.piston_radius,
        )
        segment.friction = 0.64
        segment.color = pygame.color.THECOLORS["blue"]
        space.add(piston, segment)
        return piston

    def move_piston(self, piston, v):
        def cap(y):
            maximum_piston_y = (
                self.screen_height
                - self.wall_width
                - (self.piston_height - self.piston_head_height)
            )
            if y > maximum_piston_y:
                y = maximum_piston_y
            elif y < maximum_piston_y - (
                self.n_piston_positions * self.pixels_per_position
            ):
                y = maximum_piston_y - (
                    self.n_piston_positions * self.pixels_per_position
                )
            return y

        piston.position = (
            piston.position[0],
            cap(piston.position[1] - v * self.pixels_per_position),
        )

    def reset(self, seed=None, options=None):
        if seed is not None:
            self._seed(seed)
        self.space = pymunk.Space(threaded=False)
        self.add_walls()
        # self.space.threads = 2
        self.space.gravity = (0.0, 750.0)
        self.space.collision_bias = 0.0001
        self.space.iterations = 10  # 10 is default in PyMunk

        self.pistonList = []
        maximum_piston_y = (
            self.screen_height
            - self.wall_width
            - (self.piston_height - self.piston_head_height)
        )
        for i in range(self.n_pistons):
            # Multiply by 0.5 to use only the lower half of possible positions
            possible_y_displacements = np.arange(
                0,
                0.5 * self.pixels_per_position * self.n_piston_positions,
                self.pixels_per_position,
            )
            piston = self.add_piston(
                self.space,
                self.wall_width
                + self.piston_radius
                + self.piston_width * i,  # x position
                maximum_piston_y
                # y position
                - self.np_random.choice(possible_y_displacements),
            )
            piston.velociy = 0
            self.pistonList.append(piston)

        self.horizontal_offset = 0
        self.vertical_offset = 0
        horizontal_offset_range = 30
        vertical_offset_range = 15
        if self.random_drop:
            self.vertical_offset = self.np_random.integers(
                -vertical_offset_range, vertical_offset_range + 1
            )
            self.horizontal_offset = self.np_random.integers(
                -horizontal_offset_range, horizontal_offset_range + 1
            )
        ball_x = (
            self.screen_width
            - self.wall_width
            - self.ball_radius
            - horizontal_offset_range
            + self.horizontal_offset
        )
        ball_y = (
            self.screen_height
            - self.wall_width
            - self.piston_body_height
            - self.ball_radius
            - (0.5 * self.pixels_per_position * self.n_piston_positions)
            - vertical_offset_range
            + self.vertical_offset
        )

        # Ensure ball starts somewhere right of the left wall
        ball_x = max(ball_x, self.wall_width + self.ball_radius + 1)

        self.ball = self.add_ball(
            ball_x, ball_y, self.ball_mass, self.ball_friction, self.ball_elasticity
        )
        self.ball.angle = 0
        self.ball.velocity = (0, 0)
        if self.random_rotate:
            self.ball.angular_velocity = self.np_random.uniform(
                -6 * math.pi, 6 * math.pi
            )

        self.lastX = int(self.ball.position[0] - self.ball_radius)
        self.distance = self.lastX - self.wall_width

        self.draw_background()
        self.draw()

        self.agents = self.possible_agents[:]

        self._agent_selector.reinit(self.agents)
        self.agent_selection = self._agent_selector.next()

        self.terminate = False
        self.truncate = False
        self.rewards = dict(zip(self.agents, [0 for _ in self.agents]))
        self._cumulative_rewards = dict(zip(self.agents, [0 for _ in self.agents]))
        self.terminations = dict(zip(self.agents, [False for _ in self.agents]))
        self.truncations = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [{} for _ in self.agents]))

        self.frames = 0

    def draw_background(self):
        outer_walls = pygame.Rect(
            0,  # Left
            0,  # Top
            self.screen_width,  # Width
            self.screen_height,  # Height
        )
        outer_wall_color = (58, 64, 65)
        pygame.draw.rect(self.screen, outer_wall_color, outer_walls)
        inner_walls = pygame.Rect(
            self.wall_width / 2,  # Left
            self.wall_width / 2,  # Top
            self.screen_width - self.wall_width,  # Width
            self.screen_height - self.wall_width,  # Height
        )
        inner_wall_color = (68, 76, 77)
        pygame.draw.rect(self.screen, inner_wall_color, inner_walls)
        self.draw_pistons()

    def draw_pistons(self):
        piston_color = (65, 159, 221)
        x_pos = self.wall_width
        for piston in self.pistonList:
            self.screen.blit(
                self.piston_body_sprite,
                (x_pos, self.screen_height - self.wall_width - self.piston_body_height),
            )
            # Height is the size of the blue part of the piston. 6 is the piston base height (the gray part at the bottom)
            height = (
                self.screen_height
                - self.wall_width
                - self.piston_body_height
                - (piston.position[1] + self.piston_radius)
                + (self.piston_body_height - 6)
            )
            body_rect = pygame.Rect(
                piston.position[0]
                + self.piston_radius
                + 1,  # +1 to match up to piston graphics
                piston.position[1] + self.piston_radius + 1,
                18,
                height,
            )
            pygame.draw.rect(self.screen, piston_color, body_rect)
            x_pos += self.piston_width

    def draw(self):
        if self.render_mode is None:
            return
        # redraw the background image if ball goes outside valid position
        if not self.valid_ball_position_rect.collidepoint(self.ball.position):
            # self.screen.blit(self.background, (0, 0))
            self.draw_background()

        ball_x = int(self.ball.position[0])
        ball_y = int(self.ball.position[1])

        color = (255, 255, 255)
        pygame.draw.rect(self.screen, color, self.render_rect)
        color = (65, 159, 221)
        pygame.draw.circle(self.screen, color, (ball_x, ball_y), self.ball_radius)

        line_end_x = ball_x + (self.ball_radius - 1) * np.cos(self.ball.angle)
        line_end_y = ball_y + (self.ball_radius - 1) * np.sin(self.ball.angle)
        color = (58, 64, 65)
        pygame.draw.line(
            self.screen, color, (ball_x, ball_y), (line_end_x, line_end_y), 3
        )  # 39 because it kept sticking over by 1 at 40

        for piston in self.pistonList:
            self.screen.blit(
                self.piston_sprite,
                (
                    piston.position[0] - self.piston_radius,
                    piston.position[1] - self.piston_radius,
                ),
            )
        self.draw_pistons()

    def get_nearby_pistons(self):
        # first piston = leftmost
        nearby_pistons = []
        ball_pos = int(self.ball.position[0] - self.ball_radius)
        closest = abs(self.pistonList[0].position.x - ball_pos)
        closest_piston_index = 0
        for i in range(self.n_pistons):
            next_distance = abs(self.pistonList[i].position.x - ball_pos)
            if next_distance < closest:
                closest = next_distance
                closest_piston_index = i

        if closest_piston_index > 0:
            nearby_pistons.append(closest_piston_index - 1)
        nearby_pistons.append(closest_piston_index)
        if closest_piston_index < self.n_pistons - 1:
            nearby_pistons.append(closest_piston_index + 1)

        return nearby_pistons

    def get_local_reward(self, prev_position, curr_position):
        local_reward = 0.5 * (prev_position - curr_position)
        return local_reward

    def render(self):
        if self.render_mode is None:
            gymnasium.logger.warn(
                "You are calling render method without specifying any render mode."
            )
            return

        if self.render_mode == "human" and not self.renderOn:
            # sets self.renderOn to true and initializes display
            self.enable_render()

        self.draw_background()
        self.draw()

        observation = np.array(pygame.surfarray.pixels3d(self.screen))
        if self.render_mode == "human":
            pygame.display.flip()
        return (
            np.transpose(observation, axes=(1, 0, 2))
            if self.render_mode == "rgb_array"
            else None
        )

    def step(self, action):
        if (
            self.terminations[self.agent_selection]
            or self.truncations[self.agent_selection]
        ):
            self._was_dead_step(action)
            return

        action = np.asarray(action)
        agent = self.agent_selection
        if self.continuous:
            self.move_piston(self.pistonList[self.agent_name_mapping[agent]], action)
        else:
            self.move_piston(
                self.pistonList[self.agent_name_mapping[agent]], action - 1
            )

        self.space.step(self.dt)
        if self._agent_selector.is_last():
            ball_min_x = int(self.ball.position[0] - self.ball_radius)
            ball_next_x = (
                self.ball.position[0]
                - self.ball_radius
                + self.ball.velocity[0] * self.dt
            )
            if ball_next_x <= self.wall_width + 1:
                self.terminate = True
            # ensures that the ball can't pass through the wall
            ball_min_x = max(self.wall_width, ball_min_x)
            self.draw()
            local_reward = self.get_local_reward(self.lastX, ball_min_x)
            # Opposite order due to moving right to left
            global_reward = (100 / self.distance) * (self.lastX - ball_min_x)
            if not self.terminate:
                global_reward += self.time_penalty
            total_reward = [
                global_reward * (1 - self.local_ratio)
            ] * self.n_pistons  # start with global reward
            local_pistons_to_reward = self.get_nearby_pistons()
            for index in local_pistons_to_reward:
                total_reward[index] += local_reward * self.local_ratio
            self.rewards = dict(zip(self.agents, total_reward))
            self.lastX = ball_min_x
            self.frames += 1
        else:
            self._clear_rewards()

        self.truncate = self.frames >= self.max_cycles
        # Clear the list of recent pistons for the next reward cycle
        if self.frames % self.recentFrameLimit == 0:
            self.recentPistons = set()
        if self._agent_selector.is_last():
            self.terminations = dict(
                zip(self.agents, [self.terminate for _ in self.agents])
            )
            self.truncations = dict(
                zip(self.agents, [self.truncate for _ in self.agents])
            )

        self.agent_selection = self._agent_selector.next()
        self._cumulative_rewards[agent] = 0
        self._accumulate_rewards()

        if self.render_mode == "human":
            self.render()


# Game art created by J K Terry
