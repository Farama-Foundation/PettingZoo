# noqa
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
There are two possible observation types for this environment, vectorized and image-based.

#### Vectorized (Default)
Pass the argument `vector_state=True` to the environment.

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

There is an option to prepend a typemask to each row vector. This can be enabled by passing `use_typemasks=True` as a kwarg.

The typemask is a 6 wide vector, that looks something like this:
```
[0., 0., 0., 1., 0., 0.]
```

Each value corresponds to either
```
[zombie, archer, knight, sword, arrow, current agent]
```

If there is no entity there, the whole typemask (as well as the whole state vector) will be 0.

As a result, setting `use_typemask=True` results in the observation being a (N+1)x11 vector.

**Transformers** (Experimental)

There is an option to also pass `transformer=True` as a kwarg to the environment. This just removes all non-existent entities from the observation and state vectors. Note that this is **still experimental** as the state and observation size are no longer constant. In particular, `N` is now a
variable number.

#### Image-based
Pass the argument `vector_state=False` to the environment.

Each agent observes the environment as a square region around itself, with its own body in the center of the square. The observation is represented as a 512x512 pixel image around the agent, or in other words, a 16x16 agent sized space around the agent.

### Manual Control

Move the archer using the 'W', 'A', 'S' and 'D' keys. Shoot the Arrow using 'F' key. Rotate the archer using 'Q' and 'E' keys.
Press 'X' key to spawn a new archer.

Move the knight using the 'I', 'J', 'K' and 'L' keys. Stab the Sword using ';' key. Rotate the knight using 'U' and 'O' keys.
Press 'M' key to spawn a new knight.



### Arguments

``` python
knights_archers_zombies_v10.env(
  spawn_rate=20,
  num_archers=2,
  num_knights=2,
  max_zombies=10,
  max_arrows=10,
  killable_knights=True,
  killable_archers=True,
  pad_observation=True,
  line_death=False,
  max_cycles=900,
  vector_state=True,
  use_typemasks=False,
  transformer=False,
```

`spawn_rate`:  how many cycles before a new zombie is spawned. A lower number means zombies are spawned at a higher rate.

`num_archers`:  how many archer agents initially spawn.

`num_knights`:  how many knight agents initially spawn.

`max_zombies`: maximum number of zombies that can exist at a time

`max_arrows`: maximum number of arrows that can exist at a time

`killable_knights`:  if set to False, knight agents cannot be killed by zombies.

`killable_archers`:  if set to False, archer agents cannot be killed by zombies.

`pad_observation`:  if agents are near edge of environment, their observation cannot form a 40x40 grid. If this is set to True, the observation is padded with black.

`line_death`:  if set to False, agents do not die when they touch the top or bottom border. If True, agents die as soon as they touch the top or bottom border.

`vector_state`: whether to use vectorized state, if set to `False`, an image-based observation will be provided instead.

`use_typemasks`: only relevant when `vector_state=True` is set, adds typemasks to the vectors.

`transformer`: **experimental**, only relevant when `vector_state=True` is set, removes non-existent entities in the vector state.


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

import os
import sys
from itertools import repeat

import gymnasium
import numpy as np
import pygame
import pygame.gfxdraw
from gymnasium.spaces import Box, Discrete
from gymnasium.utils import EzPickle, seeding

from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector, wrappers
from pettingzoo.utils.conversions import parallel_wrapper_fn

from .manual_policy import ManualPolicy  # noqa: F401
from .src import constants as const
from .src.img import get_image
from .src.players import Archer, Knight
from .src.weapons import Arrow, Sword
from .src.zombie import Zombie

sys.dont_write_bytecode = True


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


parallel_env = parallel_wrapper_fn(env)


class raw_env(AECEnv, EzPickle):

    metadata = {
        "render_modes": ["human", "rgb_array"],
        "name": "knights_archers_zombies_v10",
        "is_parallelizable": True,
        "render_fps": const.FPS,
        "has_manual_policy": True,
    }

    def __init__(
        self,
        spawn_rate=20,
        num_archers=2,
        num_knights=2,
        max_zombies=10,
        max_arrows=10,
        killable_knights=True,
        killable_archers=True,
        pad_observation=True,
        line_death=False,
        max_cycles=900,
        vector_state=True,
        use_typemasks=False,
        transformer=False,
        render_mode=None,
    ):
        EzPickle.__init__(
            self,
            spawn_rate,
            num_archers,
            num_knights,
            max_zombies,
            max_arrows,
            killable_knights,
            killable_archers,
            pad_observation,
            line_death,
            max_cycles,
            vector_state,
            use_typemasks,
            transformer,
            render_mode,
        )
        # variable state space
        self.transformer = transformer

        # whether we want RGB state or vector state
        self.vector_state = vector_state
        # agents + zombies + weapons
        self.num_tracked = (
            num_archers + num_knights + max_zombies + num_knights + max_arrows
        )
        self.use_typemasks = True if transformer else use_typemasks
        self.typemask_width = 6
        self.vector_width = 4 + self.typemask_width if use_typemasks else 4

        # Game Status
        self.frames = 0
        self.closed = False
        self.has_reset = False
        self.render_mode = render_mode
        self.render_on = False

        # Game Constants
        self.seed()
        self.spawn_rate = spawn_rate
        self.max_cycles = max_cycles
        self.pad_observation = pad_observation
        self.killable_knights = killable_knights
        self.killable_archers = killable_archers
        self.line_death = line_death
        self.num_archers = num_archers
        self.num_knights = num_knights
        self.max_zombies = max_zombies
        self.max_arrows = max_arrows

        # Represents agents to remove at end of cycle
        self.kill_list = []
        self.agent_list = []
        self.agents = []
        self.dead_agents = []

        self.agent_name_mapping = {}
        a_count = 0
        for i in range(self.num_archers):
            a_name = "archer_" + str(i)
            self.agents.append(a_name)
            self.agent_name_mapping[a_name] = a_count
            a_count += 1
        for i in range(self.num_knights):
            k_name = "knight_" + str(i)
            self.agents.append(k_name)
            self.agent_name_mapping[k_name] = a_count
            a_count += 1

        shape = (
            [512, 512, 3]
            if not self.vector_state
            else [self.num_tracked + 1, self.vector_width + 1]
        )
        low = 0 if not self.vector_state else -1.0
        high = 255 if not self.vector_state else 1.0
        dtype = np.uint8 if not self.vector_state else np.float64
        self.observation_spaces = dict(
            zip(
                self.agents,
                [
                    Box(low=low, high=high, shape=shape, dtype=dtype)
                    for _ in enumerate(self.agents)
                ],
            )
        )

        self.action_spaces = dict(
            zip(self.agents, [Discrete(6) for _ in enumerate(self.agents)])
        )

        shape = (
            [const.SCREEN_HEIGHT, const.SCREEN_WIDTH, 3]
            if not self.vector_state
            else [self.num_tracked, self.vector_width]
        )
        low = 0 if not self.vector_state else -1.0
        high = 255 if not self.vector_state else 1.0
        dtype = np.uint8 if not self.vector_state else np.float64
        self.state_space = Box(
            low=low,
            high=high,
            shape=shape,
            dtype=dtype,
        )
        self.possible_agents = self.agents

        # Initializing Pygame
        pygame.init()
        # self.WINDOW = pygame.display.set_mode([self.WIDTH, self.HEIGHT])
        self.WINDOW = pygame.Surface((const.SCREEN_WIDTH, const.SCREEN_HEIGHT))
        pygame.display.set_caption("Knights, Archers, Zombies")
        self.left_wall = get_image(os.path.join("img", "left_wall.png"))
        self.right_wall = get_image(os.path.join("img", "right_wall.png"))
        self.right_wall_rect = self.right_wall.get_rect()
        self.right_wall_rect.left = const.SCREEN_WIDTH - self.right_wall_rect.width
        self.floor_patch1 = get_image(os.path.join("img", "patch1.png"))
        self.floor_patch2 = get_image(os.path.join("img", "patch2.png"))
        self.floor_patch3 = get_image(os.path.join("img", "patch3.png"))
        self.floor_patch4 = get_image(os.path.join("img", "patch4.png"))

        self._agent_selector = agent_selector(self.agents)
        self.reinit()

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)

    # Spawn Zombies at Random Location at every 100 iterations
    def spawn_zombie(self):
        if len(self.zombie_list) < self.max_zombies:
            self.zombie_spawn_rate += 1
            zombie = Zombie(self.np_random)

            if self.zombie_spawn_rate >= self.spawn_rate:
                zombie.rect.x = self.np_random.integers(0, const.SCREEN_WIDTH)
                zombie.rect.y = 5

                self.zombie_list.add(zombie)
                self.zombie_spawn_rate = 0

    # actuate weapons
    def action_weapon(self, action, agent):
        if action == 5:
            if agent.is_knight:
                if agent.weapon_timeout > const.SWORD_TIMEOUT:
                    # make sure that the current knight doesn't have a sword already
                    if len(agent.weapons) == 0:
                        agent.weapons.add(Sword(agent))

            if agent.is_archer:
                if agent.weapon_timeout > const.ARROW_TIMEOUT:
                    # make sure that the screen has less arrows than allowable
                    if self.num_active_arrows < self.max_arrows:
                        agent.weapons.add(Arrow(agent))

    # move weapons
    def update_weapons(self):
        for agent in self.agent_list:
            for weapon in list(agent.weapons):
                weapon.update()

                if not weapon.is_active:
                    agent.weapons.remove(weapon)

    @property
    def num_active_arrows(self):
        num_arrows = 0
        for agent in self.agent_list:
            if agent.is_archer:
                num_arrows += len(agent.weapons)
        return num_arrows

    @property
    def num_active_swords(self):
        num_swords = 0
        for agent in self.agent_list:
            if agent.is_knight:
                num_swords += len(agent.weapons)
        return num_swords

    # Zombie Kills the Knight (also remove the sword)
    def zombit_hit_knight(self):
        for zombie in self.zombie_list:
            zombie_knight_list = pygame.sprite.spritecollide(
                zombie, self.knight_list, True
            )

            for knight in zombie_knight_list:
                knight.alive = False
                knight.weapons.empty()

                if knight.agent_name not in self.kill_list:
                    self.kill_list.append(knight.agent_name)

                self.knight_list.remove(knight)

    # Zombie Kills the Archer
    def zombie_hit_archer(self):
        for zombie in self.zombie_list:
            zombie_archer_list = pygame.sprite.spritecollide(
                zombie, self.archer_list, True
            )

            for archer in zombie_archer_list:
                archer.alive = False
                self.archer_list.remove(archer)
                if archer.agent_name not in self.kill_list:
                    self.kill_list.append(archer.agent_name)

    # Zombie Kills the Sword
    def sword_hit(self):
        for knight in self.knight_list:
            for sword in knight.weapons:
                zombie_sword_list = pygame.sprite.spritecollide(
                    sword, self.zombie_list, True
                )

                for zombie in zombie_sword_list:
                    self.zombie_list.remove(zombie)
                    sword.knight.score += 1

    # Zombie Kills the Arrow
    def arrow_hit(self):
        for agent in self.agent_list:
            if agent.is_archer:
                for arrow in list(agent.weapons):
                    zombie_arrow_list = pygame.sprite.spritecollide(
                        arrow, self.zombie_list, True
                    )

                    # For each zombie hit, remove the arrow, zombie and add to the score
                    for zombie in zombie_arrow_list:
                        agent.weapons.remove(arrow)
                        self.zombie_list.remove(zombie)
                        arrow.archer.score += 1

    # Zombie reaches the End of the Screen
    def zombie_endscreen(self, run, zombie_list):
        for zombie in zombie_list:
            if zombie.rect.y > const.SCREEN_HEIGHT - const.ZOMBIE_Y_SPEED:
                run = False
        return run

    # Zombie Kills all Players
    def zombie_all_players(self, run, knight_list, archer_list):
        if not knight_list and not archer_list:
            run = False
        return run

    def observe(self, agent):
        if not self.vector_state:
            screen = pygame.surfarray.pixels3d(self.WINDOW)

            i = self.agent_name_mapping[agent]
            agent_obj = self.agent_list[i]
            agent_position = (agent_obj.rect.x, agent_obj.rect.y)

            if not agent_obj.alive:
                cropped = np.zeros((512, 512, 3), dtype=np.uint8)
            else:
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
                cropped = np.zeros_like(self.observation_spaces[agent].low)
                cropped[startx:endx, starty:endy, :] = screen[
                    lower_x_bound:upper_x_bound, lower_y_bound:upper_y_bound, :
                ]

            return np.swapaxes(cropped, 1, 0)

        else:
            # get the agent
            agent = self.agent_list[self.agent_name_mapping[agent]]

            # get the agent position
            agent_state = agent.vector_state
            agent_pos = np.expand_dims(agent_state[0:2], axis=0)

            # get vector state of everything
            vector_state = self.get_vector_state()
            state = vector_state[:, -4:]
            is_dead = np.sum(np.abs(state), axis=1) == 0.0
            all_ids = vector_state[:, :-4]
            all_pos = state[:, 0:2]
            all_ang = state[:, 2:4]

            # get relative positions
            rel_pos = all_pos - agent_pos

            # get norm of relative distance
            norm_pos = np.linalg.norm(rel_pos, axis=1, keepdims=True) / np.sqrt(2)

            # kill dead things
            all_ids[is_dead] *= 0
            all_ang[is_dead] *= 0
            rel_pos[is_dead] *= 0
            norm_pos[is_dead] *= 0

            # combine the typemasks, positions and angles
            state = np.concatenate([all_ids, norm_pos, rel_pos, all_ang], axis=-1)

            # get the agent state as absolute vector
            # typemask is one longer to also include norm_pos
            if self.use_typemasks:
                typemask = np.zeros(self.typemask_width + 1)
                typemask[-2] = 1.0
            else:
                typemask = np.array([0.0])
            agent_state = agent.vector_state
            agent_state = np.concatenate([typemask, agent_state], axis=0)
            agent_state = np.expand_dims(agent_state, axis=0)

            # prepend agent state to the observation
            state = np.concatenate([agent_state, state], axis=0)

            return state

    def state(self):
        """Returns an observation of the global environment."""
        if not self.vector_state:
            state = pygame.surfarray.pixels3d(self.WINDOW).copy()
            state = np.rot90(state, k=3)
            state = np.fliplr(state)
        else:
            state = self.get_vector_state()

        return state

    def get_vector_state(self):
        state = []
        typemask = np.array([])

        # handle agents
        for agent_name in self.possible_agents:
            if agent_name not in self.dead_agents:
                agent = self.agent_list[self.agent_name_mapping[agent_name]]

                if self.use_typemasks:
                    typemask = np.zeros(self.typemask_width)
                    if agent.is_archer:
                        typemask[1] = 1.0
                    elif agent.is_knight:
                        typemask[2] = 1.0

                vector = np.concatenate((typemask, agent.vector_state), axis=0)
                state.append(vector)
            else:
                if not self.transformer:
                    state.append(np.zeros(self.vector_width))

        # handle swords
        for agent in self.agent_list:
            if agent.is_knight:
                for sword in agent.weapons:
                    if self.use_typemasks:
                        typemask = np.zeros(self.typemask_width)
                        typemask[4] = 1.0

                    vector = np.concatenate((typemask, sword.vector_state), axis=0)
                    state.append(vector)

        # handle empty swords
        if not self.transformer:
            state.extend(
                repeat(
                    np.zeros(self.vector_width),
                    self.num_knights - self.num_active_swords,
                )
            )

        # handle arrows
        for agent in self.agent_list:
            if agent.is_archer:
                for arrow in agent.weapons:
                    if self.use_typemasks:
                        typemask = np.zeros(self.typemask_width)
                        typemask[3] = 1.0

                    vector = np.concatenate((typemask, arrow.vector_state), axis=0)
                    state.append(vector)

        # handle empty arrows
        if not self.transformer:
            state.extend(
                repeat(
                    np.zeros(self.vector_width),
                    self.max_arrows - self.num_active_arrows,
                )
            )

        # handle zombies
        for zombie in self.zombie_list:
            if self.use_typemasks:
                typemask = np.zeros(self.typemask_width)
                typemask[0] = 1.0

            vector = np.concatenate((typemask, zombie.vector_state), axis=0)
            state.append(vector)

        # handle empty zombies
        if not self.transformer:
            state.extend(
                repeat(
                    np.zeros(self.vector_width),
                    self.max_zombies - len(self.zombie_list),
                )
            )

        return np.stack(state, axis=0)

    def step(self, action):
        # check if the particular agent is done
        if (
            self.terminations[self.agent_selection]
            or self.truncations[self.agent_selection]
        ):
            self._was_dead_step(action)
            return

        # agent_list : list of agent instance indexed by number
        # agent_name_mapping: dict of {str, idx} for agent index and name
        # agent_selection : str representing the agent name
        # agent: agent instance
        agent = self.agent_list[self.agent_name_mapping[self.agent_selection]]

        # cumulative rewards from previous iterations should be cleared
        self._cumulative_rewards[self.agent_selection] = 0
        agent.score = 0

        # this is... so whacky... but all actions here are index with 1 so... ok
        action = action + 1
        out_of_bounds = agent.update(action)

        # check for out of bounds death
        if self.line_death and out_of_bounds:
            agent.alive = False
            if agent in self.archer_list:
                self.archer_list.remove(agent)
            else:
                agent.weapons.empty()
                self.knight_list.remove(agent)
            self.kill_list.append(agent.agent_name)

        # actuate the weapon if necessary
        self.action_weapon(action, agent)

        # Do these things once per cycle
        if self._agent_selector.is_last():

            # Update the weapons
            self.update_weapons()

            # Zombie Kills the Sword
            self.sword_hit()

            # Zombie Kills the Arrow
            self.arrow_hit()

            # Zombie Kills the Archer
            if self.killable_archers:
                self.zombie_hit_archer()

            # Zombie Kills the Knight
            if self.killable_knights:
                self.zombit_hit_knight()

            # update some zombies
            for zombie in self.zombie_list:
                zombie.update()

            # Spawning Zombies at Random Location at every 100 iterations
            self.spawn_zombie()

            self.draw()

            self.check_game_end()
            self.frames += 1

        terminate = not self.run
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
        next_agent = self.agent_list[self.agent_name_mapping[self.agent_selection]]
        self.rewards[self.agent_selection] = next_agent.score

        self._accumulate_rewards()
        self._deads_step_first()

        if self.render_mode == "human":
            self.render()

    def enable_render(self):
        self.WINDOW = pygame.display.set_mode([const.SCREEN_WIDTH, const.SCREEN_HEIGHT])
        # self.WINDOW = pygame.Surface((const.SCREEN_WIDTH, const.SCREEN_HEIGHT))
        self.render_on = True
        self.draw()

    def draw(self):
        self.WINDOW.fill((66, 40, 53))
        self.WINDOW.blit(self.left_wall, self.left_wall.get_rect())
        self.WINDOW.blit(self.right_wall, self.right_wall_rect)
        self.WINDOW.blit(self.floor_patch1, (500, 500))
        self.WINDOW.blit(self.floor_patch2, (900, 30))
        self.WINDOW.blit(self.floor_patch3, (150, 430))
        self.WINDOW.blit(self.floor_patch4, (300, 50))
        self.WINDOW.blit(self.floor_patch1, (1000, 250))

        # draw all the sprites
        self.zombie_list.draw(self.WINDOW)
        for agent in self.agent_list:
            agent.weapons.draw(self.WINDOW)
        self.archer_list.draw(self.WINDOW)
        self.knight_list.draw(self.WINDOW)

    def render(self):
        if self.render_mode is None:
            gymnasium.logger.warn(
                "You are calling render method without specifying any render mode."
            )
            return

        if not self.render_on and self.render_mode == "human":
            # sets self.render_on to true and initializes display
            self.enable_render()

        observation = np.array(pygame.surfarray.pixels3d(self.WINDOW))
        if self.render_mode == "human":
            pygame.display.flip()
        return (
            np.transpose(observation, axes=(1, 0, 2))
            if self.render_mode == "rgb_array"
            else None
        )

    def close(self):
        if not self.closed:
            self.closed = True
            if self.render_on:
                # self.WINDOW = pygame.display.set_mode([const.SCREEN_WIDTH, const.SCREEN_HEIGHT])
                self.WINDOW = pygame.Surface((const.SCREEN_WIDTH, const.SCREEN_HEIGHT))
                self.render_on = False
                pygame.event.pump()
                pygame.display.quit()

    def check_game_end(self):
        # Zombie reaches the End of the Screen
        self.run = self.zombie_endscreen(self.run, self.zombie_list)

        # Zombie Kills all Players
        self.run = self.zombie_all_players(self.run, self.knight_list, self.archer_list)

    def reinit(self):
        # Dictionaries for holding new players and their weapons
        self.archer_dict = {}
        self.knight_dict = {}

        # Game Variables
        self.score = 0
        self.run = True
        self.zombie_spawn_rate = 0
        self.knight_player_num = self.archer_player_num = 0

        # Creating Sprite Groups
        self.zombie_list = pygame.sprite.Group()
        self.archer_list = pygame.sprite.Group()
        self.knight_list = pygame.sprite.Group()

        # agent_list is a list of instances
        # agents is s list of strings
        self.agent_list = []
        self.agents = []
        self.dead_agents = []

        for i in range(self.num_archers):
            name = "archer_" + str(i)
            self.archer_dict[f"archer{self.archer_player_num}"] = Archer(
                agent_name=name
            )
            self.archer_dict[f"archer{self.archer_player_num}"].offset(i * 50, 0)
            self.archer_list.add(self.archer_dict[f"archer{self.archer_player_num}"])
            self.agent_list.append(self.archer_dict[f"archer{self.archer_player_num}"])
            if i != self.num_archers - 1:
                self.archer_player_num += 1

        for i in range(self.num_knights):
            name = "knight_" + str(i)
            self.knight_dict[f"knight{self.knight_player_num}"] = Knight(
                agent_name=name
            )
            self.knight_dict[f"knight{self.knight_player_num}"].offset(i * 50, 0)
            self.knight_list.add(self.knight_dict[f"knight{self.knight_player_num}"])
            self.agent_list.append(self.knight_dict[f"knight{self.knight_player_num}"])
            if i != self.num_knights - 1:
                self.knight_player_num += 1

        self.agent_name_mapping = {}
        a_count = 0
        for i in range(self.num_archers):
            a_name = "archer_" + str(i)
            self.agents.append(a_name)
            self.agent_name_mapping[a_name] = a_count
            a_count += 1
        for i in range(self.num_knights):
            k_name = "knight_" + str(i)
            self.agents.append(k_name)
            self.agent_name_mapping[k_name] = a_count
            a_count += 1

        self.draw()
        self.frames = 0

    def reset(self, seed=None, return_info=False, options=None):
        if seed is not None:
            self.seed(seed=seed)
        self.has_reset = True
        self.agents = self.possible_agents
        self._agent_selector.reinit(self.agents)
        self.agent_selection = self._agent_selector.next()
        self.rewards = dict(zip(self.agents, [0 for _ in self.agents]))
        self._cumulative_rewards = {a: 0 for a in self.agents}
        self.terminations = dict(zip(self.agents, [False for _ in self.agents]))
        self.truncations = dict(zip(self.agents, [False for _ in self.agents]))
        self.infos = dict(zip(self.agents, [{} for _ in self.agents]))
        self.reinit()


# The original code for this game, that was added by J K Terry, was
# created by Dipam Patel in a different repository (hence the git history)

# Game art purchased from https://finalbossblues.itch.io/time-fantasy-monsters
# and https://finalbossblues.itch.io/icons
