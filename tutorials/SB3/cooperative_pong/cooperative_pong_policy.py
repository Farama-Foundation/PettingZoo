"""A scripted Cooperative Pong policy that keeps the ball in play.

Both paddles are driven by the same rule: find the ball in the rendered frame,
compare its vertical centre to the paddle's own centre, and move toward it.
Nothing is trained -- the observation is the full screen, and the three
entities are the only white pixels in it, so they can be separated by their
column position alone.

Geometry, measured rather than assumed (280x480 frame, uint8, white on black):

    left paddle   columns   0..9
    ball          a ~10px-wide run somewhere between the paddles
    right paddle  columns 420..479   (the "cake" paddle, wider by design)

The ball is whichever white column-run is neither of the edge paddles, so the
same detector works for both agents and needs no per-agent tuning.

Usage::

    python cooperative_pong_policy.py --episodes 50
    python cooperative_pong_policy.py --gif docs/cooperative_pong_policy.gif

Actions are Discrete(3): 0 = stay, 1 = move up, 2 = move down.
"""

from __future__ import annotations

import argparse

import numpy as np

# PR #1398 renames this environment v6 -> v7 as part of a physics fix, and
# issue #1385 says the pong policy may want to land after it. Bind whichever
# version the installed PettingZoo actually ships so this script keeps working
# across that rename; the policy itself only reads pixels and is unaffected by
# the bounce change.
try:  # pragma: no cover - exercised by whichever version is installed
    from pettingzoo.butterfly import cooperative_pong_v7 as cooperative_pong
except ImportError:
    from pettingzoo.butterfly import cooperative_pong_v6 as cooperative_pong

STAY, UP, DOWN = 0, 1, 2


def _white_mask(frame: np.ndarray) -> np.ndarray:
    """Boolean mask of the lit pixels. The frame is pure black and white."""
    return frame[:, :, 0] > 127


def _edge_runs(mask: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Lit pixels contiguously connected to the left and to the right edge.

    Both paddles are anchored to their own screen edge and the ball never is,
    so edge connectivity separates them without hard-coded columns. The right
    paddle is a four-rectangle staircase spanning 60 px, and a fixed column cut
    wide enough to contain it also hides every ball in that strip.
    """
    left = np.cumprod(mask, axis=1).astype(bool)
    right = np.cumprod(mask[:, ::-1], axis=1)[:, ::-1].astype(bool)
    return left, right


def find_ball_y(frame: np.ndarray) -> float | None:
    """Vertical centre of the ball, or None when it is not on screen.

    The ball is whatever is lit but not joined to either edge, because every
    entity renders in the same white and only the paddles touch an edge.
    """
    mask = _white_mask(frame)
    left, right = _edge_runs(mask)
    rows = np.nonzero((mask & ~left & ~right).any(axis=1))[0]
    if rows.size == 0:
        return None
    return float((rows[0] + rows[-1]) / 2.0)


def find_paddle_y(frame: np.ndarray, side: str) -> float | None:
    """Vertical centre of one paddle, read from the run joined to its edge."""
    mask = _white_mask(frame)
    left, right = _edge_runs(mask)
    rows = np.nonzero((left if side == "left" else right).any(axis=1))[0]
    if rows.size == 0:
        return None
    return float((rows[0] + rows[-1]) / 2.0)


def act(frame: np.ndarray, side: str, deadzone: float) -> int:
    """Move the paddle toward the ball's row.

    The deadzone stops the paddle oscillating around a ball it is already
    lined up with; without it the paddle jitters and loses ground on a fast
    vertical approach.
    """
    ball_y = find_ball_y(frame)
    paddle_y = find_paddle_y(frame, side)
    if ball_y is None or paddle_y is None:
        return STAY
    delta = ball_y - paddle_y
    if abs(delta) <= deadzone:
        return STAY
    return DOWN if delta > 0 else UP


def run_episode(
    seed: int, max_cycles: int, deadzone: float, frames: list | None = None
) -> tuple[float, int]:
    """Play one episode. Returns (reward for one paddle, steps survived)."""
    env = cooperative_pong.parallel_env(max_cycles=max_cycles, render_mode="rgb_array")
    observations, _ = env.reset(seed=seed)
    total = 0.0
    steps = 0
    while env.agents:
        actions = {
            agent: act(
                observations[agent],
                "left" if agent == "paddle_0" else "right",
                deadzone,
            )
            for agent in env.agents
        }
        observations, rewards, _, _, _ = env.step(actions)
        # Both paddles are rewarded identically in this cooperative task.
        total += float(next(iter(rewards.values()), 0.0))
        steps += 1
        if frames is not None:
            frames.append(env.render())
    env.close()
    return total, steps


def run_random(seed: int, max_cycles: int) -> tuple[float, int]:
    """Seeded random control, so the policy's score has something to beat."""
    env = cooperative_pong.parallel_env(max_cycles=max_cycles, render_mode="rgb_array")
    env.reset(seed=seed)
    rng = np.random.default_rng(seed)
    total = 0.0
    steps = 0
    while env.agents:
        actions = {agent: int(rng.integers(0, 3)) for agent in env.agents}
        _, rewards, _, _, _ = env.step(actions)
        total += float(next(iter(rewards.values()), 0.0))
        steps += 1
    env.close()
    return total, steps


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episodes", type=int, default=50)
    parser.add_argument("--max-cycles", type=int, default=900)
    parser.add_argument("--deadzone", type=float, default=4.0)
    parser.add_argument("--seed-start", type=int, default=0)
    parser.add_argument(
        "--gif", type=str, default=None, help="write a GIF of one episode"
    )
    parser.add_argument("--gif-seed", type=int, default=1)
    args = parser.parse_args()

    if args.gif:
        frames: list = []
        reward, steps = run_episode(
            args.gif_seed, args.max_cycles, args.deadzone, frames
        )
        try:
            import imageio.v2 as imageio
        except ImportError:
            raise SystemExit(
                "writing a GIF needs imageio: pip install imageio"
            ) from None
        imageio.mimsave(args.gif, frames, fps=30, loop=0)
        print(
            f"wrote {args.gif}: seed {args.gif_seed}, reward {reward:.2f}, {steps} steps, {len(frames)} frames"
        )
        return

    seeds = range(args.seed_start, args.seed_start + args.episodes)
    policy = [run_episode(s, args.max_cycles, args.deadzone) for s in seeds]
    random = [run_random(s, args.max_cycles) for s in seeds]

    p_reward = np.array([r for r, _ in policy])
    p_steps = np.array([s for _, s in policy])
    r_reward = np.array([r for r, _ in random])
    r_steps = np.array([s for _, s in random])

    print(
        f"seeds {args.seed_start}..{args.seed_start + args.episodes - 1}, max_cycles={args.max_cycles}"
    )
    print(
        f"  scripted policy: reward {p_reward.mean():7.2f} +- {p_reward.std():5.2f}   steps {p_steps.mean():7.1f}"
    )
    print(
        f"  seeded random  : reward {r_reward.mean():7.2f} +- {r_reward.std():5.2f}   steps {r_steps.mean():7.1f}"
    )
    survived = int((p_steps >= args.max_cycles).sum())
    print(
        f"  full-length episodes: {survived}/{args.episodes} scripted, "
        f"{int((r_steps >= args.max_cycles).sum())}/{args.episodes} random"
    )


if __name__ == "__main__":
    main()
