from pettingzoo.classic import gobblet_v1
import argparse
import torch
import os

def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--render_mode", type=str, default="human", help="options: human, human_full, ANSI"
    )
    parser.add_argument(
        "--agent_type", type=str, default="random", help="options: random, DQN"
    )
    return parser

def get_args() -> argparse.Namespace:
    parser = get_parser()
    return parser.parse_known_args()[0]

if __name__ == "__main__":
    # train the agent and watch its performance in a match!
    args = get_args()

    env = gobblet_v1.env(render_mode=args.render_mode)
    env.reset()
    for agent in env.agent_iter():
        observation, reward, termination, truncation, info = env.last()
        if termination:
            print(f"Termination ({agent})")
            env.step(None)
        elif truncation:
            print("Truncated")
        else:
            if args.agent_type == "DQN":
                policy = torch.load(os.getcwd() + "/log/gobblet/dqn/policy.pth")
                action = policy.policies[agent] # debug from taimou training says "the trained policy can be accessed via policy.policies[agents[1]]"
            else: # Use random sampling if no agent type is specified
                action = None if termination or truncation else env.action_space(agent).sample()
            pos = action % 9; piece = (action // 9) + 1
            print(f"AGENT: {agent}, ACTION: {action}, POSITION: {pos}, PIECE: {piece}")
            env.step(action)
