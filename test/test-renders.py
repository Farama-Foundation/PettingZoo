import time

from pettingzoo.classic.rlcard_envs import leduc_holdem, texas_holdem, gin_rummy, texas_holdem_no_limit
from pettingzoo.classic.tictactoe import tictactoe


def main():
    env = leduc_holdem.env(render_mode='human')
    env.reset(seed=1)
    #
    actions = [0, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
    for i, agent in enumerate(env.agent_iter()):
        obs, rew, terms, truncs, info = env.last()
        mask = obs["action_mask"]
        env.render()
        time.sleep(2)
        if terms:
            action = None
        else:
            action = actions[i]
        env.step(action)

    # env = texas_holdem_no_limit.env(num_players=6, render_mode="human")
    # env.reset(seed=42)
    #
    # for agent in env.agent_iter():
    #     observation, reward, terms, truncation, info = env.last()
    #
    #     mask = observation["action_mask"]
    #     if terms:
    #         action = None
    #     else:
    #         action = env.action_space(agent).sample(mask)
    #
    #     time.sleep(2)
    #
    #     env.step(action)
    # env.close()

    # env = texas_holdem.env(num_players=6, render_mode="human")
    # env.reset(seed=42)
    #
    # for i, agent in enumerate(env.agent_iter()):
    #     observation, reward, terms, truncation, info = env.last()
    #
    #     mask = observation["action_mask"]
    #     if terms:
    #         action = None
    #     else:
    #         action = env.action_space(agent).sample(mask)
    #     env.step(action)
    #     time.sleep(1)
    # env.close()

    # env = gin_rummy.env(render_mode='human')
    # env.reset(seed=1)
    # #
    # for agent in env.agent_iter():
    #     obs, rew, terms, truncs, info = env.last()
    #     mask = obs["action_mask"]
    #     # env.render()
    #     if terms:
    #         action = None
    #     else:
    #         action = env.action_space(agent).sample(mask)
    #     env.step(action)


    # env = tictactoe.env(render_mode='human')
    # env.reset(seed=1)
    # #
    # for agent in env.agent_iter():
    #     obs, rew, terms, truncs, info = env.last()
    #     mask = obs["action_mask"]
    #     # env.render()
    #     if terms:
    #         action = None
    #     else:
    #         action = env.action_space(agent).sample(mask)
    #     env.step(action)
    #     time.sleep(1)

    # for _ in range(10):
    #
    #
    #     env.step
    #


"""
np.ceil(len(possible_agents) / 2)           np.ceil((i+1) / 2)              diff

Agents 2: 1                                 NA                              
Agents 3: 2                                 (0: 1, 2: 2)                    
Agents 4: 2
Agents 5: 3
Agents 6: 3

"""



if __name__ == '__main__':
    main()