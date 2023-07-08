import glob
import os

from sb3_contrib import MaskablePPO

from pettingzoo.classic import chess_v6


def watch_action_mask(env_fn):
    # Watch a game between two trained agents
    env = env_fn.env(render_mode="human")
    env.reset()

    # If training script has not been run, run it now
    try:
        latest_policy = max(
            glob.glob(f"{env.metadata['name']}*.zip"), key=os.path.getctime
        )
    except ValueError:
        print("Policy not found. Running training to generate new policy.")

        from tutorials.SB3.sb3_chess_action_mask import train_action_mask

        train_action_mask(env_fn)

        latest_policy = max(
            glob.glob(f"{env.metadata['name']}*.zip"), key=os.path.getctime
        )

    model = MaskablePPO.load(latest_policy)

    for agent in env.agent_iter():
        obs, reward, termination, truncation, info = env.last()

        # Separate observation and action mask
        observation, action_mask = obs.values()

        if termination or truncation:
            act = None
        else:
            # Note: PettingZoo expects integer actions
            act = int(model.predict(observation, action_masks=action_mask)[0])
        env.step(act)
    env.close()


if __name__ == "__main__":
    watch_action_mask(chess_v6)
