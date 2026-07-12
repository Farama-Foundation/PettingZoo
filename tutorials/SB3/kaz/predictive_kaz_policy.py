"""Search, evaluate, and render a predictive vector policy for KAZ.

The controller is intentionally small and inspectable. Archers solve a basic
projectile-intercept problem, agents prioritize zombies nearest the bottom of
the board, and a compact grid search calibrates the few policy thresholds.
"""

from __future__ import annotations

import argparse
import itertools
import math
from dataclasses import asdict, dataclass, replace
from pathlib import Path

import numpy as np
from PIL import Image

from pettingzoo.butterfly import knights_archers_zombies_v11

SCREEN_WIDTH = 1280.0
SCREEN_HEIGHT = 720.0
ARROW_SPEED = 45.0
ZOMBIE_Y_SPEED = 5.0


@dataclass(frozen=True)
class PolicyParams:
    """Parameters selected by the reproducible search below."""

    archer_alignment: float = 0.9962
    archer_lead: float = 0.5
    split_archer_targets: bool = True
    knight_alignment: float = 0.72
    knight_attack_distance: float = 0.105
    knight_approach_distance: float = 0.30
    knight_min_y: float = 0.62


@dataclass
class EpisodeResult:
    reward: float
    frames: list[np.ndarray]


def active_zombies(observation: np.ndarray) -> list[np.ndarray]:
    """Return active zombie rows from a vector-masked observation."""
    return [row for row in observation if row[0] > 0.5 and row[6] > 0.0]


def world_position(current: np.ndarray, target: np.ndarray) -> tuple[float, float]:
    """Recover a target's normalized world position from relative state."""
    return float(current[7] + target[7]), float(current[8] + target[8])


def target_for_agent(
    observation: np.ndarray, agent: str, params: PolicyParams
) -> np.ndarray | None:
    """Prioritize the bottom-most threat and split targets when useful."""
    current = observation[0]
    zombies = active_zombies(observation)
    if not zombies:
        return None

    zombies.sort(
        key=lambda row: (
            -world_position(current, row)[1],
            float(row[6]),
            abs(float(row[7])),
        )
    )

    agent_index = int(agent.rsplit("_", 1)[1])
    if agent.startswith("archer") and params.split_archer_targets:
        return zombies[min(agent_index, len(zombies) - 1)]
    if agent.startswith("knight"):
        return zombies[min(agent_index, len(zombies) - 1)]
    return zombies[0]


def intercept_direction(target: np.ndarray, lead: float) -> tuple[float, float]:
    """Aim at the positive-time intercept of an arrow and moving zombie."""
    rel_x = float(target[7]) * SCREEN_WIDTH
    rel_y = float(target[8]) * SCREEN_HEIGHT

    # KAZ zombies move five pixels down each cycle and have a small, slightly
    # left-biased random wobble. ``lead`` is calibrated by the search function.
    zombie_vx = -lead
    zombie_vy = ZOMBIE_Y_SPEED * lead

    a = zombie_vx**2 + zombie_vy**2 - ARROW_SPEED**2
    b = 2.0 * (rel_x * zombie_vx + rel_y * zombie_vy)
    c = rel_x**2 + rel_y**2
    discriminant = b**2 - 4.0 * a * c

    time_to_hit = 0.0
    if discriminant >= 0.0 and abs(a) > 1e-9:
        roots = (
            (-b - math.sqrt(discriminant)) / (2.0 * a),
            (-b + math.sqrt(discriminant)) / (2.0 * a),
        )
        positive_roots = [root for root in roots if root > 0.0]
        if positive_roots:
            time_to_hit = min(positive_roots)

    aim_x = rel_x + zombie_vx * time_to_hit
    aim_y = rel_y + zombie_vy * time_to_hit
    norm = math.hypot(aim_x, aim_y) or 1.0
    return aim_x / norm, aim_y / norm


def rotate_toward(current: np.ndarray, target_x: float, target_y: float) -> int:
    """Choose the shorter rotation direction toward a unit target vector."""
    heading_x = float(current[9])
    heading_y = float(current[10])
    cross = heading_x * target_y - heading_y * target_x
    return 3 if cross > 0.0 else 2


def policy_action(
    observation: np.ndarray, agent: str, params: PolicyParams = PolicyParams()
) -> int:
    """Map a vector-masked observation to one of the six KAZ actions."""
    current = observation[0]
    target = target_for_agent(observation, agent, params)
    if target is None:
        return 5

    if agent.startswith("archer"):
        target_x, target_y = intercept_direction(target, params.archer_lead)
        alignment = float(current[9]) * target_x + float(current[10]) * target_y
        if alignment < params.archer_alignment:
            return rotate_toward(current, target_x, target_y)
        return 4

    rel_x = float(target[7]) * SCREEN_WIDTH
    rel_y = float(target[8]) * SCREEN_HEIGHT
    norm = math.hypot(rel_x, rel_y) or 1.0
    target_x = rel_x / norm
    target_y = rel_y / norm
    alignment = float(current[9]) * target_x + float(current[10]) * target_y
    distance = float(target[6])

    if alignment < params.knight_alignment:
        return rotate_toward(current, target_x, target_y)
    if distance <= params.knight_attack_distance:
        return 4
    if (
        distance <= params.knight_approach_distance
        and float(current[8]) > params.knight_min_y
    ):
        return 0
    return 5


def run_episode(
    seed: int,
    params: PolicyParams = PolicyParams(),
    *,
    max_cycles: int = 900,
    max_zombies: int = 10,
    random_policy: bool = False,
    render: bool = False,
    frame_stride: int = 8,
) -> EpisodeResult:
    """Run one deterministically seeded episode."""
    env = knights_archers_zombies_v11.env(
        render_mode="rgb_array" if render else None,
        max_cycles=max_cycles,
        max_zombies=max_zombies,
        max_arrows=10,
        obs_method="vector-masked",
    )
    env.reset(seed=seed)
    for index, agent in enumerate(env.possible_agents):
        env.action_space(agent).seed(seed * 1009 + index)

    total_reward = 0.0
    frames: list[np.ndarray] = []
    step = 0
    for agent in env.agent_iter():
        observation, reward, termination, truncation, _ = env.last()
        total_reward += reward

        if termination or truncation:
            action = None
        elif random_policy:
            action = env.action_space(agent).sample()
        else:
            action = policy_action(observation, agent, params)
        env.step(action)

        if render and step % frame_stride == 0:
            frame = env.render()
            if frame is not None:
                frames.append(frame)
        step += 1

    env.close()
    return EpisodeResult(total_reward, frames)


def evaluate(
    seeds: range,
    params: PolicyParams,
    *,
    max_cycles: int,
    max_zombies: int,
    random_policy: bool = False,
) -> np.ndarray:
    """Evaluate a policy on an explicit seed block."""
    return np.array(
        [
            run_episode(
                seed,
                params,
                max_cycles=max_cycles,
                max_zombies=max_zombies,
                random_policy=random_policy,
            ).reward
            for seed in seeds
        ],
        dtype=np.float64,
    )


def search_params(
    seeds: range, *, max_cycles: int, max_zombies: int
) -> tuple[PolicyParams, np.ndarray]:
    """Search a compact, interpretable controller parameter grid."""
    base = PolicyParams()
    best_params = base
    best_scores = np.array([], dtype=np.float64)
    best_key = (float("-inf"), float("-inf"))

    candidates = itertools.product(
        (False, True),
        (0.25, 0.5, 0.75, 1.0),
        (0.9848, 0.9914, 0.9962, 0.9986),
    )
    for split_targets, lead, alignment in candidates:
        params = replace(
            base,
            split_archer_targets=split_targets,
            archer_lead=lead,
            archer_alignment=alignment,
        )
        scores = evaluate(
            seeds,
            params,
            max_cycles=max_cycles,
            max_zombies=max_zombies,
        )
        key = (float(np.mean(scores)), -float(np.std(scores)))
        if key > best_key:
            best_key = key
            best_params = params
            best_scores = scores

    return best_params, best_scores


def paired_bootstrap_ci(
    differences: np.ndarray, *, samples: int = 20_000, seed: int = 20260710
) -> tuple[float, float]:
    """Return a deterministic percentile CI for the paired mean difference."""
    rng = np.random.default_rng(seed)
    indexes = rng.integers(0, len(differences), size=(samples, len(differences)))
    means = differences[indexes].mean(axis=1)
    low, high = np.quantile(means, [0.025, 0.975])
    return float(low), float(high)


def save_gif(
    frames: list[np.ndarray],
    output_path: Path,
    *,
    width: int,
    colors: int,
    duration_ms: int,
) -> None:
    """Write compact, documentation-ready RGB frames as an animated GIF."""
    if not frames:
        raise ValueError("No frames were captured")

    height = round(width * frames[0].shape[0] / frames[0].shape[1])
    images = [
        Image.fromarray(frame)
        .resize((width, height), Image.Resampling.LANCZOS)
        .quantize(colors=colors)
        for frame in frames
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=duration_ms,
        loop=0,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=10)
    parser.add_argument("--eval-start", type=int, default=1000)
    parser.add_argument("--max-cycles", type=int, default=900)
    parser.add_argument("--max-zombies", type=int, default=10)
    parser.add_argument("--search", action="store_true")
    parser.add_argument("--search-episodes", type=int, default=5)
    parser.add_argument("--render-gif", type=Path)
    parser.add_argument("--gif-seed", type=int)
    parser.add_argument("--gif-width", type=int, default=640)
    parser.add_argument("--gif-colors", type=int, default=256)
    parser.add_argument("--gif-duration-ms", type=int, default=240)
    parser.add_argument("--frame-stride", type=int, default=64)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.episodes <= 0 or args.search_episodes <= 0:
        raise ValueError("Episode counts must be positive")

    params = PolicyParams()
    if args.search:
        params, search_scores = search_params(
            range(args.search_episodes),
            max_cycles=args.max_cycles,
            max_zombies=args.max_zombies,
        )
        print("Selected params:", asdict(params))
        print("Search scores:", search_scores.astype(int).tolist())

    eval_seeds = range(args.eval_start, args.eval_start + args.episodes)
    policy_scores = evaluate(
        eval_seeds,
        params,
        max_cycles=args.max_cycles,
        max_zombies=args.max_zombies,
    )
    random_scores = evaluate(
        eval_seeds,
        params,
        max_cycles=args.max_cycles,
        max_zombies=args.max_zombies,
        random_policy=True,
    )
    ci_low, ci_high = paired_bootstrap_ci(policy_scores - random_scores)

    print("Evaluation seeds:", f"{eval_seeds.start}..{eval_seeds.stop - 1}")
    print("Policy scores:", policy_scores.astype(int).tolist())
    print("Random scores:", random_scores.astype(int).tolist())
    print(f"Policy mean: {np.mean(policy_scores):.2f}")
    print(f"Random mean: {np.mean(random_scores):.2f}")
    print(
        "Paired mean improvement: "
        f"{np.mean(policy_scores - random_scores):.2f} "
        f"(bootstrap 95% CI [{ci_low:.2f}, {ci_high:.2f}])"
    )

    if args.render_gif is not None:
        if args.gif_seed is None:
            median = float(np.median(policy_scores))
            gif_seed = min(
                eval_seeds,
                key=lambda seed: (
                    abs(policy_scores[seed - eval_seeds.start] - median),
                    seed,
                ),
            )
        else:
            gif_seed = args.gif_seed

        result = run_episode(
            gif_seed,
            params,
            max_cycles=args.max_cycles,
            max_zombies=args.max_zombies,
            render=True,
            frame_stride=args.frame_stride,
        )
        save_gif(
            result.frames,
            args.render_gif,
            width=args.gif_width,
            colors=args.gif_colors,
            duration_ms=args.gif_duration_ms,
        )
        print(f"Rendered representative seed {gif_seed}: reward {result.reward:.0f}")
        print(f"Wrote {args.render_gif}")


if __name__ == "__main__":
    main()
