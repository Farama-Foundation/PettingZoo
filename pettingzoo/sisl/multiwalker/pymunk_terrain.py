"""Procedural terrain for the Pymunk Multiwalker port.

The prototype in PettingZoo #1435 only builds flat ground. The Box2D
implementation generates terrain procedurally in `_generate_terrain(hardcore)`,
and that generator is what makes the environment a real task rather than a
walking demo, so it is the next piece the port needs.

Parity here is not "looks similar". The terrain is a pure function of the draws
taken from `np_random`, in order, so a correct port has to consume that stream in
exactly the same sequence as Box2D: same call, same arguments, same number of
draws per step. Change the order and a given seed produces different ground,
which silently breaks every reproducibility guarantee the environment offers and
makes any learning-curve comparison against the Box2D version meaningless.

This module therefore keeps the state machine's control flow identical to
`multiwalker_base._generate_terrain` and only swaps out the body creation. It
computes the terrain purely -- x/y arrays plus the polygons for pits, stumps and
stairs -- so it can be tested against the Box2D generator's RNG consumption
without a physics engine present, and then handed to Pymunk separately.

Reference: pettingzoo/sisl/multiwalker/multiwalker_base.py, `_generate_terrain`.
"""

from __future__ import annotations

import numpy as np

# Mirrors multiwalker_base. Kept local so this module can be tested standalone.
SCALE = 30.0
VIEWPORT_H = 400
TERRAIN_STEP = 14 / SCALE
TERRAIN_LENGTH = 200
TERRAIN_HEIGHT = VIEWPORT_H / SCALE / 4
TERRAIN_GRASS = 10
TERRAIN_STARTPAD = 20
FRICTION = 2.5

GRASS, STUMP, STAIRS, PIT, _STATES_ = range(5)


class Terrain:
    """The result of one terrain generation.

    `x` and `y` are the ground polyline. `obstacles` holds the extra static
    polygons -- pit walls, stumps and stair treads -- each as a list of (x, y)
    vertices in world units, tagged with the state that produced it so callers
    can colour or filter them.
    """

    __slots__ = ("x", "y", "obstacles", "edges")

    def __init__(self, x, y, obstacles, edges):
        self.x = x
        self.y = y
        self.obstacles = obstacles
        self.edges = edges

    def __len__(self):
        return len(self.x)


def generate_terrain(np_random, hardcore=False, terrain_length=TERRAIN_LENGTH):
    """Generate terrain, consuming `np_random` exactly as Box2D does.

    The draw order below is load-bearing and must not be reordered:

      1. per-step `uniform(-1, 1)` while in GRASS past the start pad;
      2. `integers(3, 5)` on entering PIT;
      3. `integers(1, 3)` on entering STUMP;
      4. `random()`, `integers(4, 5)`, `integers(3, 5)` on entering STAIRS,
         in that order;
      5. `integers(TERRAIN_GRASS / 2, TERRAIN_GRASS)` whenever the counter
         reaches zero, followed by `integers(1, _STATES_)` only when hardcore
         and the current state is GRASS.

    Returns a Terrain. No physics objects are created here.
    """
    state = GRASS
    velocity = 0.0
    y = TERRAIN_HEIGHT
    counter = TERRAIN_STARTPAD
    oneshot = False
    terrain_x = []
    terrain_y = []
    obstacles = []

    # Bound to the enclosing scope by the state machine, exactly as in Box2D
    # where they are attributes assigned in one branch and read in another.
    original_y = y
    stair_height = 0
    stair_width = 0
    stair_steps = 0

    for i in range(terrain_length):
        x = i * TERRAIN_STEP
        terrain_x.append(x)

        if state == GRASS and not oneshot:
            velocity = 0.8 * velocity + 0.01 * np.sign(TERRAIN_HEIGHT - y)
            if i > TERRAIN_STARTPAD:
                velocity += np_random.uniform(-1, 1) / SCALE
            y += velocity

        elif state == PIT and oneshot:
            counter = np_random.integers(3, 5)
            poly = [
                (x, y),
                (x + TERRAIN_STEP, y),
                (x + TERRAIN_STEP, y - 4 * TERRAIN_STEP),
                (x, y - 4 * TERRAIN_STEP),
            ]
            obstacles.append(("pit", list(poly)))
            obstacles.append(
                ("pit", [(p[0] + TERRAIN_STEP * counter, p[1]) for p in poly])
            )
            counter += 2
            original_y = y

        elif state == PIT and not oneshot:
            y = original_y
            if counter > 1:
                y -= 4 * TERRAIN_STEP

        elif state == STUMP and oneshot:
            counter = np_random.integers(1, 3)
            obstacles.append(
                (
                    "stump",
                    [
                        (x, y),
                        (x + counter * TERRAIN_STEP, y),
                        (x + counter * TERRAIN_STEP, y + counter * TERRAIN_STEP),
                        (x, y + counter * TERRAIN_STEP),
                    ],
                )
            )

        elif state == STAIRS and oneshot:
            stair_height = +1 if np_random.random() > 0.5 else -1
            stair_width = np_random.integers(4, 5)
            stair_steps = np_random.integers(3, 5)
            original_y = y
            for s in range(stair_steps):
                obstacles.append(
                    (
                        "stairs",
                        [
                            (
                                x + (s * stair_width) * TERRAIN_STEP,
                                y + (s * stair_height) * TERRAIN_STEP,
                            ),
                            (
                                x + ((1 + s) * stair_width) * TERRAIN_STEP,
                                y + (s * stair_height) * TERRAIN_STEP,
                            ),
                            (
                                x + ((1 + s) * stair_width) * TERRAIN_STEP,
                                y + (-1 + s * stair_height) * TERRAIN_STEP,
                            ),
                            (
                                x + (s * stair_width) * TERRAIN_STEP,
                                y + (-1 + s * stair_height) * TERRAIN_STEP,
                            ),
                        ],
                    )
                )
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

    edges = [
        ((terrain_x[i], terrain_y[i]), (terrain_x[i + 1], terrain_y[i + 1]))
        for i in range(terrain_length - 1)
    ]
    return Terrain(terrain_x, terrain_y, obstacles, edges)


def add_terrain_to_space(space, terrain, shape_filter=None):
    """Attach a generated Terrain to a Pymunk space as static geometry.

    Ground is a chain of segments rather than one polygon so that concave
    terrain -- which every pit produces -- is representable at all; Pymunk
    polygons must be convex. Obstacles are convex quads and go in as polygons.
    """
    import pymunk

    shapes = []
    static = space.static_body
    for a, b in terrain.edges:
        seg = pymunk.Segment(static, a, b, 0.0)
        seg.friction = FRICTION
        if shape_filter is not None:
            seg.filter = shape_filter
        space.add(seg)
        shapes.append(seg)
    for kind, verts in terrain.obstacles:
        poly = pymunk.Poly(static, verts)
        poly.friction = FRICTION
        if shape_filter is not None:
            poly.filter = shape_filter
        space.add(poly)
        shapes.append(poly)
    return shapes
