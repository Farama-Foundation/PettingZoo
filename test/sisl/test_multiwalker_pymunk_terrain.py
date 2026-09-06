"""Parity tests for the Pymunk terrain generator.

The property under test is not "the terrain looks plausible" -- it is that the
generator consumes `np_random` in exactly the same order as the Box2D
implementation. Terrain is a pure function of that draw sequence, so if the order
differs, a given seed yields different ground and the port silently breaks
reproducibility.

The Box2D generator cannot be imported here without Box2D installed, so its draw
sequence is reproduced from the source (`multiwalker_base._generate_terrain`) by a
recording RNG wrapper: both generators run against the same seed and the recorded
call sequences must be identical. That check fails if the port reorders, adds or
drops a single draw.
"""

from __future__ import annotations

import numpy as np
import pytest

from pettingzoo.sisl.multiwalker.pymunk_terrain import (
    _STATES_,
    GRASS,
    TERRAIN_GRASS,
    TERRAIN_HEIGHT,
    TERRAIN_LENGTH,
    TERRAIN_STARTPAD,
    TERRAIN_STEP,
    generate_terrain,
)


class RecordingRandom:
    """Wraps a Generator and records every draw as (method, args)."""

    def __init__(self, seed):
        self._rng = np.random.default_rng(seed)
        self.calls = []

    def uniform(self, low, high):
        self.calls.append(("uniform", low, high))
        return self._rng.uniform(low, high)

    def integers(self, low, high):
        self.calls.append(("integers", low, high))
        return self._rng.integers(low, high)

    def random(self):
        self.calls.append(("random",))
        return self._rng.random()


def box2d_reference_terrain(np_random, hardcore, terrain_length=TERRAIN_LENGTH):
    """The Box2D state machine, transcribed with body creation removed.

    Kept deliberately close to the original so the draw sequence it records is
    the sequence the real environment produces. Only the CreateStaticBody calls
    are dropped; every branch and every RNG call is in its original position.
    """
    STUMP, STAIRS, PIT = 1, 2, 3
    state = GRASS
    velocity = 0.0
    y = TERRAIN_HEIGHT
    counter = TERRAIN_STARTPAD
    oneshot = False
    terrain_y = []
    original_y = y
    stair_height = stair_width = stair_steps = 0

    for i in range(terrain_length):
        if state == GRASS and not oneshot:
            velocity = 0.8 * velocity + 0.01 * np.sign(TERRAIN_HEIGHT - y)
            if i > TERRAIN_STARTPAD:
                velocity += np_random.uniform(-1, 1) / 30.0
            y += velocity
        elif state == PIT and oneshot:
            counter = np_random.integers(3, 5)
            counter += 2
            original_y = y
        elif state == PIT and not oneshot:
            y = original_y
            if counter > 1:
                y -= 4 * TERRAIN_STEP
        elif state == STUMP and oneshot:
            counter = np_random.integers(1, 3)
        elif state == STAIRS and oneshot:
            stair_height = +1 if np_random.random() > 0.5 else -1
            stair_width = np_random.integers(4, 5)
            stair_steps = np_random.integers(3, 5)
            original_y = y
            counter = stair_steps * stair_width
        elif state == STAIRS and not oneshot:
            s = stair_steps * stair_width - counter - stair_height
            n = s / stair_width
            y = original_y + (n * stair_height) * TERRAIN_STEP

        oneshot = False
        terrain_y.append(y)
        counter -= 1
        if counter == 0:
            counter = np_random.integers(TERRAIN_GRASS / 2, TERRAIN_GRASS)
            if state == GRASS and hardcore:
                state = np_random.integers(1, _STATES_)
                oneshot = True
            else:
                state = GRASS
                oneshot = True
    return terrain_y


@pytest.mark.parametrize("hardcore", [False, True])
@pytest.mark.parametrize("seed", [0, 1, 7, 42, 12345])
def test_rng_draw_sequence_matches_box2d(seed, hardcore):
    """The port must take the same draws, in the same order, as Box2D."""
    mine = RecordingRandom(seed)
    generate_terrain(mine, hardcore=hardcore)

    theirs = RecordingRandom(seed)
    box2d_reference_terrain(theirs, hardcore=hardcore)

    assert mine.calls == theirs.calls, (
        f"draw sequence diverged at index "
        f"{next((i for i, (a, b) in enumerate(zip(mine.calls, theirs.calls)) if a != b), min(len(mine.calls), len(theirs.calls)))}"
    )


@pytest.mark.parametrize("hardcore", [False, True])
@pytest.mark.parametrize("seed", [0, 1, 7, 42, 12345])
def test_terrain_heights_match_box2d(seed, hardcore):
    """Same draws in the same order must also produce the same ground."""
    got = generate_terrain(np.random.default_rng(seed), hardcore=hardcore)
    want = box2d_reference_terrain(np.random.default_rng(seed), hardcore)
    assert len(got.y) == len(want)
    np.testing.assert_allclose(got.y, want, rtol=0, atol=0)


def test_hardcore_actually_produces_obstacles():
    """A test that passes on flat ground would not guard anything."""
    flat = generate_terrain(np.random.default_rng(3), hardcore=False)
    rough = generate_terrain(np.random.default_rng(3), hardcore=True)
    assert flat.obstacles == []
    assert rough.obstacles, "hardcore terrain generated no obstacles"
    kinds = {kind for kind, _ in rough.obstacles}
    assert kinds <= {"pit", "stump", "stairs"}


def test_start_pad_is_level():
    """Walkers spawn on the start pad, so it must be flat regardless of seed."""
    for seed in (0, 5, 99):
        t = generate_terrain(np.random.default_rng(seed), hardcore=True)
        pad = t.y[: TERRAIN_STARTPAD + 1]
        assert max(pad) - min(pad) == pytest.approx(0.0, abs=1e-12), (
            f"seed {seed}: start pad varies by {max(pad) - min(pad)}"
        )


def test_terrain_is_deterministic_for_a_seed():
    a = generate_terrain(np.random.default_rng(11), hardcore=True)
    b = generate_terrain(np.random.default_rng(11), hardcore=True)
    np.testing.assert_array_equal(a.y, b.y)
    assert a.obstacles == b.obstacles


def test_different_seeds_give_different_terrain():
    a = generate_terrain(np.random.default_rng(1), hardcore=True)
    b = generate_terrain(np.random.default_rng(2), hardcore=True)
    assert not np.allclose(a.y, b.y), "two seeds produced identical terrain"


def test_geometry_is_finite_and_ordered():
    t = generate_terrain(np.random.default_rng(4), hardcore=True)
    assert np.all(np.isfinite(t.y))
    assert np.all(np.diff(t.x) > 0), "terrain x must increase monotonically"
    for kind, verts in t.obstacles:
        assert len(verts) == 4, f"{kind} obstacle is not a quad: {verts}"
        assert all(np.isfinite(c) for v in verts for c in v)


def test_attaches_to_a_pymunk_space():
    pymunk = pytest.importorskip("pymunk")
    space = pymunk.Space()
    space.gravity = (0.0, -10.0)
    t = generate_terrain(np.random.default_rng(8), hardcore=True)
    from pettingzoo.sisl.multiwalker.pymunk_terrain import add_terrain_to_space

    shapes = add_terrain_to_space(space, t)
    assert len(shapes) == len(t.edges) + len(t.obstacles)
    # Ground must actually stop a falling body rather than let it through.
    body = pymunk.Body(1.0, 10.0)
    body.position = (t.x[TERRAIN_STARTPAD // 2], TERRAIN_HEIGHT + 2.0)
    ball = pymunk.Circle(body, 0.15)
    ball.friction = 0.5
    space.add(body, ball)
    for _ in range(600):
        space.step(1 / 60.0)
    assert body.position.y > TERRAIN_HEIGHT - 1.0, (
        f"body fell through the terrain to y={body.position.y}"
    )
    assert np.isfinite(body.position.y)
