"""Evaluate the Multiwalker policy. Displacement is the load-bearing metric.

Reward alone cannot distinguish a walking policy from one that stands still:
terminate_reward is -100 while forward_reward is 1.0, so simply not falling
scores well. The package's x displacement is what the task is actually about,
so it is reported first and every claim rests on it.
"""

import argparse

import numpy as np
from stable_baselines3 import PPO

from pettingzoo.sisl import multiwalker_v9 as mw


def episode(policy, seed, max_cycles):
    env = mw.parallel_env(max_cycles=max_cycles)
    obs, _ = env.reset(seed=seed)
    inner = env.unwrapped.env
    x0 = float(inner.package.position[0])
    total, steps = 0.0, 0
    while env.agents:
        actions = {a: policy(obs[a]) for a in env.agents}
        obs, rewards, _, _, _ = env.step(actions)
        total += float(next(iter(rewards.values()), 0.0))
        steps += 1
    displacement = float(inner.package.position[0]) - x0
    env.close()
    return total, steps, displacement


def block(policy, start, n, max_cycles):
    out = [episode(policy, s, max_cycles) for s in range(start, start + n)]
    r, s, d = (np.array(x) for x in zip(*out))
    return r, s, d


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="multiwalker_ppo")
    ap.add_argument("--episodes", type=int, default=25)
    ap.add_argument("--max-cycles", type=int, default=500)
    args = ap.parse_args()

    model = PPO.load(args.model)
    rng = np.random.default_rng(0)

    def trained(obs):
        return model.predict(obs, deterministic=True)[0]

    def still(obs):
        """Zero torque. Scores well on reward without going anywhere."""
        return np.zeros(4, dtype=np.float32)

    def rand(obs):
        return rng.uniform(-1, 1, 4).astype(np.float32)

    print(f"{'arm':<16}{'seeds':<12}{'displacement':>16}{'reward':>10}{'steps':>8}")
    for name, pol in [("PPO", trained), ("do nothing", still), ("random", rand)]:
        for start in (0, 1000):
            r, s, d = block(pol, start, args.episodes, args.max_cycles)
            print(
                f"{name:<16}{f'{start}..{start + args.episodes - 1}':<12}"
                f"{d.mean():>10.2f} +-{d.std():5.2f}{r.mean():>10.2f}{s.mean():>8.1f}"
            )


if __name__ == "__main__":
    main()
