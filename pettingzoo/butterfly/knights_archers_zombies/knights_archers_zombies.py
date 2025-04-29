# noqa: D212, D415
"""
# Knights Archers Zombies ('KAZ')

```{figure} butterfly_knights_archers_zombies.gif
:width: 200px
:name: knights_archers_zombies
```

This environment is part of the <a href='..'>butterfly environments</a>. Please read that page first for general information.

| Import               | `from pettingzoo.butterfly import knights_archers_zombies_v10` |
|----------------------|----------------------------------------------------------------|
| Actions              | Discrete                                                       |
| Parallel API         | Yes                                                            |
| Manual Control       | Yes                                                            |
| Agents               | `agents= ['archer_0', 'archer_1', 'knight_0', 'knight_1']`     |
| Agents               | 4                                                              |
| Action Shape         | (1,)                                                           |
| Action Values        | [0, 5]                                                         |
| Observation Shape    | (512, 512, 3)                                                  |
| Observation Values   | (0, 255)                                                       |
| State Shape          | (720, 1280, 3)                                                 |
| State Values         | (0, 255)                                                       |


Zombies walk from the top border of the screen down to the bottom border in unpredictable paths. The agents you control are knights and archers (default 2 knights and 2 archers) that are initially positioned at the bottom border of the screen. Each agent can rotate clockwise or counter-clockwise
and move forward or backward. Each agent can also attack to kill zombies. When a knight attacks, it swings a mace in an arc in front of its current heading direction. When an archer attacks, it fires an arrow in a straight line in the direction of the archer's heading. The game ends when all
agents die (collide with a zombie) or a zombie reaches the bottom screen border. A knight is rewarded 1 point when its mace hits and kills a zombie. An archer is rewarded 1 point when one of their arrows hits and kills a zombie.

### Actions
Each agent acts independently. The action space is [0,5] with the following meanings:

* 0 - move forward
* 1 - move backward
* 2 - turn counter clockwise
* 3 - turn clockwise
* 4 - use weapon
* 5 - do nothing

Movement and turning is done at a fixed rate.

### Observations
There are two possible observation types for this environment, vectorized (including two additional subtypes - sequence and typemasked) and image-based.

#### Vectorized (Default)
Pass the argument `obs_method='vector'` to the environment.

The observation is an (N+1)x5 array for each agent, where `N = num_archers + num_knights + num_swords + max_arrows + max_zombies`.
> Note that `num_swords = num_knights`

The ordering of the rows of the observation look something like this:
```
[
[current agent],
[archer 1],
...,
[archer N],
[knight 1],
...
[knight M],
[sword 1],
...
[sword M],
[arrow 1],
...
[arrow max_arrows],
[zombie 1],
...
[zombie max_zombies]
]
```

In total, there will be N+1 rows. Rows with no entities will be all 0, but the ordering of the entities will not change.

**Vector Breakdown**

This breaks down what a row in the observation means. All distances are normalized to [0, 1].
Note that for positions, [0, 0] is the top left corner of the image. Down is positive y, Left is positive x.

For the vector for `current agent`:
- The first value means nothing and will always be 0.
- The next four values are the position and angle of the current agent.
  - The first two values are position values, normalized to the width and height of the image respectively.
  - The final two values are heading of the agent represented as a unit vector.

For everything else:
- Each row of the matrix (this is an 5 wide vector) has a breakdown that looks something like this:
  - The first value is the absolute distance between an entity and the current agent.
  - The next four values are relative position and absolute angles of each entity relative to the current agent.
    - The first two values are position values relative to the current agent.
    - The final two values are the angle of the entity represented as a directional unit vector relative to the world.

**Typemasks**

There is an option to prepend a typemask to each row vector. This can be enabled by passing `obs_method='vector-masked'` as a kwarg.

The typemask is a 6 wide vector, that looks something like this:
```
[0., 0., 0., 1., 0., 0.]
```

Each value corresponds to either
```
[zombie, archer, knight, sword, arrow, current agent]
```

If there is no entity there, the whole typemask (as well as the whole state vector) will be 0.

As a result, setting `obs_method='vector-masked'` results in the observation being a (N+1)x11 vector.

**Sequence Space** (Experimental)

There is an option to also pass `obs_method='vector-sequence'` as a kwarg to the environment. This just removes all non-existent entities from the observation and state vectors. Note that this is **still experimental** as the state and observation size
are no longer constant. In particular, `N` is now a variable number.

#### Image-based
Pass the argument `obs_method='image'` to the environment.

Each agent observes the environment as a square region around itself, with its own body in the center of the square. The observation is represented as a 512x512 pixel image around the agent, or in other words, a 16x16 agent sized space around the agent.
Each pixel is defined as RGB values in range [0, 255]. Areas outside of the game box are returned as black pixels: (0,0,0).
Dead agents return all pixels as black


### Arguments

``` python
knights_archers_zombies_v10.env(
  spawn_delay=20,
  num_archers=2,
  num_knights=2,
  max_zombies=10,
  max_arrows=10,
  killable_knights=True,
  killable_archers=True,
  line_death=False,
  max_cycles=900,
  obs_method="vector",
)
```

`spawn_delay`: how many cycles before a new zombie is spawned. A higher number means zombies are spawned at a slower rate.

`num_archers`:  how many archer agents initially spawn.

`num_knights`:  how many knight agents initially spawn.

`max_zombies`: maximum number of zombies that can exist at a time

`max_arrows`: maximum number of arrows that can exist at a time

`killable_knights`:  if set to False, knight agents cannot be killed by zombies.

`killable_archers`:  if set to False, archer agents cannot be killed by zombies.

`line_death`:  if set to False, agents do not die when they touch the top or bottom border. If True, agents die as soon as they touch the top or bottom border.

`obs_method`: method of observations to use. Options are 'vector' (default), 'image', 'vector-sequence', or 'vector-masked'. See docs above for details.


### Version History

* v10: Add vectorizable state space (1.17.0)
* v9: Code rewrite and numerous fixes (1.16.0)
* v8: Code cleanup and several bug fixes (1.14.0)
* v7: Minor bug fix relating to end of episode crash (1.6.0)
* v6: Fixed reward structure (1.5.2)
* v5: Removed black death argument (1.5.0)
* v4: Fixed observation and rendering issues (1.4.2)
* v3: Misc bug fixes, bumped PyGame and PyMunk version (1.4.0)
* v2: Fixed bug in how `dones` were computed (1.3.1)
* v1: Fixes to how all environments handle premature death (1.3.0)
* v0: Initial versions release (1.0.0)

"""

from __future__ import annotations

import os
import sys
from enum import Enum
from itertools import repeat
from typing import Any

import gymnasium
import numpy as np
import numpy.typing as npt
import pygame
from gymnasium.spaces import Box, Discrete, Sequence
from gymnasium.utils import EzPickle, seeding
from typing_extensions import TypeAlias

from pettingzoo import AECEnv
from pettingzoo.butterfly.knights_archers_zombies.src import constants as const
from pettingzoo.butterfly.knights_archers_zombies.src.constants import Actions
from pettingzoo.butterfly.knights_archers_zombies.src.img import get_image
from pettingzoo.butterfly.knights_archers_zombies.src.interval import Interval
from pettingzoo.butterfly.knights_archers_zombies.src.players import (
    Archer,
    Knight,
    Player,
    is_archer,
    is_knight,
)
from pettingzoo.butterfly.knights_archers_zombies.src.zombie import Zombie
from pettingzoo.utils import AgentSelector, wrappers
from pettingzoo.utils.conversions import parallel_wrapper_fn

sys.dont_write_bytecode = True


__all__ = ["env", "parallel_env", "raw_env"]


AgentID = str
ObsTypeVector: TypeAlias = npt.NDArray[np.float64]
ObsTypeImage: TypeAlias = npt.NDArray[np.uint8]
ObsType: TypeAlias = ObsTypeImage | ObsTypeVector
ActionType = int
StateTypeVector: TypeAlias = npt.NDArray[np.float64]
StateTypeImage: TypeAlias = npt.NDArray[np.uint8]
StateType: TypeAlias = ObsTypeImage | ObsTypeVector


class ObsOptions(Enum):
    """Types of Observations supported."""

    IMAGE = "image"  # uses ObsTypeImage
    VECTOR = "vector"  # uses ObsTypeVector
    VECTOR_SEQUENCE = "vector-sequence"  # uses ObsTypeVector
    VECTOR_MASKED = "vector-masked"  # uses ObsTypeVector


def env(**kwargs: Any) -> AECEnv[AgentID, ObsType, ActionType]:
    aec_env: AECEnv[AgentID, ObsType, ActionType] = raw_env(**kwargs)
    aec_env = wrappers.AssertOutOfBoundsWrapper(aec_env)
    aec_env = wrappers.OrderEnforcingWrapper(aec_env)
    return aec_env


parallel_env = parallel_wrapper_fn(env)


class raw_env(AECEnv[AgentID, ObsType, ActionType], EzPickle):
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "name": "knights_archers_zombies_v10",
        "is_parallelizable": True,
        "render_fps": const.FPS,
        "has_manual_policy": True,
    }

    def __init__(
        self,
        spawn_delay: int = 20,
        num_archers: int = 2,
        num_knights: int = 2,
        max_zombies: int = 10,
        max_arrows: int = 10,
        killable_knights: bool = True,
        killable_archers: bool = True,
        line_death: bool = False,
        max_cycles: int = 900,
        obs_method: str = "vector",
        render_mode: str | None = None,
    ) -> None:
        EzPickle.__init__(
            self,
            spawn_delay=spawn_delay,
            num_archers=num_archers,
            num_knights=num_knights,
            max_zombies=max_zombies,
            max_arrows=max_arrows,
            killable_knights=killable_knights,
            killable_archers=killable_archers,
            line_death=line_death,
            max_cycles=max_cycles,
            obs_method=obs_method,
            render_mode=render_mode,
        )
        if render_mode is not None and render_mode not in self.metadata["render_modes"]:
            raise ValueError(f"render_mode: '{render_mode}' is not supported.")
        try:
            self.obs_type = ObsOptions(obs_method)
        except ValueError as e:
            raise ValueError(f"Invalid 'obs_method': {obs_method}") from e

        # variable state space
        self.sequence_space = self.obs_type == ObsOptions.VECTOR_SEQUENCE
        self.vector_state = self.obs_type != ObsOptions.IMAGE

        # agents + zombies + weapons
        self.num_tracked = (
            num_archers + num_knights + max_zombies + num_knights + max_arrows
        )

        self.use_typemasks = self.obs_type in [
            ObsOptions.VECTOR_SEQUENCE,
            ObsOptions.VECTOR_MASKED,
        ]
        self.typemask_width = 6
        self.vector_width = 4 + self.typemask_width if self.use_typemasks else 4

        # Game Status
        self.zombie_spawn_interval = Interval(spawn_delay)
        self.frames = 0
        self.render_mode = render_mode
        self.screen_dims = [const.SCREEN_WIDTH, const.SCREEN_HEIGHT]
        self.screen = self._get_screen()

        # Game Constants
        self._seed()
        self.max_cycles = max_cycles
        self.killable_knights = killable_knights
        self.killable_archers = killable_archers
        self.line_death = line_death
        self.num_archers = num_archers
        self.num_knights = num_knights
        self.max_zombies = max_zombies
        self.max_arrows = max_arrows

        # Represents agents to remove at end of cycle
        self.kill_list: list[AgentID] = []
        self.agent_map: dict[str, Player] = {}
        self.dead_agents: list[AgentID] = []

        self.possible_agents = self._build_possible_agents()
        self.observation_spaces = self._build_observation_spaces()
        self.action_spaces = self._build_action_spaces()
        self.state_space = self._build_state_space()

        self.agents = self.possible_agents[:]

        if self.render_mode == "human":
            self.clock = pygame.time.Clock()

        self.background = self._generate_background()

        self._agent_selector = AgentSelector(self.agents)
        self.reinit()

    def _build_possible_agents(self) -> list[AgentID]:
        possible_agents: list[AgentID] = []

        for i in range(self.num_archers):
            agent_name = f"archer_{i}"
            possible_agents.append(agent_name)

        for i in range(self.num_knights):
            agent_name = f"knight_{i}"
            possible_agents.append(agent_name)

        return possible_agents

    def _generate_background(self) -> pygame.Surface:
        """Returns a background surface formed from image components."""
        background = pygame.Surface((const.SCREEN_WIDTH, const.SCREEN_HEIGHT))
        left_wall = get_image(os.path.join("img", "left_wall.png"))
        right_wall = get_image(os.path.join("img", "right_wall.png"))
        right_wall_rect = right_wall.get_rect()
        right_wall_rect.left = const.SCREEN_WIDTH - right_wall_rect.width
        floor_patch1 = get_image(os.path.join("img", "patch1.png"))
        floor_patch2 = get_image(os.path.join("img", "patch2.png"))
        floor_patch3 = get_image(os.path.join("img", "patch3.png"))
        floor_patch4 = get_image(os.path.join("img", "patch4.png"))

        background.fill((66, 40, 53))
        background.blit(left_wall, left_wall.get_rect())
        background.blit(right_wall, right_wall_rect)
        background.blit(floor_patch1, (500, 500))
        background.blit(floor_patch2, (900, 30))
        background.blit(floor_patch3, (150, 430))
        background.blit(floor_patch4, (300, 50))
        background.blit(floor_patch1, (1000, 250))
        return background

    def _build_observation_spaces(self) -> dict[AgentID, gymnasium.spaces.Space[Any]]:
        """Create and return the observation spaces for the object."""
        if self.vector_state:
            if self.sequence_space:
                shape = [self.vector_width + 1]
            else:
                shape = [self.num_tracked + 1, self.vector_width + 1]

            box_space = Box(low=-1.0, high=1.0, shape=shape, dtype=np.float64)

            if self.sequence_space:
                obs_space: Box | Sequence = Sequence(space=box_space, stack=True)
            else:
                obs_space = box_space
        else:  # image space
            obs_space = Box(low=0, high=255, shape=[512, 512, 3], dtype=np.uint8)

        return {i: obs_space for i in self.possible_agents}

    def _build_action_spaces(self) -> dict[AgentID, gymnasium.spaces.Space[Any]]:
        """Create and return the action spaces for the object."""
        return {i: Discrete(6) for i in self.possible_agents}

    def _build_state_space(self) -> Box:
        """Create and return the state space for the object."""
        if self.vector_state:
            shape = [self.num_tracked, self.vector_width]
            return Box(low=-1.0, high=1.0, shape=shape, dtype=np.float64)
        # image space
        shape = [const.SCREEN_HEIGHT, const.SCREEN_WIDTH, 3]
        return Box(low=0, high=255, shape=shape, dtype=np.uint8)

    def observation_space(self, agent: AgentID) -> gymnasium.spaces.Space[Any]:
        return self.observation_spaces[agent]

    def action_space(self, agent: AgentID) -> gymnasium.spaces.Space[Any]:
        return self.action_spaces[agent]

    def _seed(self, seed: int | None = None) -> None:
        self.np_random, seed = seeding.np_random(seed)

    def do_zombie_turn(self) -> None:
        """Have zombies attack, move, and then spawn."""
        # Any players in comtact with zombies are killed unless
        # the env was created with killable players turned off
        for zombie in self.zombie_list:
            zombie_hit_list = pygame.sprite.spritecollide(
                zombie, self.player_list, True
            )
            for player in zombie_hit_list:
                if is_archer(player) and not self.killable_archers:
                    continue
                if is_knight(player) and not self.killable_knights:
                    continue
                self._remove_agent(player)

        # have zombies move
        for zombie in self.zombie_list:
            zombie.act()

        # spawn new zombie if appropriate
        if len(self.zombie_list) < self.max_zombies:
            if self.zombie_spawn_interval.increment():
                zombie = Zombie(self.np_random)
                self.zombie_list.add(zombie)

    def _remove_agent(self, agent: Player) -> None:
        """Mark an agent as dead."""
        agent.is_alive = False
        if agent in self.player_list:
            self.player_list.remove(agent)
        if agent.agent_name not in self.kill_list:
            self.kill_list.append(agent.agent_name)
        if is_knight(agent):
            agent.weapons.empty()

    def apply_weapons(self) -> None:
        """Move the weapons and remove any zombies that were hit.

        The weapons are moved along their path.
        If an arrow hits a zombie, both the arrow and the zombie are removed.
        The archer that fired the arrow is awarded 1 point.

        If a sword hits a zombie, the zombie is removed but the sword is not.
        The knight wielding a sword is awarded 1 point.
        """
        for agent in self.agent_map.values():
            for weapon in list(agent.weapons):
                weapon.act()

                if not weapon.is_active:
                    agent.weapons.remove(weapon)

        # remove zombies hit by weapons
        for agent in self.agent_map.values():
            for weapon in list(agent.weapons):
                zombie_hit_list = pygame.sprite.spritecollide(
                    weapon, self.zombie_list, True
                )
                for zombie in zombie_hit_list:
                    self.zombie_list.remove(zombie)
                    weapon.player.score += 1
                    if is_archer(agent):
                        # remove the arrow that hit the zombie
                        agent.weapons.remove(weapon)

    @property
    def num_active_arrows(self) -> int:
        num_arrows = 0
        for agent in self.agent_map.values():
            if is_archer(agent):
                num_arrows += len(agent.weapons)
        return num_arrows

    @property
    def num_active_swords(self) -> int:
        num_swords = 0
        for agent in self.agent_map.values():
            if is_knight(agent):
                num_swords += len(agent.weapons)
        return num_swords

    def _observe_image(self, agent: AgentID) -> ObsTypeImage:
        """Return observation for given agent as an image based observation."""
        # the observation is based on the image, so we need to update it
        # this is already done in render(), which is called when render_mode
        # is "human", so skip in that case
        if self.render_mode != "human":
            self.draw()

        screen = pygame.surfarray.pixels3d(self.screen)

        agent_obj = self.agent_map[agent]
        agent_position = (agent_obj.rect.x, agent_obj.rect.y)

        shape = self.observation_spaces[agent].shape
        assert shape is not None
        obs = np.zeros(shape, dtype=np.uint8)
        if agent_obj.is_alive:
            min_x = agent_position[0] - 256
            max_x = agent_position[0] + 256
            min_y = agent_position[1] - 256
            max_y = agent_position[1] + 256
            lower_y_bound = max(min_y, 0)
            upper_y_bound = min(max_y, const.SCREEN_HEIGHT)
            lower_x_bound = max(min_x, 0)
            upper_x_bound = min(max_x, const.SCREEN_WIDTH)
            startx = lower_x_bound - min_x
            starty = lower_y_bound - min_y
            endx = 512 + upper_x_bound - max_x
            endy = 512 + upper_y_bound - max_y
            obs[startx:endx, starty:endy, :] = screen[
                lower_x_bound:upper_x_bound, lower_y_bound:upper_y_bound, :
            ]

        return np.swapaxes(obs, 1, 0)

    def _observe_vector(self, agent: AgentID) -> ObsTypeVector:
        """Return observation for given agent as a vector based observation."""
        agent_obj = self.agent_map[agent]

        # get the agent position
        agent_state = agent_obj.get_vector_state(self.use_typemasks)
        agent_pos = np.expand_dims(agent_state[-4:-2], axis=0)

        # get vector state of everything
        vector_state = self.get_vector_state()
        state = vector_state[:, -4:]  # trim type mask, if present
        is_dead = np.sum(np.abs(state), axis=1) == 0.0
        all_typemasks = vector_state[:, :-4]
        all_pos = state[:, 0:2]
        all_ang = state[:, 2:4]

        # get relative positions
        rel_pos = all_pos - agent_pos

        # get norm of relative distance
        norm_pos = np.linalg.norm(rel_pos, axis=1, keepdims=True) / np.sqrt(2)

        # kill dead things
        all_typemasks[is_dead] *= 0
        all_ang[is_dead] *= 0
        rel_pos[is_dead] *= 0
        norm_pos[is_dead] *= 0

        # combine the typemasks, positions and angles
        state = np.concatenate([all_typemasks, norm_pos, rel_pos, all_ang], axis=-1)

        # set current agent data
        full_agent_state = np.zeros((1, self.vector_width + 1), dtype=np.float64)
        if self.use_typemasks:
            full_agent_state[0, 5] = 1.0
        full_agent_state[0, -4:] = agent_state[-4:]
        full_agent_state[0, -5] = 0.0  # distance to self

        # prepend agent state to the observation
        state = np.concatenate([full_agent_state, state], axis=0)
        if self.sequence_space:
            # remove pure zero rows if using sequence space
            state = state[~np.all(state == 0, axis=-1)]

        return state

    def observe(self, agent: AgentID) -> ObsType:
        """Return the observation for the given agent."""
        if self.vector_state:
            return self._observe_vector(agent)
        return self._observe_image(agent)

    def state(self) -> StateType:
        """Returns an observation of the global environment."""
        if not self.vector_state:
            # this makes a copy of the state, only including the
            # expected size. It is intentionally done without using
            # the .copy() function to accommodate a future case where
            # the screen may be larger than the expected size.
            state: StateTypeImage = pygame.surfarray.pixels3d(self.screen)[
                : const.SCREEN_WIDTH, : const.SCREEN_HEIGHT, :
            ]
            state = np.rot90(state, k=3)
            return np.fliplr(state)
        return self.get_vector_state()

    def get_vector_state(self) -> StateTypeVector:
        state: list[StateTypeVector] = []
        empty_row = np.zeros(self.vector_width)

        # handle agents - all archers then all knights
        for category in ["archer", "knight"]:
            for agent_name in self.possible_agents:
                if agent_name.startswith(category):
                    if agent_name not in self.dead_agents:
                        agent = self.agent_map[agent_name]
                        state.append(agent.get_vector_state(self.use_typemasks))
                    else:
                        state.append(empty_row)

        # handle swords
        for agent in self.agent_map.values():
            if is_knight(agent):
                for sword in agent.weapons:
                    state.append(sword.get_vector_state(self.use_typemasks))

        n_empty_swords = self.num_knights - self.num_active_swords
        state.extend(repeat(empty_row, n_empty_swords))

        # handle arrows
        for agent in self.agent_map.values():
            if is_archer(agent):
                for arrow in agent.weapons:
                    state.append(arrow.get_vector_state(self.use_typemasks))

        n_empty_arrows = self.max_arrows - self.num_active_arrows
        state.extend(repeat(empty_row, n_empty_arrows))

        # handle zombies
        for zombie in self.zombie_list:
            state.append(zombie.get_vector_state(self.use_typemasks))

        n_empty_zombies = self.max_zombies - len(self.zombie_list)
        state.extend(repeat(empty_row, n_empty_zombies))

        return np.stack(state, axis=0)

    def step(self, action: ActionType) -> None:
        # check if the particular agent is done
        if (
            self.terminations[self.agent_selection]
            or self.truncations[self.agent_selection]
        ):
            self._was_dead_step(action)
            return

        agent = self.agent_map[self.agent_selection]

        # cumulative rewards from previous iterations should be cleared
        self._cumulative_rewards[self.agent_selection] = 0
        agent.score = 0

        agent_action = Actions(action)

        # archer can't attack if the number of arrows exceeds
        # the max count. In this case, change the action to no action.
        if is_archer(agent) and agent_action == Actions.ACTION_ATTACK:
            if self.num_active_arrows >= self.max_arrows:
                agent_action = Actions.ACTION_NONE

        if not agent.is_timed_out(agent_action):
            out_of_bounds = agent.act(agent_action)
        else:
            out_of_bounds = False

        if self.line_death and out_of_bounds:
            self._remove_agent(agent)

        # Do these things once per cycle
        if self._agent_selector.is_last():
            # Update the weapons and use them against zombies
            self.apply_weapons()

            self.do_zombie_turn()

            self._check_game_over()
            self.frames += 1

        terminate = self.game_over
        truncate = self.frames >= self.max_cycles
        self.terminations = {a: terminate for a in self.agents}
        self.truncations = {a: truncate for a in self.agents}

        # manage the kill list
        if self._agent_selector.is_last():
            # start iterating on only the living agents
            _live_agents = self.agents[:]
            for k in self.kill_list:
                # kill the agent
                _live_agents.remove(k)
                # set the termination for this agent for one round
                self.terminations[k] = True
                # add that we know this guy is dead
                self.dead_agents.append(k)

            # reset the kill list
            self.kill_list = []

            # reinit the agent selector with existing agents
            self._agent_selector.reinit(_live_agents)

        # if there still exist agents, get the next one
        if len(self._agent_selector.agent_order):
            self.agent_selection = self._agent_selector.next()

        self._clear_rewards()
        next_agent = self.agent_map[self.agent_selection]
        self.rewards[self.agent_selection] = next_agent.score

        self._accumulate_rewards()
        self._deads_step_first()

        if self.render_mode == "human":
            self.render()

    def draw(self) -> None:
        self.screen.blit(self.background, (0, 0))

        # draw all the sprites
        self.zombie_list.draw(self.screen)
        for agent in self.agent_map.values():
            agent.weapons.draw(self.screen)
        self.player_list.draw(self.screen)

    def _get_screen(self) -> pygame.Surface:
        """Return a newly created pygame surface."""
        pygame.init()

        if self.render_mode == "human":
            screen = pygame.display.set_mode(self.screen_dims)
            pygame.display.set_caption("Knights, Archers, Zombies")
            return screen
        if self.render_mode == "rgb_array" or self.render_mode is None:
            return pygame.Surface(self.screen_dims)

        raise ValueError(f"Unknown render_mode: {self.render_mode}")

    def render(self) -> npt.NDArray[np.uint8] | None:
        if self.render_mode is None:
            gymnasium.logger.warn(
                "You are calling render method without specifying any render mode."
            )
            return None

        self.draw()

        observation = np.array(pygame.surfarray.pixels3d(self.screen))
        if self.render_mode == "human":
            pygame.display.flip()
            self.clock.tick(self.metadata["render_fps"])
        return (
            np.transpose(observation, axes=(1, 0, 2))
            if self.render_mode == "rgb_array"
            else None
        )

    def close(self) -> None:
        """Close the screen, if open."""
        pygame.quit()

    def _check_zombie_escape(self) -> bool:
        """Return True if Zombies won by reaching the end."""
        for zombie in self.zombie_list:
            if zombie.rect.y > const.SCREEN_HEIGHT - const.ZOMBIE_Y_SPEED:
                return True
        return False

    def _check_zombie_killall(self) -> bool:
        """Return True if Zombies won by killing all players."""
        return not bool(self.player_list)

    def _check_game_over(self) -> None:
        """Determine whether game is over and set self.game_over with result."""
        self.game_over = self._check_zombie_escape() or self._check_zombie_killall()

    def reinit(self) -> None:
        self.game_over = False

        self.zombie_list: pygame.sprite.Group[Any] = pygame.sprite.Group()
        self.player_list: pygame.sprite.Group[Any] = pygame.sprite.Group()

        self.agent_map = {}
        self.agents = []
        self.dead_agents = []

        for agent in self.possible_agents:
            if agent.startswith("archer"):
                player: Player = Archer(agent_name=agent)
            elif agent.startswith("knight"):
                player = Knight(agent_name=agent)
            else:
                raise ValueError(f"Unknown agent type: {agent}")
            self.player_list.add(player)
            player.offset(int(agent[-1]) * 50, 0)
            self.agent_map[agent] = player
            self.agents.append(agent)

        self.screen = self._get_screen()
        if self.render_mode is not None:
            self.render()

        self.frames = 0

    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> None:
        if seed is not None:
            self._seed(seed=seed)
        self.agents = self.possible_agents
        self._agent_selector.reinit(self.agents)
        self.agent_selection = self._agent_selector.next()
        self.rewards = {i: 0 for i in self.agents}
        self._cumulative_rewards = {a: 0 for a in self.agents}
        self.terminations = {i: False for i in self.agents}
        self.truncations = {i: False for i in self.agents}
        self.infos = {i: {} for i in self.agents}
        self.reinit()


# The original code for this game, that was added by J K Terry, was
# created by Dipam Patel in a different repository (hence the git history)

# Game art purchased from https://finalbossblues.itch.io/time-fantasy-monsters
# and https://finalbossblues.itch.io/icons
