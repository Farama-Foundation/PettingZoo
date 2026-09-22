"""Train a Multiwalker policy and render the documentation GIF.

The environment's default rewards are used unchanged, because the GIF has to
show the environment as it ships. That matters more than it sounds: with
``terminate_reward = -100`` against ``forward_reward = 1.0``, a policy that
simply stands still and never drops the package already scores positively.
A shorter run of this same setup learned exactly that -- +6.30 reward, 20/20
full-length episodes, and the package moving 0.95 units before stopping dead.

So displacement, not reward, is the metric this script reports first. See
``eval_multiwalker_policy.py`` for the evaluation table.

Usage::

    python train_multiwalker_policy.py                    # 6M steps, ~20 min on CPU
    python train_multiwalker_policy.py --steps 1000000
    python train_multiwalker_policy.py --gif ../../../docs/environments/sisl/sisl_multiwalker.gif
"""

from __future__ import annotations

import argparse

import numpy as np
import supersuit as ss
from stable_baselines3 import PPO

from pettingzoo.sisl import multiwalker_v9

MODEL = "multiwalker_ppo"


def make_env(n_envs: int = 8):
    env = multiwalker_v9.parallel_env(max_cycles=500)
    env = ss.pettingzoo_env_to_vec_env_v1(env)
    return ss.concat_vec_envs_v1(
        env, n_envs, num_cpus=1, base_class="stable_baselines3"
    )


def train(steps: int, seed: int) -> None:
    """PPO on the default reward. gamma is high so distant forward progress survives discounting.

    ``seed`` is applied to torch and numpy directly rather than through PPO's
    own ``seed=``: SB3 forwards that to ``env.seed()``, which SuperSuit's
    ConcatVecEnv does not implement, so passing it raises AttributeError.

    This pins the run, not the bytes of the checkpoint. PyTorch does not
    promise bit-identical results across versions or hardware, so the thing
    to reproduce is the reported displacement, not a file hash.
    """
    import numpy as np
    import torch

    torch.manual_seed(seed)
    np.random.seed(seed)

    model = PPO(
        "MlpPolicy",
        make_env(),
        verbose=1,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=1024,
        gamma=0.999,
        gae_lambda=0.95,
        ent_coef=0.001,
        clip_range=0.2,
        n_epochs=10,
        policy_kwargs={"net_arch": [256, 256]},
    )
    model.learn(total_timesteps=steps)
    model.save(MODEL)
    print(f"saved {MODEL}.zip")


def render(path: str, seed: int, stride: int, scale: int) -> None:
    """Write the docs GIF and print the displacement it shows.

    ``stride`` and ``scale`` keep the file near the size of the GIF it
    replaces; the repository's existing sisl_multiwalker.gif is ~320 KB.
    """
    try:
        import imageio.v2 as imageio
    except ImportError:
        raise SystemExit("writing a GIF needs imageio: pip install imageio") from None

    model = PPO.load(MODEL)
    env = multiwalker_v9.parallel_env(max_cycles=500, render_mode="rgb_array")
    observations, _ = env.reset(seed=seed)
    inner = env.unwrapped.env
    start_x = float(inner.package.position[0])

    frames = []
    while env.agents:
        actions = {
            agent: model.predict(observations[agent], deterministic=True)[0]
            for agent in env.agents
        }
        observations, _, _, _, _ = env.step(actions)
        frames.append(env.render())
    displacement = float(inner.package.position[0]) - start_x
    env.close()

    small = [np.asarray(f)[::scale, ::scale, :3] for f in frames[::stride]]
    imageio.mimsave(path, small, fps=20, loop=0)
    print(
        f"wrote {path}: seed {seed}, {len(small)} frames, "
        f"package displacement {displacement:.2f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=6_000_000)
    parser.add_argument("--seed", type=int, default=0, help="training seed")
    parser.add_argument("--gif", type=str, default=None)
    parser.add_argument("--gif-seed", type=int, default=1)
    parser.add_argument("--stride", type=int, default=5, help="keep every Nth frame")
    parser.add_argument("--scale", type=int, default=2, help="downsample factor")
    args = parser.parse_args()

    if args.gif:
        render(args.gif, args.gif_seed, args.stride, args.scale)
    else:
        train(args.steps, args.seed)


if __name__ == "__main__":
    main()
