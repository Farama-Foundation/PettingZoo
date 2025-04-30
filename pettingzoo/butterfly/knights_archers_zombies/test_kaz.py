"""Tests for Knights Archers Zombies."""

from __future__ import annotations

import itertools
from collections.abc import Sequence
from math import sqrt
from typing import cast

import numpy as np
import numpy.typing as npt
import pygame
import pytest

from pettingzoo.butterfly.knights_archers_zombies.knights_archers_zombies import (
    raw_env as KAZEnv,
)
from pettingzoo.butterfly.knights_archers_zombies.src import constants as const
from pettingzoo.butterfly.knights_archers_zombies.src.players import (
    Archer,
    Knight,
    Player,
    is_archer,
    is_knight,
)
from pettingzoo.butterfly.knights_archers_zombies.src.weapons import (
    Arrow,
    Sword,
    Weapon,
)
from pettingzoo.butterfly.knights_archers_zombies.src.zombie import Zombie


def test_kaz_obs_modes() -> None:
    """Test that obs modes are supported.

    If this is changed, the docs for the env should be updated to reflect modes.
    """
    methods = [  # (method_str, is_valid)
        ("image", True),
        ("vector", True),
        ("vector-masked", True),
        ("vector-sequence", True),
        ("random", False),
        ("", False),
        (2, False),
        (None, False),
    ]
    for method_str, is_valid in methods:
        if is_valid:
            # confirm we can create
            _ = KAZEnv(obs_method=method_str)  # type: ignore[arg-type]
        else:
            # confirm we get an error
            with pytest.raises(ValueError):
                _ = KAZEnv(obs_method=method_str)  # type: ignore[arg-type]


def test_kaz_image_state() -> None:
    """Confirm image state is a mapping of the screen"""
    env = KAZEnv(
        obs_method="image",
    )
    env.reset()
    image_state = env.state()

    assert env.screen is not None
    image: npt.NDArray[np.uint8] = pygame.surfarray.array3d(env.screen)
    height, width = const.SCREEN_HEIGHT, const.SCREEN_WIDTH
    expected_state = image[:width, :height, :]
    # no idea why these are done
    expected_state = np.rot90(np.fliplr(expected_state), k=3)
    assert np.all(image_state == expected_state)


def test_kaz_image_observation() -> None:
    """Confirm image state is a mapping of the screen"""
    env = KAZEnv(obs_method="image", num_archers=1, num_knights=0)
    env.reset()
    agent = env.agents[0]
    # move to upper left
    env.agent_map[agent].rect.topleft = (0, 0)
    env.draw()

    obs, _, _, _, _ = env.last()

    image: npt.NDArray[np.uint8] = pygame.surfarray.array3d(env.screen)
    image = np.swapaxes(image, 1, 0)
    expected_obs = np.zeros((512, 512, 3))
    expected_obs[256:, 256:, :] = image[:256, :256, :]

    assert np.all(obs == expected_obs)


def test_kaz_zombie_spawn() -> None:
    """Confirm zombies spawn as expected."""
    spawn_delay = 5
    max_zombies = 4

    env = KAZEnv(max_zombies=4, spawn_delay=5)
    assert len(env.zombie_list) == 0, "should start with zero zombies"

    for i in range(spawn_delay * 2 * max_zombies):
        n_zombies = len(env.zombie_list)
        env.do_zombie_turn()
        if i + 1 % spawn_delay == 0 and n_zombies < max_zombies:
            assert len(env.zombie_list) == n_zombies + 1, "zombie didn't spawn"
        assert len(env.zombie_list) <= max_zombies, "too many zombies"


# objects for vector obs tests. tuples are x,y,vx,vy  where vx,vy are directions
positions: dict[str, list[tuple[float, ...]]] = {
    "archers": [(50, 600, 0, -1), (100, 500, 1, 0)],
    "knights": [(250, 600, sqrt(2), sqrt(2)), (250, 500, -1, 0)],
    "zombies": [(100, 100, 0, 1)],
    "arrows": [(50, 500, 0, -1), (50, 450, 0, -1), (75, 400, 0, -1)],
    "swords": [(280, 600, 3 / sqrt(34), 5 / sqrt(34))],
}

# this is the expected vector output for 2 archers, 2 knights,
# 1 of 2 sowrds, 1 of 4 zombies, 3 of 5 arrows from positions mapping above
# it includes type masks
expected_vector_type_masked = np.array(
    [
        # current agent
        [0, 0, 0, 0, 0, 1, 0, 0.0390625, 0.83333333, 0, -1.0],
        # archers
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, -1.0],
        [0, 1, 0, 0, 0, 0, 0.10201961, 0.0390625, -0.1388888, 1, 0.0],
        # knights
        [0, 0, 1, 0, 0, 0, 0.11048543, 0.15625, 0, 1.41421356, 1.41421356],
        [0, 0, 1, 0, 0, 0, 0.14782453, 0.15625, -0.13888889, -1, 0.0],
        # swords
        [0, 0, 0, 1, 0, 0, 0.12705825, 0.1796875, 0, 0.51449576, 0.85749293],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        # arrows
        [0, 0, 0, 0, 1, 0, 0.09820928, 0, -0.13888889, 0, -1.0],
        [0, 0, 0, 0, 1, 0, 0.14731391, 0, -0.20833333, 0, -1.0],
        [0, 0, 0, 0, 1, 0, 0.19690348, 0.01953125, -0.27777778, 0, -1.0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        # zombies
        [1, 0, 0, 0, 0, 0, 0.49182261, 0.0390625, -0.69444444, 0, 1.0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ],
    dtype=np.float64,
)


def setup_sim(env: KAZEnv, objects: dict[str, list[tuple[int | float, ...]]]) -> None:
    """Set up the env with the given objects for vector obs tests.

    This puts all the objects in the specified locations with directions"""
    archer_0 = cast(Archer, env.agent_map["archer_0"])
    archer_1 = env.agent_map["archer_1"]
    knight_0 = cast(Knight, env.agent_map["knight_0"])
    knight_1 = env.agent_map["knight_1"]
    sword = Sword(knight_0)
    knight_0.weapons.add(sword)
    arrows: list[Arrow] = []
    for _ in range(3):
        arrows.append(Arrow(archer_0))
        archer_0.weapons.add(arrows[-1])
    zombie = Zombie(np.random.default_rng())
    env.zombie_list.add(zombie)
    agent_pos_list: list[tuple[Weapon | Player | Zombie, tuple[float, ...]]] = [
        (archer_0, objects["archers"][0]),
        (archer_1, objects["archers"][1]),
        (knight_0, objects["knights"][0]),
        (knight_1, objects["knights"][1]),
        (sword, objects["swords"][0]),
        (arrows[0], objects["arrows"][0]),
        (arrows[1], objects["arrows"][1]),
        (arrows[2], objects["arrows"][2]),
        (zombie, objects["zombies"][0]),
    ]
    for agent, pos in agent_pos_list:
        agent.rect.x = int(pos[0])
        agent.rect.y = int(pos[1])
        agent.direction = pygame.Vector2(pos[2], pos[3])


def test_kaz_vector_masked_obs() -> None:
    """Confirm that typemasked vector obs matches expected."""
    env = KAZEnv(max_zombies=4, max_arrows=5, obs_method="vector-masked")
    env.reset()
    setup_sim(env, positions)
    obs, _, _, _, _ = env.last()
    actual_obs = pytest.approx(obs)
    result = np.all(actual_obs == expected_vector_type_masked)
    assert result, "Vector masked obs is wrong"


def test_kaz_vector_sequence_obs() -> None:
    """Confirm that sequence vector obs matches expected."""
    env = KAZEnv(max_zombies=4, max_arrows=5, obs_method="vector-sequence")
    env.reset()
    setup_sim(env, positions)
    obs, _, _, _, _ = env.last()
    # sequence drops out the empty lines
    pruned_obs = expected_vector_type_masked[
        ~np.all(expected_vector_type_masked == 0, axis=1)
    ]
    actual_obs = pytest.approx(obs)
    result = np.all(actual_obs == pruned_obs)
    assert result, "Vector sequence obs is wrong"


def test_kaz_vector_obs() -> None:
    """Confirm that vector obs matches expected."""
    env = KAZEnv(max_zombies=4, max_arrows=5, obs_method="vector")
    env.reset()
    setup_sim(env, positions)
    obs, _, _, _, _ = env.last()
    # non-type masked doesn't have the first six columns
    pruned_obs = expected_vector_type_masked[:, 6:]
    actual_obs = pytest.approx(obs)
    result = np.all(actual_obs == pruned_obs)
    assert result, "Vector obs is wrong"


def test_kaz_agent_management() -> None:
    """Confirm agent handling work as expected."""
    env = KAZEnv(num_archers=2, num_knights=2)
    env.reset()
    expected_possible_agents = ["archer_0", "archer_1", "knight_0", "knight_1"]
    expected_agents = expected_possible_agents[:]
    assert sorted(expected_possible_agents) == sorted(
        env.possible_agents
    ), "Wrong possible agent list"
    assert sorted(expected_agents) == sorted(env.agents), "Wrong agent list"

    # four agents to move
    env.step(1)
    env.step(1)
    agent_to_kill = expected_agents.pop(1)
    env._remove_agent(env.agent_map[agent_to_kill])
    env.step(1)
    env.step(1)

    # should now be 3 agents
    n_agents = len(env._agent_selector.agent_order)
    assert n_agents == 3, "Agent not removed properly"
    assert env.dead_agents == [agent_to_kill], "dead_agents list is wrong"


obs_modes = ["vector", "image", "vector-masked", "vector-sequence"]
render_modes = [None, "rgb_array", "human"]

obs_test_combinations = list(itertools.product(obs_modes, render_modes))


def dummy_set_mode(
    size: tuple[float, float] | Sequence[float] | pygame.Vector2 = (1, 1),
    flags: int = 0,
    depth: int = 0,
    display: int = 0,
    vsync: int = 0,
) -> pygame.Surface:
    """Dummy function to prevent window from popping up"""
    return pygame.Surface(size)


@pytest.mark.parametrize("obs_method, render_mode", obs_test_combinations)
def test_kaz_obs_updates(obs_method: str, render_mode: str | None) -> None:
    """Confirm that obs updates after each agent acts.

    This is to ensure it complies with the intent of the AEC method.
    """
    if render_mode == "human":
        # prevent window from displaying
        pygame.display.set_mode = dummy_set_mode
        pygame.display.flip = lambda: None

    env = KAZEnv(
        num_archers=2, num_knights=2, obs_method=obs_method, render_mode=render_mode
    )
    env.reset()
    # cluster agents nearby so they can see each other
    for i, agent_name in enumerate(env.possible_agents):
        agent_obj = env.agent_map[agent_name]
        agent_obj.rect.x = i * 50
        agent_obj.rect.y = 600

    obs0, _, _, _, _ = env.last()
    obs0_alt, _, _, _, _ = env.last()

    # these should be the same because nothing has changed
    assert np.all(obs0 == obs0_alt), "kaz env observation is non-repeatable"

    prev_obs = obs0_alt

    # move every agent. Confirm the obs changes and doesn't match the original
    # the observation in each case must be different because the agent is in
    # a new position.
    for _ in env.agents:
        env.step(1)  # move the agent, so the obs is different
        obs, _, _, _, _ = env.last()
        assert not np.all(obs == prev_obs), "kaz obs not changing as expected"
        assert not np.all(obs != obs0), "kaz obs not changing as expected"
        prev_obs = obs


def test_kaz_killable_agents() -> None:
    """Confirm agents are or not killed based on options."""
    for is_archer_killable in [True, False]:
        for is_knight_killable in [True, False]:
            env = KAZEnv(
                num_archers=1,
                num_knights=1,
                killable_archers=is_archer_killable,
                killable_knights=is_knight_killable,
            )
            env.reset()
            # move agents, then zombies to overlap
            env.agent_map["archer_0"].rect.topleft = (50, 600)
            env.agent_map["knight_0"].rect.topleft = (100, 600)
            zombie1 = Zombie(np.random.default_rng())
            zombie1.rect.topleft = (60, 600)
            zombie2 = Zombie(np.random.default_rng())
            zombie2.rect.topleft = (110, 600)
            env.zombie_list.add(zombie1)
            env.zombie_list.add(zombie2)
            # check for overlaps
            env.do_zombie_turn()
            assert (
                "archer_0" in env.kill_list
            ) == is_archer_killable, "archer death status is wrong"
            assert (
                "knight_0" in env.kill_list
            ) == is_knight_killable, "knight death status is wrong"


def test_kaz_zombie_motion() -> None:
    """Confirm zombie moves as expected."""
    expected_path = [
        (200, 55),
        (200, 60),
        (230, 65),
        (230, 70),
        (230, 75),
        (200, 80),
        (200, 85),
        (200, 90),
        (230, 95),
        (230, 100),
    ]
    env = KAZEnv(num_archers=1, num_knights=1)
    env.reset()
    zombie = Zombie(np.random.default_rng(23))
    env.zombie_list.add(zombie)
    zombie.rect.topleft = (200, 50)
    idx = 0
    while zombie.rect.y < 100:
        env.do_zombie_turn()
        assert zombie.rect.topleft == expected_path[idx], "wrong zombie movement"
        idx += 1


def test_kaz_scores() -> None:
    """Confirm scoring happens as expected."""
    env = KAZEnv(num_archers=1, num_knights=1)
    env.reset()
    zombies: list[Zombie] = []
    for _ in range(4):
        zombie = Zombie(np.random.default_rng())
        env.zombie_list.add(zombie)
        zombies.append(zombie)

    knight_0 = env.agent_map["knight_0"]
    archer_0 = env.agent_map["archer_0"]
    # should have no score to start
    assert archer_0.score == 0, "archer has unexpected score"
    assert knight_0.score == 0, "knight has unexpected score"

    sword = Sword(cast(Knight, knight_0))
    knight_0.weapons.add(sword)
    zombies[0].rect.topleft = (100, 200)
    # move knight in position to hit zombie (sword moves with knight)
    knight_0.rect.topleft = (80, 250)

    arrow_0 = Arrow(cast(Archer, archer_0))
    arrow_1 = Arrow(cast(Archer, archer_0))
    archer_0.weapons.add(arrow_0)
    archer_0.weapons.add(arrow_1)
    zombies[1].rect.topleft = (200, 200)
    # move arrow to hit (offset in y by ARROW_SPEED so it will move into position)
    arrow_0.rect.topleft = (220, 220 + const.ARROW_SPEED)
    # hit two zombies with one arrow
    zombies[2].rect.topleft = (400, 200)
    zombies[3].rect.topleft = (zombies[2].rect.x + zombies[2].rect.width, 200)
    # put arow in between zombies, to hit both
    arrow_1.rect.topleft = (zombies[3].rect.x - 10, 180 + const.ARROW_SPEED)

    env.apply_weapons()
    assert knight_0.score == 1, "knight did not score as expected"
    assert archer_0.score == 3, "archer did not score as expected"


def test_kaz_weapons() -> None:
    """Test that weapons behave correctly."""
    max_arrows = 5
    env = KAZEnv(num_archers=1, num_knights=1, max_arrows=max_arrows)
    env.reset()
    knight_0 = env.agent_map["knight_0"]
    archer_0 = env.agent_map["archer_0"]

    assert env.num_active_arrows == 0, "bad arrow count"
    assert env.num_active_swords == 0, "bad sword count"

    knight_0.attack()
    assert env.num_active_swords == 1, "sword did not appear as expected"
    # attacking again should raise an error
    with pytest.raises(RuntimeError):
        knight_0.attack()
    assert env.num_active_swords == 1, "bad sword count"
    # the sword should last several steps...
    n_steps = (const.MAX_ARC - const.MIN_ARC) // const.SWORD_SPEED
    for _ in range(n_steps):
        env.apply_weapons()
        assert env.num_active_swords == 1, "sword left early"
    # ... and go away on the next step
    env.apply_weapons()
    assert env.num_active_swords == 0, "sword didn't disappear as expected"

    archer_0.attack()
    assert env.num_active_arrows == 1, "arrow did not appear as expected"
    # attacking again should raise an error
    with pytest.raises(RuntimeError):
        archer_0.attack()
    assert env.num_active_arrows == 1, "bad arrow count"

    # confirm archer is timed out on attack
    for _ in range(const.ARROW_TIMEOUT - 1):
        # if we try to attack directly, it will fail
        with pytest.raises(RuntimeError):
            archer_0.attack()
        # no new arrow
        assert env.num_active_arrows == 1, "unexpected arrow appeared"

        # if we try to attack via step, it should not work
        env.agent_selection = "archer_0"
        env.step(const.Actions.ACTION_ATTACK.value)
        assert env.num_active_arrows == 1, "unexpected arrow appeared"

    # now that the timeout is over, we should get a new arrow when attacking
    env.agent_selection = "archer_0"
    env.step(const.Actions.ACTION_ATTACK.value)
    assert env.num_active_arrows == 2, "arrow didn't appear as expected"

    # reset the timeout and fire arrows to the max
    n_arrows = 2
    while n_arrows < max_arrows:
        n_arrows += 1
        archer_0.timeout = None
        env.agent_selection = "archer_0"
        env.step(const.Actions.ACTION_ATTACK.value)
        assert env.num_active_arrows == n_arrows, "arrow didn't appear as expected"

    # we are at the max number of arrows
    assert env.num_active_arrows == max_arrows, "wrong number of arrows"
    # trying to fire another, even without timeout, will not work
    archer_0.timeout = None
    env.agent_selection = "archer_0"
    env.step(const.Actions.ACTION_ATTACK.value)
    assert env.num_active_arrows == max_arrows, "more than max arrows exist"

    # confirm that an arrow that goes out of bounds is removed
    arrow = archer_0.weapons.sprites()[0]
    arrow.rect.x = -100  # out of bounds
    # this should remove the out of bounds arrow
    env.apply_weapons()
    assert env.num_active_arrows == max_arrows - 1, "arrows did not disappear"


def test_kaz_is_archer_is_knight() -> None:
    """Confirm that is_archer and is_knight work."""
    player = Player("name", "archer.png")
    archer = Archer("name")
    knight = Knight("name")
    for obj in [player, archer, knight]:
        assert is_archer(obj) == (obj == archer), "is_archer returned wrong result"
        assert is_knight(obj) == (obj == knight), "is_knight returned wrong result"


def test_kaz_player_directions() -> None:
    """Confirm that player directions are always normalized."""
    env = KAZEnv(num_archers=1, num_knights=1)
    env.reset()
    knight = env.agent_map["knight_0"]
    approx_one = pytest.approx(1.0)
    assert knight.direction.magnitude() == approx_one, (
        "Direction is not a unit vector" ""
    )
    # move around a bit
    knight.act(const.Actions.ACTION_FORWARD)
    knight.act(const.Actions.ACTION_FORWARD)
    knight.act(const.Actions.ACTION_FORWARD)
    assert knight.direction.magnitude() == approx_one, (
        "Direction is not a unit vector" ""
    )
    # confirm turns give normalized directions
    for _ in range(4):
        knight.act(const.Actions.ACTION_TURN_CCW)
        assert knight.direction.magnitude() == approx_one, (
            "Direction is not a unit vector" ""
        )
    knight.act(const.Actions.ACTION_FORWARD)
    knight.act(const.Actions.ACTION_FORWARD)
    for _ in range(12):
        knight.act(const.Actions.ACTION_TURN_CW)
        assert knight.direction.magnitude() == approx_one, (
            "Direction is not a unit vector" ""
        )
