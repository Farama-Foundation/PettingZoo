import time

from pettingzoo.classic.rlcard_envs import leduc_holdem, texas_holdem, gin_rummy


def main():
    # env = leduc_holdem.env(num_players=4, render_mode='human')
    # env.reset(seed=1)
    # #
    # for agent in env.agent_iter():
    #     obs, rew, terms, truncs, info = env.last()
    #     mask = obs["action_mask"]
    #     env.render()
    #     time.sleep(2)
    #     if terms:
    #         action = None
    #     else:
    #         action = env.action_space(agent).sample(mask)
    #     env.step(action)

    # env = texas_holdem.env(num_players=6, render_mode="human")
    # env.reset(seed=42)
    #
    # for agent in env.agent_iter():
    #     observation, reward, termination, truncation, info = env.last()
    #
    #     if termination or truncation:
    #         break
    #
    #     mask = observation["action_mask"]
    #     action = env.action_space(agent).sample(mask)  # this is where you would insert your policy
    #
    #     env.step(action)
    # env.close()

    env = gin_rummy.env(render_mode='human')
    env.reset(seed=1)
    #
    for agent in env.agent_iter():
        obs, rew, terms, truncs, info = env.last()
        mask = obs["action_mask"]
        # env.render()
        if terms:
            action = None
        else:
            action = env.action_space(agent).sample(mask)
        env.step(action)


    # for _ in range(10):
    #
    #
    #     env.step
    #




if __name__ == '__main__':
    main()