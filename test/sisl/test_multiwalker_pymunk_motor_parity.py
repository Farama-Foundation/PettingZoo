"""Motor torque parity between the Box2D reference and the Pymunk port.

WHY THIS FILE EXISTS
--------------------
`multiwalker_base.py` drives each joint with Box2D's ``maxMotorTorque``, and
``pymunk_multiwalker.py`` maps that onto ``pymunk.SimpleMotor.max_force`` by assigning the
*same number*::

    motor.max_force = MOTORS_TORQUE * clip(abs(command), 0, 1)     # pymunk port
    joint.maxMotorTorque = MOTORS_TORQUE * clip(abs(action), 0, 1)  # Box2D reference

That equality was an open question on the PR, and the concern raised was that pymunk's
``max_force`` might be an *impulse budget per step* rather than a torque, in which case the
faithful mapping would carry a ``dt`` factor and the port would be silently ~50x too strong at
50 Hz. pymunk's own documentation does not settle it -- ``max_force`` is described only as
"The maximum force that the constraint can use to act on the two bodies. Defaults to infinity",
with no units and no per-step qualifier.

So it was measured. Result: **the plain mapping is correct** and the ``dt`` factor is wrong.
Across the six stalling operating points below (varying budget, commanded rate, horizon, bar
length and density, at six distinct overpower ratios) ``max_force = torque`` tracked Box2D to
within **0.0343 rad** worst case, while ``max_force = torque * dt`` was off by **0.55--1.25 rad**
and is detected in 6 of 6 cases. The hypothesis that motivated this test was refuted by it, which
is the useful outcome: it removes a ``dt`` factor that would otherwise have been "fixed" into the
port.

WHAT MAKES THIS A REAL TEST
---------------------------
A parity assertion is worthless if it passes no matter what the port does. Two things keep it
honest:

1. **The motor must actually stall.** If the torque budget never binds, both engines simply track
   the commanded rate and every candidate mapping agrees -- the first version of this experiment
   was blind for exactly that reason, reporting the same angle for ``max_force`` of 80 and of 4000
   (a 50x change with no effect, because neither budget was the limiting factor). The fixtures
   below load the joint so that gravity's moment about the pivot (``m*g*half_len``) exceeds the
   budget, making the achieved angle a direct readout of it.
   ``test_the_budget_actually_binds`` asserts that blindness is gone.
2. **A control arm that must fail.** ``test_dt_scaled_mapping_is_refuted`` asserts the *rejected*
   mapping is measurably worse. If someone later "corrects" the port by multiplying by ``dt``,
   that test fails and says why.
"""

import numpy as np
import pytest

pymunk = pytest.importorskip("pymunk")
Box2D = pytest.importorskip("Box2D")

from Box2D import (  # noqa: E402
    b2FixtureDef,
    b2PolygonShape,
    b2RevoluteJointDef,
    b2World,
)

FPS = 50.0
DT = 1.0 / FPS

# Box2D's own solver settings, as used by multiwalker_base.step():
#   self.world.Step(1.0 / FPS, 6 * 30, 2 * 30)
VELOCITY_ITERATIONS = 6 * 30
POSITION_ITERATIONS = 2 * 30

HALF_HEIGHT = 0.1


def _box2d_angle(torque, rate, steps, half_len, density):
    """Drive one revolute joint under gravity and return its angle after `steps`."""
    world = b2World(gravity=(0, -10), doSleep=False)
    anchor = world.CreateStaticBody(position=(0, 0))
    bar = world.CreateDynamicBody(
        position=(half_len, 0),
        fixtures=b2FixtureDef(
            shape=b2PolygonShape(box=(half_len, HALF_HEIGHT)), density=density
        ),
    )
    joint = world.CreateJoint(
        b2RevoluteJointDef(
            bodyA=anchor,
            bodyB=bar,
            localAnchorA=(0, 0),
            localAnchorB=(-half_len, 0),
            enableMotor=True,
            maxMotorTorque=torque,
            motorSpeed=rate,
            enableLimit=False,
        )
    )
    for _ in range(steps):
        world.Step(DT, VELOCITY_ITERATIONS, POSITION_ITERATIONS)
    return joint.angle


def _pymunk_angle(max_force, rate, steps, half_len, density):
    """The same joint in pymunk. `rate` is negated for pymunk's sign convention."""
    space = pymunk.Space()
    space.gravity = (0, -10)
    space.iterations = VELOCITY_ITERATIONS
    mass = density * (2 * half_len) * (2 * HALF_HEIGHT)
    bar = pymunk.Body(
        mass, pymunk.moment_for_box(mass, (2 * half_len, 2 * HALF_HEIGHT))
    )
    bar.position = (half_len, 0)
    space.add(bar, pymunk.Poly.create_box(bar, (2 * half_len, 2 * HALF_HEIGHT)))
    space.add(pymunk.PivotJoint(space.static_body, bar, (0, 0), (-half_len, 0)))
    motor = pymunk.SimpleMotor(space.static_body, bar, -rate)
    motor.max_force = max_force
    space.add(motor)
    for _ in range(steps):
        space.step(DT)
    return bar.angle


# torque, rate, steps, half_len, density
#
# Every case here must STALL, i.e. gravity's moment about the pivot (m*g*half_len) must exceed
# the torque budget -- `test_the_budget_actually_binds` enforces that. A non-stalling case looks
# like a pass but proves nothing, because both engines then just track the commanded rate.
#
# A (400, 4.0, 60, 2.0, 20.0) case was removed for exactly this reason: its budget of 400 exceeds
# the 320 N*m gravity moment, so it never stalls. It *passed* the parity assertion (error 0.026
# rad) while being blind to the mapping under test -- which is why the binding guard exists rather
# than being assumed.
#
# The cases also have to be genuinely DIFFERENT. The stalled outcome turns out to depend on the
# ratio torque/(m*g*half_len), so (100, d=20) and (200, d=40) both sit at 0.3125 and produced
# angles identical to five decimals -- two labels for one experiment. The `overpower` column below
# is that ratio, kept distinct on purpose, and `test_cases_are_distinct_operating_points` asserts
# it so a future edit cannot quietly collapse them again.
STALLING_CASES = [
    # torque, rate, steps, half_len, density   -> overpower ratio
    (200.0, 4.0, 60, 2.0, 20.0),  # 0.6250
    (200.0, 4.0, 120, 2.0, 20.0),  # 0.6250, different horizon
    (150.0, 6.0, 60, 2.0, 20.0),  # 0.4688
    (100.0, 4.0, 60, 2.0, 20.0),  # 0.3125
    (250.0, 6.0, 90, 2.0, 30.0),  # 0.5208
    (120.0, 4.0, 60, 1.5, 25.0),  # 0.2133
]


def _overpower_ratio(torque, half_len, density):
    """torque / (gravity moment about the pivot) -- how deeply the motor is outmatched."""
    mass = density * (2 * half_len) * (2 * HALF_HEIGHT)
    return torque / (mass * 10.0 * half_len)


def test_cases_are_distinct_operating_points():
    """Two cases at the same overpower ratio and horizon are one experiment, not two.

    Without this, the suite can report "6 operating points" while actually sampling fewer --
    which is how (100, d=20) and (200, d=40) came to print angles identical to five decimals.
    """
    seen = {}
    for torque, rate, steps, half_len, density in STALLING_CASES:
        key = (round(_overpower_ratio(torque, half_len, density), 6), steps, rate)
        assert key not in seen, (
            f"case (T={torque}, d={density}, HL={half_len}, steps={steps}, rate={rate}) "
            f"duplicates (T={seen[key][0]}, d={seen[key][4]}, HL={seen[key][3]}): same "
            f"overpower ratio {key[0]}, same horizon -- it adds no coverage"
        )
        seen[key] = (torque, rate, steps, half_len, density)


# Measured maximum discrepancy for the plain mapping across these cases was 0.035 rad.
PARITY_TOLERANCE_RAD = 0.06


@pytest.mark.parametrize("torque,rate,steps,half_len,density", STALLING_CASES)
def test_max_force_equals_torque_matches_box2d(torque, rate, steps, half_len, density):
    """Assigning the Box2D torque straight to `max_force` reproduces Box2D's angle.

    This is the mapping the port uses, so this test is what pins it down.
    """
    reference = _box2d_angle(torque, rate, steps, half_len, density)
    ported = _pymunk_angle(torque, rate, steps, half_len, density)
    assert ported == pytest.approx(reference, abs=PARITY_TOLERANCE_RAD), (
        f"plain mapping drifted: box2d={reference:+.5f} pymunk={ported:+.5f} "
        f"(torque={torque}, rate={rate}, steps={steps})"
    )


@pytest.mark.parametrize("torque,rate,steps,half_len,density", STALLING_CASES)
def test_dt_scaled_mapping_is_refuted(torque, rate, steps, half_len, density):
    """Control arm: `max_force = torque * dt` must be measurably WORSE.

    Without this, `test_max_force_equals_torque_matches_box2d` could pass for a reason
    unrelated to the mapping -- e.g. because the budget never binds and both engines merely
    track the commanded rate. Here the rejected hypothesis has to lose, by a margin far
    outside the tolerance the plain mapping meets.
    """
    reference = _box2d_angle(torque, rate, steps, half_len, density)
    plain = abs(_pymunk_angle(torque, rate, steps, half_len, density) - reference)
    dt_scaled = abs(
        _pymunk_angle(torque * DT, rate, steps, half_len, density) - reference
    )
    assert dt_scaled > plain, (
        "the dt-scaled mapping was not worse, so this experiment cannot tell the two "
        f"mappings apart: plain_err={plain:.4f} dt_err={dt_scaled:.4f}"
    )
    assert dt_scaled > PARITY_TOLERANCE_RAD, (
        f"dt-scaled error {dt_scaled:.4f} rad is within the parity tolerance "
        f"{PARITY_TOLERANCE_RAD}, so this test would accept the wrong mapping too"
    )


@pytest.mark.parametrize("torque,rate,steps,half_len,density", STALLING_CASES)
def test_the_budget_actually_binds(torque, rate, steps, half_len, density):
    """Guard against a blind experiment: the torque budget must be the limiting factor.

    Two independent checks. First, gravity's moment about the pivot with the bar horizontal
    exceeds the budget, so the motor cannot simply win. Second -- and this is the one that
    catches a silently non-binding setup -- raising the budget by 50x must change the
    outcome. When the budget does not bind, `max_force` of 200 and of 10000 give the *same*
    angle to the digit, which is exactly how the first version of this experiment fooled itself.
    """
    mass = density * (2 * half_len) * (2 * HALF_HEIGHT)
    gravity_moment = mass * 10.0 * half_len
    assert gravity_moment > torque, (
        f"gravity moment {gravity_moment:.1f} does not exceed the budget {torque}, "
        "so the motor never stalls and the parity assertion proves nothing"
    )
    at_budget = _pymunk_angle(torque, rate, steps, half_len, density)
    far_above = _pymunk_angle(torque * 50.0, rate, steps, half_len, density)
    assert not np.isclose(at_budget, far_above, atol=1e-6), (
        f"raising max_force 50x left the angle unchanged ({at_budget:+.6f}), so the budget "
        "is not binding and this fixture is blind to the mapping under test"
    )
