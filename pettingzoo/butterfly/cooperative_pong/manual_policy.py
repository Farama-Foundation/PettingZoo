"""A manual policy for CoooperativePong and script to run it."""
import pygame

from pettingzoo import AECEnv
from pettingzoo.butterfly.cooperative_pong.cooperative_pong import (
    ActionType,
    AgentID,
    ObsType,
)


class ManualPolicy:
    """Manual Policy for CooperativePong.

    See the game's documentation for details.
    """

    def __init__(
        self,
        env: AECEnv[AgentID, ObsType, ActionType],
        agent_id: int = 0,
        show_obs: bool = False,
    ) -> None:
        """Initializes the manual policy.

        Args:
            env: the environment to apply the policy to
            agent_id: the index of the agent to manually control
            show_obs: whether to show observations (not implemented yet)
        """
        self.env = env
        self.agent_id = agent_id
        self.agent = self.env.agents[self.agent_id]

        # TO-DO: show current agent observation if this is True
        self.show_obs = show_obs

        # action mappings for all agents are the same
        if True:
            self.default_action: ActionType = 0
            self.action_mapping: dict[int, ActionType] = dict()
            self.action_mapping[pygame.K_w] = 1
            self.action_mapping[pygame.K_s] = 2

    def __call__(self, observation: ObsType, agent: AgentID) -> ActionType:
        """Apply the manual policy.

        This will move the paddle based on keyboard input.
        The observation is currently ignored.

        Args:
            observation: the current observation
            agent: the agent ID to act on

        Returns:
            An action based on the policy
        """
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


if __name__ == "__main__":
    from pettingzoo.butterfly import cooperative_pong_v6

    env = cooperative_pong_v6.env(render_mode="human")
    env.reset()

    clock = pygame.time.Clock()
    manual_policy = cooperative_pong_v6.ManualPolicy(env)

    for agent in env.agent_iter():
        clock.tick(env.metadata["render_fps"])

        observation, reward, termination, truncation, info = env.last()

        if agent == manual_policy.agent:
            assert observation is not None
            action = manual_policy(observation, agent)
        else:
            action = env.action_space(agent).sample()

        env.step(action)

        if termination or truncation:
            env.reset()
