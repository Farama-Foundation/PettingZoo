import numpy as np
import pytest

from pettingzoo.sisl.multiwalker.pymunk_multiwalker import (
    MOTORS_TORQUE,
    SPEED_HIP,
    SPEED_KNEE,
    TERRAIN_HEIGHT,
    PymunkMultiWalkerPrototype,
)


def test_seeded_reset_is_reproducible_and_finite():
    first = PymunkMultiWalkerPrototype(seed=11, terrain_length=60)
    second = PymunkMultiWalkerPrototype(seed=11, terrain_length=60)

    np.testing.assert_allclose(first.observations(), second.observations())
    assert first.observations().shape == (3, 31)
    assert first.state().shape == (75,)
    assert np.isfinite(first.observations()).all()


def test_density_derived_mass_properties_match_box2d_reference():
    prototype = PymunkMultiWalkerPrototype(seed=1, terrain_length=60)
    walker = prototype.walkers[0]

    assert walker.hull.mass == pytest.approx(5.422223, rel=1e-6)
    assert walker.legs[0].mass == pytest.approx(0.302222, rel=1e-6)
    assert walker.legs[1].mass == pytest.approx(0.241778, rel=1e-6)

    center_of_gravity = walker.hull.center_of_gravity
    center_offset_sq = center_of_gravity.x**2 + center_of_gravity.y**2
    inertia_about_body_origin = walker.hull.moment + walker.hull.mass * center_offset_sq
    assert inertia_about_body_origin == pytest.approx(2.001745, rel=1e-6)


def test_step_configures_all_four_motors_and_returns_parallel_state():
    prototype = PymunkMultiWalkerPrototype(seed=5, terrain_length=60)
    actions = np.tile(np.array([1.0, -0.5, -1.0, 0.25]), (3, 1))

    observations, rewards, dones = prototype.step(actions)

    first_walker = prototype.walkers[0]
    assert [joint.motor.rate for joint in first_walker.joints] == [
        SPEED_HIP,
        -SPEED_KNEE,
        -SPEED_HIP,
        SPEED_KNEE,
    ]
    assert [joint.motor.max_force for joint in first_walker.joints] == pytest.approx(
        [MOTORS_TORQUE, MOTORS_TORQUE * 0.5, MOTORS_TORQUE, MOTORS_TORQUE * 0.25]
    )
    assert observations.shape == (3, 31)
    assert rewards.shape == (3,)
    assert dones.shape == (3,)
    assert np.isfinite(observations).all()
    assert np.isfinite(rewards).all()
    assert np.max(np.abs(rewards)) < 1.0


def test_package_terrain_contact_sets_failure_state():
    prototype = PymunkMultiWalkerPrototype(seed=3, terrain_length=60)
    prototype.package.position = (prototype.package.position.x, TERRAIN_HEIGHT)
    prototype.space.reindex_shapes_for_body(prototype.package)

    prototype._update_contacts()
    _, rewards, dones = prototype.step(np.zeros((3, 4)))

    assert prototype.game_over
    assert dones.all()
    assert (rewards < 0).all()


def test_step_rejects_non_parallel_action_shape():
    prototype = PymunkMultiWalkerPrototype(seed=2, terrain_length=60)

    with pytest.raises(ValueError, match="expected actions with shape"):
        prototype.step(np.zeros(4))
