"""Uses Pygame and pygbag to run an interactive connect four game locally in the browser.

Usage: Run pygbag Pygame in parent directory (pettingzoo/tutorials), open (http://localhost:8000/)

Author: Elliot Tower (https://github.com/elliottower)
"""


import asyncio
import time

import pygame

from pettingzoo.classic import connect_four_v3


async def main():
    env = connect_four_v3.env(render_mode="human")
    env.reset()

    env.render()  # need to render the environment before pygame can take user input

    for agent in env.agent_iter():
        observation, reward, termination, truncation, info = env.last()
        if termination:
            print(f"Termination ({agent}), Reward: {reward}, info: {info}")
            env.step(None)
        elif truncation:
            print("Truncated")
        else:
            if agent == env.agents[1]:
                # Get user input via the mouse
                while True:
                    event = pygame.event.wait()
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        pygame.display.quit()
                    mousex, mousey = pygame.mouse.get_pos()
                    if mousex < 220:
                        action = 0
                    elif 220 <= mousex < 390:
                        action = 1
                    elif 390 <= mousex < 560:
                        action = 2
                    elif 560 <= mousex < 730:
                        action = 3
                    elif 730 <= mousex < 900:
                        action = 4
                    elif 900 <= mousex < 1070:
                        action = 5
                    else:
                        action = 6
                    env.unwrapped.preview[agent] = action
                    env.render()
                    pygame.display.update()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        env.unwrapped.preview[agent] = -1
                        break
            else:
                action = env.action_space(agent).sample(mask=observation["action_mask"])
                time.sleep(0.25)
            env.step(action)

            await asyncio.sleep(0)  # Very important, and keep it 0


# This is the program entry point:
asyncio.run(main())

# Do not add anything from here
# asyncio.run is non-blocking on pygame-wasm
