from langchain.chat_models import ChatOpenAI
from pettingzoo_agent import PettingZooAgent

from action_masking_agent import ActionMaskAgent  # isort: skip


def main(agents, env):
    env.reset()

    for agent in agents.values():
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
    from pettingzoo import make

    env = make("aec", "classic/rps-v2", max_cycles=3, render_mode="human")
    agents = {
        name: PettingZooAgent(name=name, model=ChatOpenAI(temperature=1), env=env)
        for name in env.possible_agents
    }
    main(agents, env)


def tic_tac_toe():
    from pettingzoo import make

    env = make("aec", "classic/tictactoe-v3", render_mode="human")
    agents = {
        name: ActionMaskAgent(name=name, model=ChatOpenAI(temperature=0.2), env=env)
        for name in env.possible_agents
    }
    main(agents, env)


def texas_holdem_no_limit():
    from pettingzoo import make

    env = make(
        "aec", "classic/texas_holdem_no_limit-v6", num_players=4, render_mode="human"
    )
    agents = {
        name: ActionMaskAgent(name=name, model=ChatOpenAI(temperature=0.2), env=env)
        for name in env.possible_agents
    }
    main(agents, env)


if __name__ == "__main__":
    rock_paper_scissors()
    tic_tac_toe()
    texas_holdem_no_limit()
