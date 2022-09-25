import pygame


class ManualPolicy:
    def __init__(self, env, agent_id: int = 0, show_obs: bool = False):

        self.env = env
        self.agent_id = agent_id
        self.agent = self.env.agents[self.agent_id]

        # TO-DO: show current agent observation if this is True
        self.show_obs = show_obs

        # action mappings for all agents are the same
        if True:
            self.default_action = 5
            self.action_mapping = dict()
            self.action_mapping[pygame.K_w] = 0  # front
            self.action_mapping[pygame.K_s] = 1  # back
            self.action_mapping[pygame.K_a] = 2  # rotate left
            self.action_mapping[pygame.K_d] = 3  # rotate right
            self.action_mapping[pygame.K_SPACE] = 4  # weapon

    def __call__(self, observation, agent):
        # only trigger when we are the correct agent
        assert (
            agent == self.agent
        ), f"Manual Policy only applied to agent: {self.agent}, but got tag for {agent}."

        # set the default action
        action = self.default_action

        # if we get a key, override action using the dict
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # escape to end
                    exit()

                elif event.key == pygame.K_BACKSPACE:
                    # backspace to reset
                    self.env.reset()

                elif event.key in self.action_mapping:
                    action = self.action_mapping[event.key]

        return action

    @property
    def available_agents(self):
        return self.env.agent_name_mapping


if __name__ == "__main__":
    from pettingzoo.butterfly import knights_archers_zombies_v10

    clock = pygame.time.Clock()

    env = knights_archers_zombies_v10.env()
    env.reset()

    manual_policy = knights_archers_zombies_v10.ManualPolicy(env)

    for agent in env.agent_iter():
        clock.tick(env.metadata["render_fps"])

        observation, reward, termination, truncation, info = env.last()

        if agent == manual_policy.agent:
            action = manual_policy(observation, agent)
        else:
            action = env.action_space(agent).sample()

        env.step(action)

        env.render()

        if termination or truncation:
            env.reset()
