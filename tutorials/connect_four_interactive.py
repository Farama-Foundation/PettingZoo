from pettingzoo.classic import connect_four_v3
import argparse
import numpy as np
import sys
import pygame


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--render_mode", type=str, default="human", help="options: human, rgb_array"
    )
    parser.add_argument(
        "--agent_type", type=str, default="random", help="options: random, random_admissable"
    )
    parser.add_argument(
        "--seed", type=int, default=None, help="random seed for board and policy"
    )

    return parser

def get_args() -> argparse.Namespace:
    parser = get_parser()
    return parser.parse_known_args()[0]

if __name__ == "__main__":
    # train the agent and watch its performance in a match!
    args = get_args()

    env = connect_four_v3.env(render_mode=args.render_mode)
    if args.seed is not None:
        env.reset(seed=args.seed)
        np.random.seed(args.seed)
    else:
        env.reset()
    turn = 0
    for agent in env.agent_iter():
        observation, reward, termination, truncation, info = env.last()
        if termination:
            print(f"Termination ({agent}), Reward: {reward}, info: {info}")
            env.step(None)
        elif truncation:
            print("Truncated")
        else:
            if args.agent_type == "random":
                action = env.action_space(agent).sample()
            if args.agent_type == "random_admissable":
                action_mask = observation['action_mask']
                action = np.random.choice(np.arange(len(action_mask)), p=action_mask / np.sum(action_mask))
            if agent == env.agents[1]:
                pygame.event.clear()
                while True:
                    event = pygame.event.wait()
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        pygame.display.quit()
                        sys.exit()
                    mousex, mousey = pygame.mouse.get_pos()
                    if  50 <= mousex < 220:
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
                    elif 1070 <= mousex < 1240:
                        action = 6

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        break
            env.step(action)
