import glob
import os

from sb3_contrib import MaskablePPO

from pettingzoo.classic import chess_v6


def watch_action_mask(env_fn):
    # Watch a game between two trained agents
    env = env_fn.env(render_mode="human")
    env.reset()

    latest_policy = max(glob.glob(f"{env.metadata['name']}*.zip"), key=os.path.getctime)
    model = MaskablePPO.load(latest_policy)

    for agent in env.agent_iter():
        obs, reward, termination, truncation, info = env.last()

        # Separate observation and action mask
        observation, action_mask = obs.values()

        if termination or truncation:
            act = None
        else:
            # Note that use of masks is manual and optional outside of learning,
            # so masking can be "removed" at testing time
            act = int(
                model.predict(observation, action_masks=action_mask)[0]
            )  # PettingZoo expects integer actions
        env.step(act)
    env.close()


if __name__ == "__main__":
    watch_action_mask(chess_v6)
