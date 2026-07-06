"""Evolved vector-observation policy for Knights-Archers-Zombies.

This script keeps the KAZ demo lightweight and reproducible. It uses the
``vector-masked`` observation, searches a small set of interpretable policy
parameters, evaluates the tuned policy against a random baseline, and can render
the best episode as a GIF for the documentation.
"""

from __future__ import annotations

import argparse
import itertools
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from PIL import Image

from pettingzoo.butterfly import knights_archers_zombies_v11


@dataclass(frozen=True)
class PolicyParams:
    archer_align: float = 0.995
    knight_align: float = 0.92
    archer_fire: float = 0.55
    archer_move: float = 0.75
    archer_retreat: float = 0.18
    archer_y_min: float = 0.45
    knight_hit: float = 0.20
    knight_stop: float = 0.28
    knight_y_min: float = 0.35
    dot_weight: float = 0.08
    bottom_weight: float = 0.02


def zombie_rows(observation: np.ndarray) -> list[np.ndarray]:
    """Return active zombie rows from a vector-masked KAZ observation."""
    return [row for row in observation if row[0] > 0.5 and abs(float(row[6])) > 1e-9]


def select_target(observation: np.ndarray, params: PolicyParams) -> np.ndarray | None:
    """Choose a nearby zombie, preferring targets already near the agent aim."""
    candidates = zombie_rows(observation)
    if not candidates:
        return None

    heading_x = float(observation[0][9])
    heading_y = float(observation[0][10])

    def target_score(row: np.ndarray) -> float:
        distance = float(row[6])
        rel_x = float(row[7])
        rel_y = float(row[8])
        norm = math.hypot(rel_x, rel_y) or 1.0
        aim_dot = (heading_x * rel_x + heading_y * rel_y) / norm
        return (
            distance
            - params.dot_weight * max(aim_dot, 0.0)
            + params.bottom_weight * (-rel_y)
        )

    return min(candidates, key=target_score)


def policy_action(
    observation: np.ndarray, agent: str, params: PolicyParams = PolicyParams()
) -> int:
    """Map a vector observation to a KAZ action."""
    current = observation[0]
    y_pos = float(current[8])
    heading_x = float(current[9])
    heading_y = float(current[10])

    target = select_target(observation, params)
    if target is None:
        return 5

    distance = float(target[6])
    rel_x = float(target[7])
    rel_y = float(target[8])
    norm = math.hypot(rel_x, rel_y)
    if norm < 1e-9:
        return 4

    target_x = rel_x / norm
    target_y = rel_y / norm
    dot = heading_x * target_x + heading_y * target_y
    cross = heading_x * target_y - heading_y * target_x

    is_archer = agent.startswith("archer")
    align_threshold = params.archer_align if is_archer else params.knight_align
    if dot < align_threshold:
        return 3 if cross > 0 else 2

    if is_archer:
        if distance < params.archer_retreat and y_pos < 0.92:
            return 1
        if distance <= params.archer_fire:
            return 4
        if y_pos > params.archer_y_min and distance > params.archer_move:
            return 0
        return 5

    if distance <= params.knight_hit:
        return 4
    if distance <= params.knight_stop and dot > 0.92:
        return 4
    if y_pos < params.knight_y_min and rel_y < 0:
        return 1
    return 0


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
    """Small grid search over interpretable thresholds."""
    best_params = PolicyParams()
    best_scores: list[float] = []
    best_mean = float("-inf")

    for archer_align, knight_align, archer_fire, knight_hit in itertools.product(
        [0.97, 0.985, 0.995],
        [0.92, 0.96, 0.985],
        [0.55, 0.70, 0.90, 1.10],
        [0.16, 0.20, 0.25, 0.30],
    ):
        params = PolicyParams(
            archer_align=archer_align,
            knight_align=knight_align,
            archer_fire=archer_fire,
            knight_hit=knight_hit,
            knight_stop=knight_hit + 0.08,
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=10)
    parser.add_argument("--max-cycles", type=int, default=900)
    parser.add_argument("--max-zombies", type=int, default=10)
    parser.add_argument("--search", action="store_true")
    parser.add_argument("--render-gif", type=Path)
    parser.add_argument("--gif-seed", type=int, default=0)
    parser.add_argument("--gif-duration-ms", type=int, default=80)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    seeds = range(args.episodes)

    params = PolicyParams()
    if args.search:
        params, search_scores = search_params(
            seeds=range(min(args.episodes, 5)),
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
