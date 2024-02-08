import random

import numpy as np
import pygame
from custom_environment import CustomActionMaskedEnvironment, CustomEnvironment


class PygameVisualizer:
    def __init__(self, env, width=700, height=700):
        pygame.init()
        self.env = env
        self.screen = pygame.display.set_mode((width, height))
        self.cell_size = width // 7
        self.colors = {
            "prisoner": (255, 0, 0),  # Red
            "guard": (0, 0, 255),  # Blue
            "escape": (0, 255, 0),  # Green
            "background": (255, 255, 255),  # White
        }

    def draw_grid(self):
        self.screen.fill(self.colors["background"])
        for y in range(7):
            for x in range(7):
                rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

        # Draw the agents
        p_x, p_y = self.env.prisoner_x, self.env.prisoner_y
        g_x, g_y = self.env.guard_x, self.env.guard_y
        e_x, e_y = self.env.escape_x, self.env.escape_y

        pygame.draw.rect(
            self.screen,
            self.colors["prisoner"],
            (
                p_x * self.cell_size,
                p_y * self.cell_size,
                self.cell_size,
                self.cell_size,
            ),
        )
        pygame.draw.rect(
            self.screen,
            self.colors["guard"],
            (
                g_x * self.cell_size,
                g_y * self.cell_size,
                self.cell_size,
                self.cell_size,
            ),
        )
        pygame.draw.rect(
            self.screen,
            self.colors["escape"],
            (
                e_x * self.cell_size,
                e_y * self.cell_size,
                self.cell_size,
                self.cell_size,
            ),
        )

    def run(self, steps):
        running = True
        while steps > 0:
            # Both agents take random actions
            actions = {
                agent: self.env.action_space(agent).sample()
                for agent in self.env.agents
            }

            # Step the environment
            observations, rewards, terminations, truncations, infos = self.env.step(
                actions
            )

            # Draw the grid and agents
            self.draw_grid()

            pygame.display.flip()
            pygame.time.delay(100)

            steps -= 1

            # Check for termination conditions
            if any(terminations.values()):
                if rewards["prisoner"] == 1:
                    print("Prisoner escaped!")
                elif rewards["prisoner"] == -1:
                    print("Prisoner caught by the guard!")
                return

        print("This game has ended because the specified number of steps was reached.")
        return


# Initialize your environment
env = CustomActionMaskedEnvironment()
env.reset()

visualizer = PygameVisualizer(env)
# You can change the number of steps
visualizer.run(100)
