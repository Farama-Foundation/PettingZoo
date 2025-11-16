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

        self.default_action: ActionType = 0
        self.action_mapping: dict[int, ActionType] = {}

        # action mappings
        if agent_id == 0:
            self.action_mapping[pygame.K_w] = 1
            self.action_mapping[pygame.K_s] = 2
        elif agent_id == 1:
            self.action_mapping[pygame.K_UP] = 1
            self.action_mapping[pygame.K_DOWN] = 2

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

    # which agents will be controlled by manual policies
    MANUAL_AGENTS = [0, 1]

    env = cooperative_pong_v6.env(render_mode="human")
    env.reset()

    # this allows holding down a key for continuous motion. Only a single
    # key will be registered at a time.
    pygame.key.set_repeat(True)

    clock = pygame.time.Clock()

    manual_policies: dict[AgentID, cooperative_pong_v6.ManualPolicy] = {}
    for agent_id in MANUAL_AGENTS:
        new_policy = cooperative_pong_v6.ManualPolicy(env, agent_id)
        manual_policies[new_policy.agent] = new_policy

    for agent in env.agent_iter():
        clock.tick(env.metadata["render_fps"])

        observation, reward, termination, truncation, info = env.last()

        if agent in manual_policies:
            assert observation is not None
            action = manual_policies[agent](observation, agent)
        else:
            action = env.action_space(agent).sample()

        env.step(action)

        if termination or truncation:
            env.reset()
