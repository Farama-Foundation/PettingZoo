"""Reward-function parity with the Box2D reference.

Criterion 1 of the merge standard set out on Farama-Foundation/Gymnasium#1602
("same goal and reward functions") is the one criterion that can be settled
exactly rather than statistically, so it is worth pinning in a test instead of
leaving it to the learning-curve comparison to notice.

These tests drive the real ``PymunkMultiWalkerPrototype.step`` and force the
fallen/failed states directly, because a walker only falls after a specific
contact and waiting for one makes the test depend on solver dynamics rather
than on the reward algebra under test.

The clause being pinned is the per-walker branch in
``multiwalker_base.scroll_subroutine``::

    if fallen:
        rewards[i] += self.fall_reward
        if self.remove_on_fall:
            walker._destroy()
        if not self.terminate_on_fall:
            rewards[i] += self.terminate_reward   # per walker
        done[i] = True                            # per walker

An earlier revision of this prototype collapsed that into a single global
branch, which is off by ``terminate_reward`` (-100) for every fallen walker --
two orders of magnitude larger than a typical per-step shaping delta, and
therefore large enough to change what a policy learns rather than merely to
shift the returns.
"""

import numpy as np
import pytest

from pettingzoo.sisl.multiwalker.pymunk_multiwalker import (
    PymunkMultiWalkerPrototype,
)

NEUTRAL = np.zeros((3, 4), dtype=np.float64)


def _prototype(**kwargs):
    return PymunkMultiWalkerPrototype(seed=3, terrain_length=60, **kwargs)


def _step_with_fallen(prototype, fallen):
    """Step once with the fallen mask forced, returning (rewards, dones).

    ``_update_contacts`` recomputes the mask from the space, so it has to be
    overwritten after the step rather than before it.
    """
    original = prototype._update_contacts

    def patched():
        original()
        prototype.fallen_walkers = np.asarray(fallen, dtype=bool)

    prototype._update_contacts = patched
    _, rewards, dones = prototype.step(NEUTRAL)
    return rewards, dones


def test_a_single_fallen_walker_ends_alone():
    """terminate_on_fall=False: only the walker that fell is done."""
    prototype = _prototype(terminate_on_fall=False, shared_reward=False)
    _, dones = _step_with_fallen(prototype, [True, False, False])

    assert dones[0] and not dones[1] and not dones[2], (
        "a fallen walker must terminate on its own when terminate_on_fall is "
        f"False; got dones={dones}"
    )


def test_a_single_fallen_walker_is_charged_fall_plus_terminate_reward():
    """terminate_on_fall=False: the fall costs fall_reward AND terminate_reward.

    Kept separate from the ``dones`` assertion above on purpose. When both lived
    in one test the ``dones`` assert fired first and short-circuited this one, so
    a mutation run could not show whether the reward magnitude was actually
    pinned -- one failing test looked like coverage of both facts.
    """
    prototype = _prototype(terminate_on_fall=False, shared_reward=False)
    rewards, _ = _step_with_fallen(prototype, [True, False, False])

    # shared_reward=False makes local_ratio 1.0, so rewards are not averaged and
    # the per-walker penalty stays attributable to walker 0.
    penalty = rewards[0] - rewards[1]
    assert penalty == pytest.approx(
        prototype.fall_reward + prototype.terminate_reward, abs=1e-9
    ), (
        "walker 0 should be charged fall_reward + terminate_reward relative to "
        f"an upright walker; got {penalty}"
    )


def test_fall_penalty_alone_when_terminate_on_fall_ends_the_episode():
    """terminate_on_fall=True: everyone gets terminate_reward, once."""
    prototype = _prototype(terminate_on_fall=True, shared_reward=False)
    rewards, dones = _step_with_fallen(prototype, [True, False, False])

    assert dones.all(), f"terminate_on_fall=True must end every walker; got {dones}"
    penalty = rewards[0] - rewards[1]
    assert penalty == pytest.approx(prototype.fall_reward, abs=1e-9), (
        "with terminate_on_fall=True the global branch already charges "
        "terminate_reward to everyone, so the per-walker difference is just "
        f"fall_reward; got {penalty}"
    )


def test_terminate_reward_is_not_applied_twice_to_a_fallen_walker():
    """The per-walker and global branches must not both fire for one walker.

    This is the mutation the previous implementation could not fail: charging
    terminate_reward globally *and* per walker would double it, which no test
    that only checks "the reward went down" would catch.
    """
    prototype = _prototype(terminate_on_fall=True, shared_reward=False)
    rewards, _ = _step_with_fallen(prototype, [True, True, True])
    upright = _prototype(terminate_on_fall=True, shared_reward=False)
    baseline, _ = _step_with_fallen(upright, [False, False, False])

    delta = rewards - baseline
    expected = prototype.fall_reward + prototype.terminate_reward
    np.testing.assert_allclose(delta, np.full(3, expected), atol=1e-9)


def test_no_fall_and_no_failure_leaves_dones_all_false():
    """NEGATIVE CONTROL: the dones must be reachable as all-False.

    Without this, a bug that terminated unconditionally would still satisfy
    every assertion above.
    """
    prototype = _prototype(terminate_on_fall=False, shared_reward=False)
    rewards, dones = _step_with_fallen(prototype, [False, False, False])

    assert not dones.any(), f"nothing failed, so no walker should be done: {dones}"
    assert np.isfinite(rewards).all()


def test_package_falling_behind_the_origin_fails_every_walker():
    """The global failure branch still applies terminate_reward to everyone."""
    prototype = _prototype(terminate_on_fall=False, shared_reward=False)
    original = prototype._update_contacts

    def patched():
        original()
        prototype.package.position = (-1.0, prototype.package.position.y)

    prototype._update_contacts = patched
    _, rewards, dones = prototype.step(NEUTRAL)

    assert dones.all(), f"package behind the origin must end the episode: {dones}"
    assert (rewards <= prototype.terminate_reward).all(), (
        f"every walker should carry terminate_reward; got {rewards}"
    )
