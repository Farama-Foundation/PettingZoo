# noqa: D212, D415
"""
# Cooperative Pong

```{figure} butterfly_cooperative_pong.gif
:width: 200px
:name: cooperative_pong
```

This environment is part of the <a href='..'>butterfly environments</a>. Please read that page first for general information.

| Import               | `from pettingzoo.butterfly import cooperative_pong_v6` |
|----------------------|--------------------------------------------------------|
| Actions              | Discrete                                               |
| Parallel API         | Yes                                                    |
| Manual Control       | Yes                                                    |
| Agents               | `agents= ['paddle_0', 'paddle_1']`                     |
| Agents               | 2                                                      |
| Action Shape         | Discrete(3)                                            |
| Action Values        | [0, 1, 2]                                              |
| Observation Shape    | (280, 480, 3)                                          |
| Observation Values   | [0, 255]                                               |
| State Shape          | (280, 480, 3)                                          |
| State Values         | (0, 255)                                               |


Cooperative pong is a game of simple pong, where the objective is to keep the ball in play for the longest time. The game is over when the ball goes out of bounds from either the left or right edge of the screen. There are two agents (paddles), one that moves along the left edge and the other that
moves along the right edge of the screen. All collisions of the ball are elastic. The ball always starts moving in a random direction from the center of the screen with each reset. To make learning a little more challenging, the right paddle is tiered cake-shaped by default.
The observation space of each agent is the entire screen. There are three possible actions for the agents (_move up/down_ or do nothing). If the ball stays within bounds, each agent receives a reward of `max_reward / max_cycles` (default 0.11) at each timestep. Otherwise, each agent receives a
reward of `off_screen_penalty` (default -10) and the game ends.


### Manual Control

Move the left paddle using the 'W' and 'S' keys. Move the right paddle using 'UP' and 'DOWN' arrow keys.

### Arguments

``` python
cooperative_pong_v6.env(
    ball_speed = 9,
    left_paddle_speed = 12,
    right_paddle_speed = 12,
    cake_paddle = True,
    max_cycles = 900,
    bounce_randomness = False,
    max_reward = 100,
    off_screen_penalty = -10,
    render_mode = None,
    render_ratio = 2,
    render_fps = 15,
)
```

`ball_speed`: Speed of ball (in pixels). Note that if the ball speed is set too high, it is possible for it to move through the paddle and out of bounds.

`left_paddle_speed`: Speed of left paddle (in pixels)

`right_paddle_speed`: Speed of right paddle (in pixels)

`cake_paddle`: If True, the right paddle cakes the shape of a 4 tiered wedding cake

`max_cycles`: After max_cycles steps all agents will return done

`bounce_randomness`: If True, each collision of the ball with the paddles adds a small random angle to the direction of the ball, with the speed of the ball remaining unchanged.

`max_reward`: Total reward given to each agent over max_cycles timesteps

`off_screen_penalty`: Negative reward penalty for each agent if the ball goes off the screen

`render_mode`: Render mode for the env (either None, "human", or "rgb_array")

`render_ratio`: Scaling ratio for rendering the screen (controls display size, larger value gives smaller screen)

`render_fps`: Speed that the game is run (in frames per second, higher values give faster game)


### Version History

* v6: Fixed incorrect termination condition and random bounce behaviour (1.25.5)
* v5: Fixed ball teleporting bugs
* v4: Added max_reward and off_screen_penalty arguments and changed default, fixed glitch where ball would occasionally teleport, reward redesign (1.14.0)
* v3: Change observation space to include entire screen (1.10.0)
* v2: Misc fixes (1.4.0)
* v1: Fixed bug in how `dones` were computed (1.3.1)
* v0: Initial versions release (1.0.0)

"""

from __future__ import annotations

from typing import Any, Literal, NewType, cast

import gymnasium
import numpy as np
import numpy.typing as npt
import pygame
from gymnasium.utils import EzPickle, seeding

from pettingzoo import AECEnv
from pettingzoo.butterfly.cooperative_pong.ball import Ball
from pettingzoo.butterfly.cooperative_pong.cake_paddle import CakePaddle
from pettingzoo.butterfly.cooperative_pong.paddle import Paddle
from pettingzoo.utils import wrappers
from pettingzoo.utils.agent_selector import AgentSelector
from pettingzoo.utils.conversions import parallel_wrapper_fn

FPS = 15


__all__ = ["env", "raw_env", "parallel_env"]


AgentID = NewType("AgentID", str)
ObsType = NewType("ObsType", npt.NDArray[np.integer])
ActionType = Literal[0, 1, 2]
StateType = NewType("StateType", npt.NDArray[np.integer])


def get_valid_angle(randomizer: np.random.Generator) -> float:
    """Generate an initial angle for the ball's motion.

    This generates an angle in [0, 2*np.pi) that excludes the following
    angle ranges (given in degrees):
    (90 +- ver_deg_range)
    (270 +- ver_deg_range)
    (180 +- hor_deg_range)
    (0 +- hor_deg_range)

    for the default values of ver_deg_range = 25 and hor_deg_range = 10:
    (65, 115), (245, 295), (170, 190), (0, 10), (350, 360)

    Args:
        randomizer: The random generator to use in generating the angle

    Returns:
        The angle generated (radians)
    """
    ver_deg_range = 25
    hor_deg_range = 10
    a1 = np.radians(90 - ver_deg_range)
    b1 = np.radians(90 + ver_deg_range)
    a2 = np.radians(270 - ver_deg_range)
    b2 = np.radians(270 + ver_deg_range)
    c1 = np.radians(180 - hor_deg_range)
    d1 = np.radians(180 + hor_deg_range)
    c2 = np.radians(360 - hor_deg_range)
    d2 = np.radians(0 + hor_deg_range)

    angle = 0.0
    while (
        (a1 < angle < b1)
        or (a2 < angle < b2)
        or (c1 < angle < d1)
        or (angle > c2)
        or (angle < d2)
    ):
        angle = 2 * np.pi * randomizer.random()

    return angle


class CooperativePong:
    """The base env for Cooperative Pong."""

    def __init__(
        self,
        randomizer: np.random.Generator,
        ball_speed: float = 9,
        left_paddle_speed: float = 12,
        right_paddle_speed: float = 12,
        cake_paddle: bool = True,
        max_cycles: int = 900,
        bounce_randomness: bool = False,
        max_reward: float = 100,
        off_screen_penalty: float = -10,
        render_mode: str | None = None,
        render_ratio: int = 2,
        render_fps: int = 15,
    ) -> None:
        """Initializes the CooperativePong game.

        Args:
            randomizer: Random generator
            ball_speed: Speed of ball (in pixels) If the ball speed is set too
              high, it is possible for it to move through the paddle and out of
              bounds. A warning will be printed in this case.
            left_paddle_speed: Speed of left paddle (in pixels)
            right_paddle_speed: Speed of right paddle (in pixels)
            cake_paddle: If True, the right paddle cakes the shape of a
              4 tiered wedding cake
            max_cycles: After max_cycles steps all agents will return done
            bounce_randomness: If True, each collision of the ball with the
              paddles adds a small random angle to the direction of the ball,
              with the speed of the ball remaining unchanged.
            max_reward: Total reward given to each agent over max_cycles timesteps
            off_screen_penalty: Negative reward penalty for each agent if the ball
              goes off the screen
            render_mode: Render mode for the env (either None, "human", or
              "rgb_array")
            render_ratio: Scaling ratio for rendering the screen (controls display
              size, larger value gives smaller screen)
            render_fps: Speed that the game is run (in frames per second, higher
              values give faster game)
        """
        super().__init__()

        pygame.init()
        self.num_agents = 2

        self.render_ratio = render_ratio

        # Display screen
        self.s_width, self.s_height = 960 // render_ratio, 560 // render_ratio
        self.area = pygame.Rect(0, 0, self.s_width, self.s_height)
        self.max_reward = max_reward
        self.off_screen_penalty = off_screen_penalty

        # define action and observation spaces
        self.action_space = [
            gymnasium.spaces.Discrete(3) for _ in range(self.num_agents)
        ]
        self.observation_space = [
            gymnasium.spaces.Box(
                low=0, high=255, shape=(self.s_height, self.s_width, 3), dtype=np.uint8
            )
            for _ in range(self.num_agents)
        ]
        # define the global space of the environment or state
        self.state_space = gymnasium.spaces.Box(
            low=0, high=255, shape=((self.s_height, self.s_width, 3)), dtype=np.uint8
        )

        self.render_mode = render_mode
        self.screen: pygame.Surface | None = None

        # set speed
        self.speed = [ball_speed, left_paddle_speed, right_paddle_speed]

        self.max_cycles = max_cycles

        # paddles
        l_paddle_dims = (20 // render_ratio, 80 // render_ratio)
        self.p0 = Paddle(l_paddle_dims, left_paddle_speed, "left")
        if cake_paddle:
            r_paddle_dims = (30 // render_ratio, 120 // render_ratio)
            self.p1: Paddle = CakePaddle(r_paddle_dims, right_paddle_speed, "right")
        else:
            r_paddle_dims = (20 // render_ratio, 100 // render_ratio)
            self.p1 = Paddle(r_paddle_dims, right_paddle_speed, "right")

        if ball_speed > l_paddle_dims[0] or ball_speed > r_paddle_dims[0]:
            gymnasium.logger.warn(
                "Ball speed is larger than width of the paddle. This can cause the ball "
                "to move through the paddle, leading to incorrect behavior."
            )

        self.agents = [AgentID("paddle_0"), AgentID("paddle_1")]

        self.ball = Ball(
            randomizer,
            (20 // render_ratio, 20 // render_ratio),
            ball_speed,
            bounce_randomness,
        )
        self.randomizer = randomizer

        self.reinit()

        self.render_fps = render_fps
        if self.render_mode == "human":
            self.clock = pygame.time.Clock()

    def reinit(self) -> None:
        """Reinitialize datastructures."""
        self.rewards = dict(zip(self.agents, [0.0] * len(self.agents)))
        self.terminations = dict(zip(self.agents, [False] * len(self.agents)))
        self.truncations = dict(zip(self.agents, [False] * len(self.agents)))
        self.infos: dict[AgentID, dict[str, Any]] = dict(
            zip(self.agents, [{}] * len(self.agents))
        )
        self.score = 0.0

    def reset(self) -> None:
        """Reset the env for a new run."""
        # reset ball and paddle init conditions
        # set the direction to an angle between [0, 2*np.pi)
        angle = get_valid_angle(self.randomizer)
        self.ball.reset(center=self.area.center, angle=angle)

        self.p0.reset(self.area, self.speed[1])
        self.p1.reset(self.area, self.speed[2])

        self.terminate = False
        self.truncate = False

        self.num_frames = 0

        self.reinit()

        # Pygame surface required even for render_mode == None, as observations are taken from pixel values
        # Observe
        if self.render_mode != "human":
            self.screen = pygame.Surface((self.s_width, self.s_height))

        self.render()

    def close(self) -> None:
        """Close the pygame window, if open."""
        if self.screen is not None:
            pygame.quit()
            self.screen = None

    def render(self) -> npt.NDArray[np.integer] | None:
        """Render the current state.

        The result of this call depends on the render_mode:
        * None: a warning in printed and nothing else is done
        * "human": the image is displayed in a Pygame window
        * "rgb_array": an numeric array of the screen is returned

        Returns:
            If render_mode is "rgb_array", an array of the screen
            image as integers is returned. Otherwise, None is returned.
        """
        if self.render_mode is None:
            gymnasium.logger.warn(
                "You are calling render method without specifying any render mode."
            )
            return None

        if self.screen is None:
            if self.render_mode == "human":
                self.screen = pygame.display.set_mode((self.s_width, self.s_height))
                pygame.display.set_caption("Cooperative Pong")
        assert self.screen is not None
        self.draw()

        observation = np.array(pygame.surfarray.pixels3d(self.screen))
        if self.render_mode == "human":
            pygame.display.flip()
            self.clock.tick(self.render_fps)
        return (
            np.transpose(observation, axes=(1, 0, 2))
            if self.render_mode == "rgb_array"
            else None
        )

    def observe(self) -> ObsType:
        """Return the current screen as an array."""
        assert self.screen is not None
        observation = np.array(pygame.surfarray.pixels3d(self.screen))
        observation = np.rot90(
            observation, k=3
        )  # now the obs is laid out as H, W as rows and cols
        observation = np.fliplr(observation)  # laid out in the correct order
        return cast(ObsType, observation)

    def state(self) -> StateType:
        """Returns an observation of the global environment."""
        assert self.screen is not None
        state = pygame.surfarray.pixels3d(self.screen).copy()
        state = np.rot90(state, k=3)
        state = np.fliplr(state)
        return cast(StateType, state)

    def draw(self) -> None:
        """Draw the paddles and ball on the screen."""
        assert self.screen is not None
        pygame.draw.rect(self.screen, (0, 0, 0), self.area)
        self.p0.draw(self.screen)
        self.p1.draw(self.screen)
        self.ball.draw(self.screen)

    def step(self, action: ActionType, agent: AgentID) -> None:
        """Update the env based on the action of the given agent.

        This will move the paddles and ball as appropriate and determine
        the new state as a result.
        When agent is the first player:
        * the rewards are zeroed
        * the left paddle (player 1) is moved
        When agent is the second player:
        * the right paddle (player 2) is moved
        * the ball is moved
        * the state (terminated/truncated/running) is determined
        * the reward/score is calculated
        * all datastructures are updated

        Args:
            action: the action to take
            agent: which agent is acting
        """
        # update p0, p1 accordingly
        # action: 0: do nothing,
        # action: 1: p[i] move up
        # action: 2: p[i] move down
        if agent == self.agents[0]:
            self.rewards = {a: 0 for a in self.agents}
            self.p0.update(self.area, action)
        elif agent == self.agents[1]:
            self.p1.update(self.area, action)

            # do the rest if not terminated
            if not self.terminate:
                # update ball position
                self.ball.update2(self.area, self.p0, self.p1)

                # do the miscellaneous stuff after the last agent has moved
                # reward is the length of time ball is in play
                reward = 0.0
                # ball is out-of-bounds
                if self.ball.is_out_of_bounds():
                    self.terminate = True
                    reward = self.off_screen_penalty
                    self.score += reward
                else:
                    self.terminate = False
                    self.num_frames += 1
                    reward = self.max_reward / self.max_cycles
                    self.score += reward
                    self.truncate = self.num_frames >= self.max_cycles

                for ag in self.agents:
                    self.rewards[ag] = reward
                    self.terminations[ag] = self.terminate
                    self.truncations[ag] = self.truncate
                    self.infos[ag] = {}

        self.render()


def env(**kwargs: Any) -> AECEnv[AgentID, ObsType, ActionType]:
    """Creates the wrapped environment."""
    aec_env: AECEnv[AgentID, ObsType, ActionType] = raw_env(**kwargs)
    aec_env = wrappers.AssertOutOfBoundsWrapper(aec_env)
    aec_env = wrappers.OrderEnforcingWrapper(aec_env)
    return aec_env


parallel_env = parallel_wrapper_fn(env)


class raw_env(AECEnv[AgentID, ObsType, ActionType], EzPickle):
    """The CooperativePong AEC environment."""

    metadata = {
        "render_modes": ["human", "rgb_array"],
        "name": "cooperative_pong_v6",
        "is_parallelizable": True,
        "render_fps": FPS,
        "has_manual_policy": True,
    }

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the environment."""
        EzPickle.__init__(self, **kwargs)
        self._kwargs = kwargs

        self._seed()

        self.agents = self.env.agents[:]
        self.possible_agents = self.agents[:]
        self._agent_selector = AgentSelector(self.agents)
        self.agent_selection = self._agent_selector.reset()

        self.action_spaces = dict(zip(self.agents, self.env.action_space))
        self.observation_spaces = dict(zip(self.agents, self.env.observation_space))
        self.state_space = self.env.state_space

        self.observations: dict[AgentID, ObsType] = {}
        self.rewards = self.env.rewards
        self.terminations = self.env.terminations
        self.truncations = self.env.truncations
        self.infos = self.env.infos

        self.score = self.env.score

        self.render_mode = self.env.render_mode

    def observation_space(self, agent: AgentID) -> gymnasium.spaces.Space[Any]:
        """Return the observation space for the given agent."""
        return self.observation_spaces[agent]

    def action_space(self, agent: AgentID) -> gymnasium.spaces.Space[Any]:
        """Return the action space for the given agent."""
        return self.action_spaces[agent]

    def _seed(self, seed: int | None = None) -> None:
        """Seed the random number generator.

        This also creates the underlying environment.
        """
        self.randomizer, seed = seeding.np_random(seed)
        self.env = CooperativePong(self.randomizer, **self._kwargs)

    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> None:
        """Reset the environment."""
        if seed is not None:
            self._seed(seed=seed)
        self.env.reset()
        self.agents = self.possible_agents[:]
        self.agent_selection = self._agent_selector.reset()
        self.rewards = self.env.rewards
        self._cumulative_rewards = {a: 0 for a in self.agents}
        self.terminations = self.env.terminations
        self.truncations = self.env.truncations
        self.infos = self.env.infos

    def observe(self, agent: AgentID) -> ObsType:
        """Return the observation for the given agent."""
        obs = self.env.observe()
        return obs

    def state(self) -> StateType:
        """Return the state for the environment."""
        state = self.env.state()
        return state

    def close(self) -> None:
        """Close the renderer."""
        self.env.close()

    def render(self) -> npt.NDArray[np.integer] | None:
        """Render the current state of the environment."""
        return self.env.render()

    def step(self, action: ActionType) -> None:
        """Take a step of the environment."""
        if (
            self.terminations[self.agent_selection]
            or self.truncations[self.agent_selection]
        ):
            self._was_dead_step(action)
            return
        agent = self.agent_selection

        self.env.step(action, agent)
        # select next agent and observe
        self.agent_selection = self._agent_selector.next()
        self.rewards = self.env.rewards
        self.terminations = self.env.terminations
        self.truncations = self.env.truncations
        self.infos = self.env.infos

        self.score = self.env.score

        self._cumulative_rewards[agent] = 0
        self._accumulate_rewards()


# This was originally created, in full, by Ananth Hari in a different repo, and was
# added in by J K Terry (which is why they're shown as the creator in the git history)
