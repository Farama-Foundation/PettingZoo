import numpy as np
from .cooperative_pong import env as _env
import pygame
from pettingzoo.utils import save_image_observation
from pettingzoo.utils import wrapper

def manual_control(**kwargs):
    env = _env(**kwargs)
    env = wrapper(env, color_reduction='B', down_scale=(10, 10), range_scale=(0, 255), new_dtype=np.float32, frame_stacking=4)
    env.reset(observe=True)

    # Use save_observation to save a dictionary of observations
    for i in range(2):
        obs = env.step(0)
        agent = env.agent_selection
        save_image_observation(obs, frame_stacking=env.frame_stacking, pre_fs_ndim=env.pre_fs_ndim[agent], reverse_colors=False)
    exit()
    
    quit_loop = 0

    # Fixed: Key held down will generate multiple events
    pygame.key.set_repeat(20, 0)
    
    total_reward = 0
    initial_iteration = {agent: True for agent in env.agents}
    dones = {agent: False for agent in env.agents}
    done = all(dones.values())
    
    while not done:
    
        action_dict = {agent: 0 for agent in env.agents}  # do nothing
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_loop = 1
                break
            elif event.type == pygame.KEYDOWN:
                # Quit if ESC is pressed
                if event.key == pygame.K_ESCAPE:
                    quit_loop = 1
                    break
                if event.key == pygame.K_BACKSPACE:
                    env.reset()
                    total_reward = 0
                if event.key == pygame.K_w:
                    # player1.moveup()
                    action_dict[0] = 1
                if event.key == pygame.K_s:
                    # player1.movedown()
                    action_dict[0] = 2
                if event.key == pygame.K_UP:
                    # player2.moveup()
                    action_dict[1] = 1
                if event.key == pygame.K_DOWN:
                    # player2.movedown()
                    action_dict[1] = 2
        if quit_loop:
            break
    
        for _ in env.agents:
            agent = env.agent_selection
            if not dones[agent]:
                if not initial_iteration[agent]:
                    reward, dones[agent], _ = env.last_cycle()
                    total_reward += reward
                    print("step reward for agent {} is {} done: {}".format(agent, reward, dones[agent]))
                initial_iteration[agent] = False
                env.step(action_dict[agent], observe=False)
        done = all(dones.values())
        if done:
            print("Total reward", total_reward, "done", done)

        env.render()
        pygame.event.pump()
        # env.plot_obs(observation, "obs")
        # break
    
    # assert (total_reward == env.env.score), "Final score = {} and reward = {} are not the same".format(total_reward, env.env.score)
    print("Final reward is {0:.2f}".format(total_reward))
    # Uncomment next line to print FPS at which the game runs
    # print("fps = ", env.env.clock.get_fps())
    
    # pygame.time.wait(3000)
    env.close()
