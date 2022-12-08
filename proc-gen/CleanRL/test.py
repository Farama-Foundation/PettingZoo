from collections import deque
import time
import random
import gym
import torch
from rich import print
import supersuit
from pettingzoo.atari import space_invaders_v1

from stable_baselines3.common.atari_wrappers import (  # isort:skip
    ClipRewardEnv,
    EpisodicLifeEnv,
    FireResetEnv,
    MaxAndSkipEnv,
    NoopResetEnv,
)

def evaluate(args, agent):
    iter_start = time.time()
    run_name = f"{args.env_id}__{args.exp_name}__{args.seed}__{int(time.time())}"
    envs = gym.vector.SyncVectorEnv(
        [create_env(args.env_id, args.seed + i, i, args.capture_video, run_name) for i in range(args.num_envs)]
    )
    #agent.q_policy.eval()    # Set online network to evaluation mode
    device = torch.device("cuda" if torch.cuda.is_available() and args.cuda else "cpu")
    states = envs.reset()
    next_obs = torch.Tensor(envs.reset()).to(device)
    eval_episodes = args.eval_episodes
    eval_rewards = deque(maxlen=eval_episodes) 
    print('Running evaluation for {} episodes'.format(eval_episodes))
    while len(eval_rewards) < eval_episodes:   
        # compute actions to take in all parallel envs, asynchronously start environment step
        #actions = agent.act(states, eps=0) # setting eps to 0 to disable exploration
        actions, logprob, _, value = agent.get_action_and_value(next_obs)
        envs.step_async(actions)       
        states, _, _, infos = envs.step_wait() # wait till all parallel envs have stepped
        for info in infos:
            if 'episode' in info.keys():    # if an episode has finished, get episode returns
                episode_metrics = info['episode']
                eval_rewards.append(episode_metrics['r'])

    envs.close()
    iter_end = time.time() - iter_start
    print('Finished evaluation in {:.2f} seconds'.format(iter_end))
    
    return eval_rewards

def create_env(env_id, seed, idx, capture_video, run_name):
    if(env_id == "ALE/SpaceInvaders-v5"):
        game_mode = random.randint(1, 15)
        game_diff = random.randint(0, 1)
    elif(env_id == "ALE/Asteroids-v5"):
        game_mode = random.randint(1, 31)
        game_diff = 0 
    elif(env_id == "ALE/DoubleDunk-v5"):
        game_mode = random.randint(1, 15)
        game_diff = 0 
    def thunk():
        env = gym.make(env_id, mode=game_mode, difficulty=game_diff)
        env = gym.wrappers.RecordEpisodeStatistics(env)
        if capture_video:
            if idx == 0:
                env = gym.wrappers.RecordVideo(env, f"videos/{run_name}")
        env = NoopResetEnv(env, noop_max=30)
        env = MaxAndSkipEnv(env, skip=4)
        env = EpisodicLifeEnv(env)
        if "FIRE" in env.unwrapped.get_action_meanings():
            env = FireResetEnv(env)
        env = ClipRewardEnv(env)
        env = gym.wrappers.ResizeObservation(env, (84, 84))
        env = gym.wrappers.GrayScaleObservation(env)
        env = gym.wrappers.FrameStack(env, 4)
        env.seed(seed)
        env.action_space.seed(seed)
        env.observation_space.seed(seed)
        return env

    return thunk

