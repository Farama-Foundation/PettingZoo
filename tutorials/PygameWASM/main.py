import asyncio
import sys
import time

sys.path.append("modules")

import numpy as np  # noqa: E402 F401
import pygame.surfarray  # noqa: E402 F401

from pettingzoo.classic import chess_v5  # noqa: E402


async def main():
    env = chess_v5.env(render_mode="human")

    seed = 1
    env.reset(seed)
    env.action_space("player_0").seed(seed)
    env.action_space("player_1").seed(seed)

    for _ in range(5):
        env.reset()
        env.render()

        for agent in env.agent_iter():
            observation, reward, termination, truncation, info = env.last()
            if termination or truncation:
                break

            mask = observation["action_mask"]
            action = env.action_space(agent).sample(mask=mask)
            time.sleep(0.25)
            env.step(action)

            await asyncio.sleep(0)  # Very important, and keep it 0

        print("Terminated") if termination else print("Truncated")
        print("Rewards: ", reward)

    await asyncio.sleep(0)  # Very important, and keep it 0


if __name__ == "__main__":
    asyncio.run(main())
