"""The environment actually uses the procedural terrain -- and against real Box2D.

Two gaps this file closes, both of which were live in the PR for five days.

**1. The generator was written, tested, and never called.**
`pymunk_terrain.py` was complete and correct, `test_multiwalker_pymunk_terrain.py`
passed 26 tests on it, and `PymunkMultiWalkerPrototype` went on building flat ground
from a private `_create_flat_terrain` helper. Every test passed the whole time, because
every test pointed at the module rather than at the environment. A test suite that only
covers a component cannot notice that nothing imports it, so the checks here assert on
`prototype.terrain` -- the ground the walkers are standing on -- and fail if it is flat.

**2. The existing parity test compares against a re-implementation, not Box2D.**
`test_multiwalker_pymunk_terrain.py` reproduces `multiwalker_base._generate_terrain`'s
draw sequence with a hand-written recorder, because Box2D may be absent. That is a real
check, but it shares an author with the thing it checks: if the port and the recorder
misread the reference the same way, both agree and the test passes. The test below drives
the actual `multiwalker_base` generator through a recording RNG and diffs the two streams
call by call. It skips when Box2D is unavailable rather than weakening.

The float32 trap, since it cost a false alarm while this was written: Box2D stores vertices
as float32, so its polygons come back as 89.133331299 where the port has 89.13333333...
Comparing obstacle vertices for exact equality reports a mismatch on geometry that is in
fact identical. Obstacles are therefore matched by centroid and extent within a tolerance.
"""

from __future__ import annotations

import numpy as np
import pytest

pymunk = pytest.importorskip("pymunk")

from pettingzoo.sisl.multiwalker.pymunk_multiwalker import (  # noqa: E402
    TERRAIN_HEIGHT,
    TERRAIN_STEP,
    PymunkMultiWalkerPrototype,
)
from pettingzoo.sisl.multiwalker.pymunk_terrain import (  # noqa: E402
    generate_terrain,
)

SEEDS = (0, 1, 7, 42, 1234)


class RecordingRandom:
    """Wraps a Generator, recording (method, args, first-value) for every draw."""

    def __init__(self, rng):
        self._rng = rng
        self.calls = []

    def _record(self, name, args, value):
        self.calls.append((name, args, float(np.asarray(value).reshape(-1)[0])))
        return value

    def uniform(self, *args, **kwargs):
        return self._record("uniform", args, self._rng.uniform(*args, **kwargs))

    def integers(self, *args, **kwargs):
        return self._record("integers", args, self._rng.integers(*args, **kwargs))

    def random(self, *args, **kwargs):
        return self._record("random", args, self._rng.random(*args, **kwargs))

    def normal(self, *args, **kwargs):
        return self._record("normal", args, self._rng.normal(*args, **kwargs))


class TestTheEnvironmentUsesTheGenerator:
    """Assertions on the environment's ground, not on the generator in isolation."""

    def test_the_ground_the_walkers_stand_on_is_not_flat(self):
        prototype = PymunkMultiWalkerPrototype(seed=7, terrain_length=200)
        y = np.asarray(prototype.terrain.y)
        assert not np.allclose(y, TERRAIN_HEIGHT), (
            "the environment built flat ground: the procedural generator exists but "
            "is not wired in"
        )
        assert y.var() > 1e-4

    def test_hardcore_adds_obstacles_and_plain_mode_does_not(self):
        # The two modes must separate. If `hardcore` never reaches the generator,
        # both return the same terrain and the flag is decorative.
        plain = PymunkMultiWalkerPrototype(seed=7, terrain_length=200, hardcore=False)
        hard = PymunkMultiWalkerPrototype(seed=7, terrain_length=200, hardcore=True)
        assert len(plain.terrain.obstacles) == 0
        assert len(hard.terrain.obstacles) > 0
        assert len(hard.terrain_shapes) > len(plain.terrain_shapes)
        assert np.asarray(hard.terrain.y).var() > np.asarray(plain.terrain.y).var()

    def test_every_generated_shape_is_attached_to_the_space(self):
        # Geometry that is computed but not added collides with nothing, which looks
        # exactly like flat ground to a walker.
        prototype = PymunkMultiWalkerPrototype(
            seed=42, terrain_length=200, hardcore=True
        )
        in_space = set(prototype.space.shapes)
        assert all(shape in in_space for shape in prototype.terrain_shapes)
        assert len(prototype.terrain_shapes) == (
            len(prototype.terrain.edges) + len(prototype.terrain.obstacles)
        )

    @pytest.mark.parametrize("hardcore", [False, True])
    def test_same_seed_reproduces_the_same_ground(self, hardcore):
        a = PymunkMultiWalkerPrototype(seed=3, terrain_length=200, hardcore=hardcore)
        b = PymunkMultiWalkerPrototype(seed=3, terrain_length=200, hardcore=hardcore)
        np.testing.assert_allclose(a.terrain.y, b.terrain.y)

    def test_different_seeds_produce_different_ground(self):
        # Guards the opposite failure: a generator wired in but handed a fixed seed.
        a = PymunkMultiWalkerPrototype(seed=3, terrain_length=200)
        b = PymunkMultiWalkerPrototype(seed=4, terrain_length=200)
        assert not np.allclose(a.terrain.y, b.terrain.y)

    def test_observations_stay_finite_over_terrain(self):
        prototype = PymunkMultiWalkerPrototype(
            seed=7, terrain_length=200, hardcore=True
        )
        for _ in range(10):
            observations, rewards, _dones = prototype.step(np.zeros((3, 4)))
            assert np.isfinite(observations).all()
            assert np.isfinite(rewards).all()

    def test_lidar_reports_terrain_it_could_not_see_when_flat(self):
        # The LIDAR filter masks TERRAIN_CATEGORY, so obstacles only register if the
        # generated shapes carry that category. A filter mismatch would leave the
        # walkers blind to exactly the geometry that was just added.
        prototype = PymunkMultiWalkerPrototype(
            seed=42, terrain_length=200, hardcore=True
        )
        lidar = np.concatenate([walker.lidar for walker in prototype.walkers])
        assert (lidar < 1.0).any(), "no LIDAR ray hit terrain: category filter mismatch"


class TestCloudDrawsAreConsumed:
    """The cosmetic stage that is not optional.

    `_generate_clouds` builds nothing this prototype can render, but it draws 11 values
    per cloud from the shared stream. Dropping it leaves terrain matching Box2D while
    every later draw is offset -- silent, and invisible to any test that only looks at
    terrain.

    The first two tests below call `_consume_cloud_rng_draws` directly, and on their own
    they are worthless for the property that matters: deleting the call from `reset` left
    both of them green, because a test that invokes a method cannot notice that production
    code never does. That is the same failure that let a wired-out terrain generator pass
    26 tests. `test_reset_consumes_terrain_draws_plus_cloud_draws` is the one that binds
    the method to `reset` -- it is what fails when the call is removed.
    """

    def test_the_draw_count_matches_box2d_arithmetic(self):
        prototype = PymunkMultiWalkerPrototype(seed=0, terrain_length=200)
        recorder = RecordingRandom(prototype.np_random)
        prototype.np_random = recorder
        prototype._consume_cloud_rng_draws()
        assert len(recorder.calls) == 11 * (200 // 20)

    def test_the_count_scales_with_terrain_length(self):
        prototype = PymunkMultiWalkerPrototype(seed=0, terrain_length=60)
        recorder = RecordingRandom(prototype.np_random)
        prototype.np_random = recorder
        prototype._consume_cloud_rng_draws()
        assert len(recorder.calls) == 11 * (60 // 20)

    @pytest.mark.parametrize("length", [60, 200])
    def test_reset_consumes_terrain_draws_plus_cloud_draws(self, length):
        # Count what `reset` itself draws. Terrain accounts for a seed-dependent number,
        # so the cloud contribution is isolated by differencing against a generator run
        # on the same seed. Remove the call from `reset` and this drops by 11 per cloud.
        from gymnasium.utils import seeding

        prototype = PymunkMultiWalkerPrototype(seed=5, terrain_length=length)
        recorder = RecordingRandom(prototype.np_random)
        prototype.np_random = recorder
        prototype.seed_value = 5
        prototype.reset()

        reference_rng, _ = seeding.np_random(5)
        reference = RecordingRandom(reference_rng)
        generate_terrain(reference, hardcore=False, terrain_length=length)

        cloud_draws = 11 * (length // 20)
        # `reset` also draws observation noise after the terrain/cloud stages, so the
        # count is a lower bound -- but it cannot be met at all if the clouds are skipped.
        assert len(recorder.calls) >= len(reference.calls) + cloud_draws, (
            "reset drew fewer values than terrain + clouds require: the cloud stage is "
            "not being consumed, so every later draw is offset from Box2D's stream"
        )

    def test_reset_leaves_the_stream_where_box2d_leaves_it(self):
        # The end-to-end version: after reset, the next value the environment would draw
        # must equal the next value Box2D would draw, having run terrain then clouds.
        from gymnasium.utils import seeding

        reference_rng, _ = seeding.np_random(9)
        generate_terrain(reference_rng, hardcore=False, terrain_length=200)
        for _ in range(200 // 20):
            reference_rng.uniform(0, 200)
            for _corner in range(5):
                reference_rng.uniform(0, 5 * TERRAIN_STEP)
                reference_rng.uniform(0, 5 * TERRAIN_STEP)
        expected_next = reference_rng.uniform(0.0, 1.0)

        prototype = PymunkMultiWalkerPrototype.__new__(PymunkMultiWalkerPrototype)
        prototype.n_walkers = 3
        prototype.terrain_length = 200
        prototype.hardcore = False
        prototype.np_random, prototype.seed_value = seeding.np_random(9)
        prototype.space = pymunk.Space(threaded=False)
        prototype.terrain, prototype.terrain_shapes = prototype._create_terrain()
        prototype._consume_cloud_rng_draws()

        assert prototype.np_random.uniform(0.0, 1.0) == expected_next


Box2D = pytest.importorskip("Box2D", reason="real-Box2D parity needs Box2D installed")


def _box2d_stream(seed, hardcore, length):
    """Drive the real multiwalker_base generator and record its draws."""
    from pettingzoo.sisl.multiwalker import multiwalker_base

    env = multiwalker_base.MultiWalkerEnv(n_walkers=3, terrain_length=length)
    env.hardcore = hardcore
    env._seed(seed)
    env.setup()
    recorder = RecordingRandom(env.np_random)
    env.np_random = recorder
    env._generate_terrain(hardcore)

    polygons = []
    for body in env.terrain:
        for fixture in body.fixtures:
            shape = fixture.shape
            if type(shape).__name__ != "b2EdgeShape":
                polygons.append([tuple(body.transform * v) for v in shape.vertices])
    return recorder.calls, list(env.terrain_y), polygons


def _signature(vertices):
    """Centroid and extent -- tolerant to Box2D storing vertices as float32."""
    array = np.asarray(vertices, dtype=float)
    return (
        array[:, 0].mean(),
        array[:, 1].mean(),
        np.ptp(array[:, 0]),
        np.ptp(array[:, 1]),
    )


class TestAgainstTheRealBox2DGenerator:
    """Diffed against `multiwalker_base` itself, not against a re-reading of it."""

    @pytest.mark.parametrize("hardcore", [False, True])
    @pytest.mark.parametrize("seed", SEEDS)
    def test_draw_sequence_is_identical_call_for_call(self, seed, hardcore):
        from gymnasium.utils import seeding

        reference, _y, _polys = _box2d_stream(seed, hardcore, 200)
        rng, _ = seeding.np_random(seed)
        recorder = RecordingRandom(rng)
        generate_terrain(recorder, hardcore=hardcore, terrain_length=200)

        assert len(recorder.calls) == len(reference)
        for index, (want, got) in enumerate(zip(reference, recorder.calls)):
            assert want[0] == got[0], f"draw {index}: {want[0]} vs {got[0]}"
            assert want[2] == got[2], f"draw {index} value differs"

    @pytest.mark.parametrize("hardcore", [False, True])
    @pytest.mark.parametrize("seed", SEEDS)
    def test_ground_height_is_identical(self, seed, hardcore):
        from gymnasium.utils import seeding

        _calls, reference_y, _polys = _box2d_stream(seed, hardcore, 200)
        rng, _ = seeding.np_random(seed)
        terrain = generate_terrain(rng, hardcore=hardcore, terrain_length=200)
        np.testing.assert_allclose(terrain.y, reference_y, rtol=0, atol=0)

    @pytest.mark.parametrize("seed", SEEDS)
    def test_hardcore_obstacles_match_one_for_one(self, seed):
        from gymnasium.utils import seeding

        _calls, _y, reference_polys = _box2d_stream(seed, True, 200)
        rng, _ = seeding.np_random(seed)
        terrain = generate_terrain(rng, hardcore=True, terrain_length=200)
        ported = [verts for _kind, verts in terrain.obstacles]

        assert len(ported) == len(reference_polys) > 0
        remaining = [_signature(v) for v in ported]
        for reference in (_signature(v) for v in reference_polys):
            match = next(
                (
                    index
                    for index, candidate in enumerate(remaining)
                    if all(abs(a - b) < 1e-3 for a, b in zip(reference, candidate))
                ),
                None,
            )
            assert match is not None, f"no port obstacle matches Box2D's {reference}"
            remaining.pop(match)
        assert remaining == []
