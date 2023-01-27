from pettingzoo.classic import gobblet_v1
import argparse

def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--render_mode", type=str, default="human", help="render modes: human, human_full"
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
        action = None if termination or truncation else env.action_space(agent).sample()  # this is where you would insert your policy
        if not termination and not truncation:
            pos = action % 9; piece = (action // 9) + 1
            print(f"AGENT: {agent}, ACTION: {action}, POSITION: {pos}, PIECE: {piece}")

        env.step(action)

