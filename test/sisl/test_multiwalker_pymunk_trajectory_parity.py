"""Fixed-action trajectory parity for the Pymunk Multiwalker port -- and its measured horizon.

WHAT THIS FILE SETTLES
----------------------
On Gymnasium#1597 I proposed comparing Box2D and Pymunk by driving both with identical scripted
action sequences and diffing the hull trajectories, on the grounds that this "separates physics
divergence from learning noise". The separation claim is right. The **long-horizon** version of the
plan is not achievable, and this file is where that was measured rather than assumed.

The walker under load is a falling, contact-rich system, i.e. chaotic. Measured on the port itself,
perturbing one motor command by **1e-6** and letting the rollout run:

| step | divergence from the unperturbed run |
| --- | --- |
| 1 | 1.8e-08 |
| 10 | 1.0e-06 |
| 51 | 1.0e-03 |
| 82 | **1.0e-01** |

A 1e-6 input reaches O(0.1) in 82 steps -- 1.64 s of simulated time at 50 Hz. Any difference
between two *different solvers* is far larger than 1e-6 on the first step. Therefore beyond roughly
that horizon a trajectory diff cannot distinguish "the port's physics is wrong" from "Box2D and
Chipmunk rounded differently once", and a long-horizon parity number would be a Lyapunov
measurement wearing a correctness label.

So the useful contract is narrow and stated explicitly:

* **Short horizon (<= ~30 steps): trajectory diffs are meaningful.** Divergence from a 1e-6
  perturbation is still ~1e-4 there, so a real mapping error stands out above the floor.
* **Long horizon: only statistical or invariant comparisons are valid** -- reward totals,
  termination behaviour, mass/inertia identities, learning curves over many seeds. Not step-by-step
  state.

WHAT THE TESTS BELOW ACTUALLY GUARD
-----------------------------------
The port is deterministic under a fixed seed (measured: bit-identical across repeated runs), so
these tests pin the port against *itself* and against deliberate perturbations. They do not assert
Box2D bit-parity, which is not available and never was.

Two traps this file is built around, both of which caught real mistakes while it was written:

1. **"Assert the walkers moved" is not a validity guard.** A zero-action rollout travels
   *further* than any scripted one here (max |dx| 1.32 vs 0.05 for `alternating`) because the
   walkers topple under gravity. Displacement measures gravity, not actuation.
2. **"Influence vs the passive baseline" does not measure actuation strength either.** An action of
   1e-6 yields influence 0.083 and an action of 1e-3 yields 1.97 -- larger than a full-scale
   script. That is chaos amplifying a tiny input, not the action doing work. Only the *short-horizon*
   window separates the two, which is why `SHORT_HORIZON` exists and why the influence guard runs
   inside it.
"""

import numpy as np
import pytest

pymunk = pytest.importorskip("pymunk")

from pettingzoo.sisl.multiwalker.pymunk_multiwalker import (  # noqa: E402
    PymunkMultiWalkerPrototype,
)

# Measured chaos budget (Box2D 2.3.8 / pymunk 7.3.0 / Python 3.12.14). A 1e-6 motor-command
# perturbation grows to these magnitudes, and this is what bounds any honest parity window.
CHAOS_FROM_1E6_PERTURBATION = {
    1: 1.8e-08,
    10: 1.0e-06,
    51: 1.0e-03,
    82: 1.0e-01,
}

# Inside this window a 1e-6 perturbation is still ~1e-4, so a genuine physics-mapping error is
# visible above the chaos floor. Beyond it, step-by-step comparison stops being informative.
SHORT_HORIZON = 30
LONG_HORIZON = 80

SEED = 7

# Deliberately asymmetric scripts; a symmetric one can cancel across the four motors.
SCRIPTS = {
    "hips_forward": lambda t: [0.8, 0.2, -0.6, 0.1],
    "knees_drive": lambda t: [0.1, 0.9, 0.15, -0.7],
    "alternating": lambda t: [0.7 * (1 if t % 20 < 10 else -1), 0.3, -0.5, 0.4],
    "ramp": lambda t: [min(1.0, t / 40.0), -0.3, 0.6, min(1.0, t / 60.0)],
}

PASSIVE = lambda t: [0.0, 0.0, 0.0, 0.0]  # noqa: E731


def _rollout(script, steps=LONG_HORIZON, seed=SEED, torque_scale=1.0):
    """Roll the port out under a fixed script; returns (steps, n_walkers, 3) of hull x/y/angle."""
    env = PymunkMultiWalkerPrototype(n_walkers=2, seed=seed)
    env.reset()
    traj = []
    for t in range(steps):
        action = np.array(
            [[c * torque_scale for c in script(t)] for _ in range(env.n_walkers)],
            dtype=np.float64,
        )
        env.step(action)
        traj.append(
            [[w.hull.position.x, w.hull.position.y, w.hull.angle] for w in env.walkers]
        )
    return np.asarray(traj)


def _max_diff(a, b):
    return float(np.abs(a - b).max())


@pytest.mark.parametrize("name", sorted(SCRIPTS))
def test_rollout_is_bit_reproducible_under_a_fixed_seed(name):
    """Precondition for everything else: identical inputs must give identical trajectories.

    If the port were nondeterministic, no parity number computed from it could be attributed to
    the physics mapping rather than to run-to-run jitter. Measured: exactly 0.0 difference.
    """
    assert _max_diff(_rollout(SCRIPTS[name]), _rollout(SCRIPTS[name])) == 0.0, (
        f"script {name!r} is not reproducible across identical runs, so every parity "
        "measurement built on it would be noise"
    )


@pytest.mark.parametrize("name", sorted(SCRIPTS))
def test_actions_drive_the_short_horizon_window(name):
    """Within the meaningful window, the scripted actions -- not gravity -- must dominate.

    Two earlier versions of this guard were wrong, both caught by measurement:
    asserting displacement fails because a zero-action rollout travels further (the walkers
    topple), and asserting influence over the LONG horizon fails because a 1e-6 action already
    yields influence 0.083 there. Restricting to the short horizon is what makes it mean
    something.
    """
    scripted = _rollout(SCRIPTS[name], steps=SHORT_HORIZON)
    passive = _rollout(PASSIVE, steps=SHORT_HORIZON)
    influence = _max_diff(scripted, passive)
    chaos_floor = CHAOS_FROM_1E6_PERTURBATION[10]
    assert influence > 100 * chaos_floor, (
        f"script {name!r} influences the first {SHORT_HORIZON} steps by only {influence:.2e}, "
        f"which is not clearly above the {chaos_floor:.1e} chaos floor"
    )


@pytest.mark.parametrize("name", sorted(SCRIPTS))
def test_a_halved_torque_is_detected_in_the_short_window(name):
    """Control arm: a real mapping error must be visible where the harness claims to look.

    Halving the commanded torque is the shape a wrong torque mapping takes. If this were only
    detectable at long horizon, the harness would be relying on chaos rather than on signal.
    """
    baseline = _rollout(SCRIPTS[name], steps=SHORT_HORIZON)
    halved = _rollout(SCRIPTS[name], steps=SHORT_HORIZON, torque_scale=0.5)
    distance = _max_diff(baseline, halved)
    assert distance > 1e-3, (
        f"halving the torque changed the first {SHORT_HORIZON} steps by only {distance:.2e} "
        f"under script {name!r}; this window cannot see a physics change"
    )


def test_chaos_horizon_is_still_what_was_measured():
    """Pin the chaos budget itself, because the whole contract of this file rests on it.

    If a future change alters the port's sensitivity, the documented "short horizon is
    meaningful, long horizon is not" reasoning stops holding and this test says so.
    """
    passive = _rollout(PASSIVE, steps=LONG_HORIZON)
    nudged = _rollout(lambda t: [1e-6, 0.0, 0.0, 0.0], steps=LONG_HORIZON)
    per_step = np.abs(passive - nudged).reshape(LONG_HORIZON, -1).max(axis=1)

    # Early on, a 1e-6 input must stay small -- that is what makes the short window usable.
    assert per_step[10] < 1e-4, (
        f"a 1e-6 perturbation already reached {per_step[10]:.2e} by step 10; the short-horizon "
        "window is no longer above the chaos floor and these comparisons need re-deriving"
    )
    # And it must genuinely blow up later -- that is what makes the long window unusable.
    assert per_step[-1] > 1e-3, (
        f"a 1e-6 perturbation only reached {per_step[-1]:.2e} by step {LONG_HORIZON}; the system "
        "is less chaotic than measured, so the long-horizon restriction may be too conservative"
    )


def test_divergence_is_locatable_in_time_not_just_in_aggregate():
    """The point of a step-by-step diff is *where* two runs part company.

    A single aggregate number cannot point at a joint or a contact event. This pins that the
    per-step signal exists and that a larger perturbation is detected no later than a smaller one.
    """
    script = SCRIPTS["alternating"]
    baseline = _rollout(script, steps=LONG_HORIZON)

    def first_exceeding(other, threshold=1e-3):
        per_step = np.abs(baseline - other).reshape(LONG_HORIZON, -1).max(axis=1)
        hits = np.nonzero(per_step > threshold)[0]
        return int(hits[0]) if len(hits) else None

    t_small = first_exceeding(_rollout(script, steps=LONG_HORIZON, torque_scale=0.95))
    t_large = first_exceeding(_rollout(script, steps=LONG_HORIZON, torque_scale=0.50))
    assert t_small is not None and t_large is not None, (
        f"no timestep crossed the threshold (5% change: {t_small}, 50% change: {t_large}); "
        "the per-step signal cannot locate a divergence"
    )
    assert t_large <= t_small, (
        f"a 50% torque change was first detected at step {t_large} but a 5% change at step "
        f"{t_small}; the per-step metric is not ordered by perturbation size"
    )
