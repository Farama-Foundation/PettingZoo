import os
import time

import pygame

from typing import Callable, Any

class ManualPolicy():
    def __init__(self, env, agent_id=0, show_obs=False):

        self.env = env
        self.agent_id = agent_id
        self.agent = self.env.agents[self.agent_id]
        self.show_obs = show_obs

        self.clock = pygame.time.Clock()
        self.clock.tick(env.metadata['video.frames_per_second'])

        self.action_space = env.action_space(env.agents[agent_id])

        # action mappings for all agents are the same
        if True:
            self.default_action = 5
            self.action_mapping = dict()
            self.action_mapping[pygame.K_w] = 0
            self.action_mapping[pygame.K_s] = 1
            self.action_mapping[pygame.K_a] = 2
            self.action_mapping[pygame.K_d] = 3
            self.action_mapping[pygame.K_SPACE] = 4

    def forward(self, observation, agent):
        # only triger when we are the correct agent
        assert agent == self.agent, f'Manual Policy only applied to agent: {self.agent}, but got tag for {agent}.'

        # set the default action
        action = self.default_action

        # if we get a key, override action using the dict
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # escape to end
                    exit()
                if event.key == pygame.K_BACKSPACE:
                    # backspace to reset
                    self.env.reset()

                action = self.action_mapping[event.key]

        return action

    @property
    def available_agents(self):
        return self.env.agents
