from langchain.chat_models import ChatOpenAI
from pettingzoo_agent import PettingZooAgent

from action_masking_agent import ActionMaskAgent  # isort: skip


def main(agents, env):
    env.reset()

    for name, agent in agents.items():
        agent.reset()

    for agent_name in env.agent_iter():
        observation, reward, termination, truncation, info = env.last()
        obs_message = agents[agent_name].observe(
            observation, reward, termination, truncation, info
        )
        print(obs_message)
        if termination or truncation:
            action = None
        else:
            action = agents[agent_name].act()
        print(f"Action: {action}")
        env.step(action)
    env.close()


def rock_paper_scissors():
    from pettingzoo.classic import rps_v2

    env = rps_v2.env(max_cycles=3, render_mode="human")
    agents = {
        name: PettingZooAgent(name=name, model=ChatOpenAI(temperature=1), env=env)
        for name in env.possible_agents
    }
    main(agents, env)


def tic_tac_toe():
    from pettingzoo.classic import tictactoe_v3

    env = tictactoe_v3.env(render_mode="human")
    agents = {
        name: ActionMaskAgent(name=name, model=ChatOpenAI(temperature=0.2), env=env)
        for name in env.possible_agents
    }
    main(agents, env)


def texas_holdem_no_limit():
    from pettingzoo.classic import texas_holdem_no_limit_v6

    env = texas_holdem_no_limit_v6.env(num_players=4, render_mode="human")
    agents = {
        name: ActionMaskAgent(name=name, model=ChatOpenAI(temperature=0.2), env=env)
        for name in env.possible_agents
    }
    main(agents, env)


if __name__ == "__main__":
    rock_paper_scissors()
    tic_tac_toe()
    texas_holdem_no_limit()
