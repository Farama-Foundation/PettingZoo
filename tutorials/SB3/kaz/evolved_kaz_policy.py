"""Interpretable vector-observation policy for Knights-Archers-Zombies.

The policy uses a small reproducible parameter sweep, projectile interception
for the archers, and a close-range fallback for the knights. It can evaluate
the policy against seeded random actions and render an episode as a GIF.
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
from pettingzoo.butterfly.knights_archers_zombies.src import constants as const


@dataclass(frozen=True)
class PolicyParams:
    """Tunable parameters for the deterministic KAZ policy."""

    archer_align_degrees: float = 6.6
    archer_lane_split: float = 0.70
    left_standby_degrees: float = 0.0
    right_standby_degrees: float = 35.0
    knight_track_distance: float = 260.0
    knight_attack_distance: float = 150.0
    knight_track_degrees: float = 18.0
    knight_attack_degrees: float = 25.0


def zombie_rows(observation: np.ndarray) -> list[np.ndarray]:
    """Return active zombie rows from a vector-masked observation."""
    return [row for row in observation if row[0] > 0.5]


def relative_pixels(row: np.ndarray) -> tuple[float, float]:
    """Convert an entity's normalized relative position to screen pixels."""
    return (
        float(row[7]) * const.SCREEN_WIDTH,
        float(row[8]) * const.SCREEN_HEIGHT,
    )


def normalized_direction(x: float, y: float) -> tuple[float, float]:
    """Return a unit direction, defaulting upward for a zero-length vector."""
    length = math.hypot(x, y)
    if length < 1e-9:
        return 0.0, -1.0
    return x / length, y / length


def intercept_direction(row: np.ndarray) -> tuple[float, float]:
    """Aim where a downward-moving zombie and an arrow should intersect."""
    x, y = relative_pixels(row)
    zombie_speed = float(const.ZOMBIE_Y_SPEED)
    arrow_speed = float(const.ARROW_SPEED)

    # Solve |(x, y) + (0, zombie_speed) * t| = arrow_speed * t.
    a = zombie_speed**2 - arrow_speed**2
    b = 2.0 * y * zombie_speed
    c = x**2 + y**2
    discriminant = max(b**2 - 4.0 * a * c, 0.0)
    roots = (
        (-b + math.sqrt(discriminant)) / (2.0 * a),
        (-b - math.sqrt(discriminant)) / (2.0 * a),
    )
    positive_roots = [root for root in roots if root > 0.0]
    intercept_time = (
        min(positive_roots) if positive_roots else math.sqrt(c) / arrow_speed
    )
    return normalized_direction(x, y + zombie_speed * intercept_time)


def turn_action(
    observation: np.ndarray,
    target_x: float,
    target_y: float,
    *,
    tolerance_degrees: float,
) -> int | None:
    """Return a turn action, or None when the agent is sufficiently aligned."""
    heading_x = float(observation[0][9])
    heading_y = float(observation[0][10])
    dot = heading_x * target_x + heading_y * target_y
    if dot >= math.cos(math.radians(tolerance_degrees)):
        return None

    cross = heading_x * target_y - heading_y * target_x
    return 3 if cross > 0.0 else 2


def archer_standby_action(
    observation: np.ndarray, archer_index: int, params: PolicyParams
) -> int:
    """Fan idle archers across the board so new targets need little turning."""
    angle_degrees = (
        params.left_standby_degrees
        if archer_index % 2 == 0
        else params.right_standby_degrees
    )
    angle = math.radians(angle_degrees)
    action = turn_action(
        observation,
        math.sin(angle),
        -math.cos(angle),
        tolerance_degrees=5.0,
    )
    return 5 if action is None else action


def select_archer_target(
    observation: np.ndarray,
    zombies: list[np.ndarray],
    archer_index: int,
    params: PolicyParams,
) -> np.ndarray:
    """Select an urgent target while giving one archer the far-right lane."""
    current_x = float(observation[0][7])
    primary_lane_is_left = archer_index % 2 == 0

    def target_key(row: np.ndarray) -> tuple[int, float, float]:
        world_x = current_x + float(row[7])
        outside_primary_lane = int(
            (world_x >= params.archer_lane_split) == primary_lane_is_left
        )
        relative_x, relative_y = relative_pixels(row)
        return outside_primary_lane, math.hypot(relative_x, relative_y), -relative_y

    return min(zombies, key=target_key)


def policy_action(
    observation: np.ndarray,
    agent: str,
    params: PolicyParams = PolicyParams(),
) -> int:
    """Map a vector-masked observation to a deterministic KAZ action."""
    zombies = zombie_rows(observation)

    if agent.startswith("archer"):
        archer_index = int(agent.rsplit("_", 1)[1])
        if not zombies:
            return archer_standby_action(observation, archer_index, params)

        target = select_archer_target(observation, zombies, archer_index, params)
        target_x, target_y = intercept_direction(target)
        action = turn_action(
            observation,
            target_x,
            target_y,
            tolerance_degrees=params.archer_align_degrees,
        )
        return 4 if action is None else action

    if not zombies:
        return 5

    target = min(zombies, key=lambda row: math.hypot(*relative_pixels(row)))
    relative_x, relative_y = relative_pixels(target)
    distance = math.hypot(relative_x, relative_y)
    if distance >= params.knight_track_distance:
        return 5

    target_x, target_y = normalized_direction(relative_x, relative_y)
    tolerance = (
        params.knight_attack_degrees
        if distance <= params.knight_attack_distance
        else params.knight_track_degrees
    )
    action = turn_action(
        observation,
        target_x,
        target_y,
        tolerance_degrees=tolerance,
    )
    if action is not None:
        return action
    return 4 if distance <= params.knight_attack_distance else 5


def run_episode(
    seed: int,
    params: PolicyParams = PolicyParams(),
    *,
    max_cycles: int = 900,
    max_zombies: int = 10,
    random_policy: bool = False,
    render: bool = False,
    frame_stride: int = 5,
) -> tuple[float, list[np.ndarray]]:
    """Run one KAZ episode and optionally capture RGB frames."""
    env = knights_archers_zombies_v11.env(
        render_mode="rgb_array" if render else None,
        max_cycles=max_cycles,
        max_zombies=max_zombies,
        max_arrows=10,
        obs_method="vector-masked",
    )
    env.reset(seed=seed)
    for agent_index, agent in enumerate(env.possible_agents):
        env.action_space(agent).seed(seed * 1009 + agent_index)

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
    return total_reward, frames


def evaluate(
    seeds: range,
    params: PolicyParams = PolicyParams(),
    *,
    max_cycles: int,
    max_zombies: int,
    random_policy: bool = False,
) -> list[float]:
    """Evaluate a policy on every seed in a range."""
    return [
        run_episode(
            seed,
            params,
            max_cycles=max_cycles,
            max_zombies=max_zombies,
            random_policy=random_policy,
        )[0]
        for seed in seeds
    ]


def search_params(
    *, seeds: range, max_cycles: int, max_zombies: int
) -> tuple[PolicyParams, list[float]]:
    """Run a small grid search over interpretable archer parameters."""
    defaults = PolicyParams()
    best_params = defaults
    best_scores: list[float] = []
    best_mean = float("-inf")

    for align, lane_split, left_standby, right_standby in itertools.product(
        [6.0, 6.6, 7.0],
        [0.65, 0.70, 0.75],
        [-5.0, 0.0],
        [30.0, 35.0],
    ):
        params = replace(
            defaults,
            archer_align_degrees=align,
            archer_lane_split=lane_split,
            left_standby_degrees=left_standby,
            right_standby_degrees=right_standby,
        )
        scores = evaluate(
            seeds,
            params,
            max_cycles=max_cycles,
            max_zombies=max_zombies,
        )
        mean_score = sum(scores) / len(scores)
        if mean_score > best_mean:
            best_mean = mean_score
            best_params = params
            best_scores = scores

    return best_params, best_scores


def save_gif(frames: list[np.ndarray], output_path: Path, *, duration_ms: int) -> None:
    """Save captured RGB frames as a looping GIF."""
    if not frames:
        raise ValueError("No frames were captured.")

    images = [Image.fromarray(frame) for frame in frames]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=duration_ms,
        loop=0,
    )


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=10)
    parser.add_argument("--seed-start", type=int, default=0)
    parser.add_argument("--max-cycles", type=int, default=900)
    parser.add_argument("--max-zombies", type=int, default=10)
    parser.add_argument("--search", action="store_true")
    parser.add_argument("--render-gif", type=Path)
    parser.add_argument("--gif-seed", type=int, default=0)
    parser.add_argument("--gif-duration-ms", type=int, default=80)
    args = parser.parse_args()
    if args.episodes <= 0:
        parser.error("--episodes must be positive")
    return args


def main() -> None:
    """Evaluate the tuned policy and optionally search or render it."""
    args = parse_args()
    seeds = range(args.seed_start, args.seed_start + args.episodes)

    params = PolicyParams()
    if args.search:
        search_seeds = range(args.seed_start, args.seed_start + min(args.episodes, 5))
        params, search_scores = search_params(
            seeds=search_seeds,
            max_cycles=args.max_cycles,
            max_zombies=args.max_zombies,
        )
        print("Best searched params:", asdict(params))
        print("Search scores:", search_scores)

    policy_scores = evaluate(
        seeds,
        params,
        max_cycles=args.max_cycles,
        max_zombies=args.max_zombies,
    )
    random_scores = evaluate(
        seeds,
        params,
        max_cycles=args.max_cycles,
        max_zombies=args.max_zombies,
        random_policy=True,
    )
    print("Policy params:", asdict(params))
    print(f"Policy scores: {policy_scores}")
    print(f"Random scores: {random_scores}")
    print(f"Policy mean: {sum(policy_scores) / len(policy_scores):.2f}")
    print(f"Random mean: {sum(random_scores) / len(random_scores):.2f}")

    if args.render_gif is not None:
        reward, frames = run_episode(
            args.gif_seed,
            params,
            max_cycles=args.max_cycles,
            max_zombies=args.max_zombies,
            render=True,
        )
        save_gif(frames, args.render_gif, duration_ms=args.gif_duration_ms)
        print(f"Rendered seed {args.gif_seed} with reward {reward:.0f}")
        print(f"Wrote {args.render_gif}")


if __name__ == "__main__":
    main()
