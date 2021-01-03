import pytest
from pettingzoo.test.all_modules import all_environments
import pettingzoo.test.api_test as api_test
from collections import Counter, defaultdict
import os
import multiprocessing
import json
import importlib
import random

def unique(list):
    uniques = []
    for i in list:
        if i not in uniques:
            uniques.append(i)
    return uniques
from pettingzoo.utils import random_demo

all_env_rewards = []

class ValueMapper:
    def __init__(self, agents):
        self.agents = agents
        self.rewards = {agent:0 for agent in agents}
    def add(self, agent, rew):
        self.rewards[agent] += rew
    def get(self):
        return self.rewards
    def summarize(self):
        agent_reward = defaultdict(int)
        for agent in self.agents:
            agent_type = agent[:agent.index("_")]
            agent_reward[agent_type] += self.rewards[agent]
        return agent_reward
    def total(self):
        return sum(self.rewards.values())

def compute(values, count):
    result = {}
    for type in values:
        result[type] = values[type] / count
    return result


def exec_env(input):
    name = input
    # if not("pistonball" in name):# or "butterfly" in name or name == "mpe/simple_spread" or name == "mpe/simple_speaker_listener" or name == "mpe/simple_reference" or name == "atari/entombed_cooperative" or name == "classic/hanabi"):
    #     return
    #envname = os.path.basename(module.__file__)[:-3]
    module = all_environments[name]
    envname =  os.path.basename(module.__file__)[:-3]
    env = module.env()
    env.reset()
    #print(name,": ",env.observation_spaces[env.agent_selection])
    # env = #(n_pursuers=n_pursuers)

    total_reward = ValueMapper(env.agents)
    abs_reward = ValueMapper(env.agents)
    non_zero_rewards = ValueMapper(env.agents)

    episode_lens = []

    # force_reset_len = 2000//10
    num_steps_total = 10000
    ep_len = 0
    print("env started")

    # start = time.time()
    env.reset()
    tot_rew = 0
    tot_steps = 0
    while tot_steps < num_steps_total:
        for agent in env.agent_iter():
            obs, reward, done, _ = env.last(observe=False)
            total_reward.add(agent, reward)
            tot_rew = tot_rew + abs(float(reward))
            # print(tot_rew)
            abs_reward.add(agent, abs(reward))
            non_zero_rewards.add(agent, int(reward != 0))

            if done:
                action = None
            elif 'legal_moves' in env.infos[agent]:
                action = random.choice(env.infos[agent]['legal_moves'])
            else:
                action = env.action_spaces[agent].sample()
            env.step(action)
            ep_len += 1
            tot_steps += 1

        episode_lens.append(ep_len)
        ep_len = 0
        # print("reset")
        # print(total_reward.total()/(y+1))
        # print(tot_rew)
        # for agent, reward in env.rewards.items():
        #     total_reward.add(agent, reward)
        #     abs_reward.add(agent, abs(reward))
        #     non_zero_rewards.add(agent, int(reward != 0))
        env.reset()


    num_episodes = len(episode_lens)
    num_steps = tot_steps
    print(envname,total_reward.total()/ num_episodes)
    ep_len = sum(episode_lens)/len(episode_lens)

    return envname,{
        "avg_episode_len":ep_len,
        "average_total_reward": total_reward.total()/ num_episodes,
        "all_mean_rewards":total_reward.total()/ num_steps,
        "all_mean_abs_rewards":abs_reward.total()/ num_steps,
        "all_prop_non_zero":non_zero_rewards.total()/ num_steps,
        "mean_rewards":compute(total_reward.summarize(), num_steps),
        "mean_abs_rewards":compute(abs_reward.summarize(), num_steps),
        "prop_non_zero":compute(non_zero_rewards.summarize(), num_steps),
        "mean_rewards_full":compute(total_reward.get(), num_steps),
        "mean_abs_rewards_full":compute(abs_reward.get(), num_steps),
        "prop_non_zero_full":compute(non_zero_rewards.get(), num_steps),
        }


inputs = list(sorted(all_environments.keys()))
pool = multiprocessing.Pool(multiprocessing.cpu_count())
all_env_rewards = pool.map(exec_env, inputs)
#all_env_rewards = [exec_env(input) for input in inputs ]
all_env_rewards = [rew for rew in all_env_rewards if rew is not None]
print(all_env_rewards)
all_env_dict = dict(all_env_rewards)

with open("env_rewards.csv",'w') as file:
    pretty_print = json.dumps(all_env_dict, sort_keys=True, indent=2, separators=(',', ': '))
    file.write(pretty_print)
