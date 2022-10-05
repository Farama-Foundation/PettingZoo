import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions.categorical import Categorical

from pettingzoo.butterfly import cooperative_pong_v5
from supersuit import color_reduction_v0, resize_v1, frame_stack_v1


class Agent(nn.Module):
    def __init__(self, num_actions):
        super().__init__()

        self.network = nn.Sequential(
            self.layer_init(nn.Conv2d(4, 32, 3, padding=1)),
            nn.MaxPool2d(2),
            nn.ReLU(),
            self.layer_init(nn.Conv2d(32, 64, 3, padding=1)),
            nn.MaxPool2d(2),
            nn.ReLU(),
            self.layer_init(nn.Conv2d(64, 128, 3, padding=1)),
            nn.MaxPool2d(2),
            nn.ReLU(),
            nn.Flatten(),
            self.layer_init(nn.Linear(128 * 4 * 4, 512)),
            nn.ReLU(),
        )
        self.actor = self.layer_init(nn.Linear(512, num_actions), std=0.01)
        self.critic = self.layer_init(nn.Linear(512, 1))

    def layer_init(self, layer, std=np.sqrt(2), bias_const=0.0):
        torch.nn.init.orthogonal_(layer.weight, std)
        torch.nn.init.constant_(layer.bias, bias_const)
        return layer

    def get_value(self, x):
        return self.critic(self.network(x / 255.0))

    def get_action_and_value(self, x, action=None):
        hidden = self.network(x / 255.0)
        logits = self.actor(hidden)
        probs = Categorical(logits=logits)
        if action is None:
            action = probs.sample()
        return action, probs.log_prob(action), probs.entropy(), self.critic(hidden)


def batchify_obs(obs, device):
    """Converts PZ style observations to batch of torch arrays"""
    # convert to list of np arrays
    obs = np.stack([obs[a] for a in env.possible_agents], axis=0)
    # transpose to be (batch, channel, height, width)
    obs = obs.transpose(0, -1, 1, 2)
    # convert to torch
    obs = torch.tensor(obs).to(device)

    return obs


def batchify(x, device):
    """Converts PZ style returns to batch of torch arrays"""
    # convert to list of np arrays
    x = np.stack([x[a] for a in env.possible_agents], axis=0)
    # convert to torch
    x = torch.tensor(x).to(device)

    return x


def unbatchify(x, env):
    """Converts np array to PZ style arguments"""
    x = x.cpu().numpy()
    x = {a: x[i] for i, a in enumerate(env.possible_agents)}

    return x


if __name__ == "__main__":

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    """ ENV SETUP """
    env = cooperative_pong_v5.parallel_env()
    env = color_reduction_v0(env)
    env = resize_v1(env, 32, 32)
    env = frame_stack_v1(env, stack_size=4)
    num_agents = len(env.possible_agents)
    num_actions = env.action_space(env.possible_agents[0]).n
    observation_size = env.observation_space((env.possible_agents[0])).shape

    """ LEARNER SETUP """
    agent = Agent(num_actions=num_actions).to(device)
    optimizer = optim.Adam(agent.parameters(), lr=0.001, eps=1e-5)

    """ ALGO PARAMS """
    ent_coef = 0.1
    vf_coef = 0.1
    clip_coef = 0.1
    gamma = 0.99
    batch_size = 32

    """ ALGO LOGIC: EPISODE STORAGE"""
    num_steps = 900
    end_step = 0
    total_episodic_return = 0
    rb_obs = torch.zeros((num_steps, num_agents, 4, 32, 32)).to(device)
    rb_actions = torch.zeros((num_steps, num_agents)).to(device)
    rb_logprobs = torch.zeros((num_steps, num_agents)).to(device)
    rb_rewards = torch.zeros((num_steps, num_agents)).to(device)
    rb_terms = torch.zeros((num_steps, num_agents)).to(device)
    rb_values = torch.zeros((num_steps, num_agents)).to(device)

    """ TRAINING LOGIC """
    # train for n number of episodes
    for episode in range(1, 1000):

        # collect observations and convert to batch of torch tensors
        next_obs = batchify_obs(env.reset(seed=None), device)
        # get next dones and convert to batch of torch tensors
        next_dones = torch.zeros(num_agents).to(device)
        # reset the episodic return
        total_episodic_return = 0

        # each episode has num_steps
        for step in range(0, num_steps):
            # store the observation and done
            rb_obs[step] = next_obs
            rb_terms[step] = next_dones

            # ALGO LOGIC: action logic
            with torch.no_grad():
                actions, logprobs, _, values = agent.get_action_and_value(next_obs)
                rb_values[step] = values.flatten()
                rb_actions[step] = actions
                rb_logprobs[step] = logprobs

            # execute the environment and log data
            next_obs, rewards, terms, truncs, infos = env.step(unbatchify(actions, env))
            next_obs = batchify_obs(next_obs, device)
            rewards = batchify(rewards, device)
            terms = batchify(terms, device)
            truncs = batchify(truncs, device)
            rb_rewards[step] = rewards
            total_episodic_return += rewards.cpu().numpy()

            # if we reach termination or truncation, end
            if any(terms) or any(truncs):
                end_step = step
                break

        # bootstrap value if not done
        with torch.no_grad():
            rb_advantages = torch.zeros_like(rb_rewards).to(device)
            for t in reversed(range(end_step + 1)):
                next_V = rb_values[t]
                delta = rb_rewards[t] + gamma * rb_values[t + 1] - rb_values[t]
                rb_advantages[t] = delta + gamma * gamma * rb_advantages[t + 1]
            rb_returns = rb_advantages + rb_values

        # convert our episodes to individual transitions
        b_obs = torch.flatten(rb_obs[:end_step], start_dim=0, end_dim=1)
        b_logprobs = torch.flatten(rb_logprobs[:end_step], start_dim=0, end_dim=1)
        b_actions = torch.flatten(rb_actions[:end_step], start_dim=0, end_dim=1)
        b_returns = torch.flatten(rb_returns[:end_step], start_dim=0, end_dim=1)
        b_values = torch.flatten(rb_values[:end_step], start_dim=0, end_dim=1)
        b_advantages = torch.flatten(rb_advantages[:end_step], start_dim=0, end_dim=1)

        # Optimizing the policy and value network
        b_index = np.arange(len(b_obs))
        clip_fracs = []
        for repeat in range(3):
            np.random.shuffle(b_index)
            for start in range(0, len(b_obs), batch_size):
                end = start + batch_size
                batch_index = b_index[start:end]

                _, newlogprob, entropy, newvalue = agent.get_action_and_value(
                    b_obs[batch_index], b_actions.long()[batch_index]
                )
                logratio = newlogprob - b_logprobs[batch_index]
                ratio = logratio.exp()

                with torch.no_grad():
                    # calculate approx_kl http://joschu.net/blog/kl-approx.html
                    old_approx_kl = (-logratio).mean()
                    approx_kl = ((ratio - 1) - logratio).mean()
                    clip_fracs += [
                        ((ratio - 1.0).abs() > clip_coef).float().mean().item()
                    ]

                # Policy loss
                pg_loss1 = -b_advantages[batch_index] * ratio
                pg_loss2 = -b_advantages[batch_index] * torch.clamp(
                    ratio, 1 - clip_coef, 1 + clip_coef
                )
                pg_loss = torch.max(pg_loss1, pg_loss2).mean()

                # Value loss
                v_loss_unclipped = (newvalue - b_returns[batch_index]) ** 2
                v_clipped = b_values[batch_index] + torch.clamp(
                    newvalue - b_values[batch_index],
                    -clip_coef,
                    clip_coef,
                )
                v_loss_clipped = (v_clipped - b_returns[batch_index]) ** 2
                v_loss_max = torch.max(v_loss_unclipped, v_loss_clipped)
                v_loss = 0.5 * v_loss_max.mean()

                entropy_loss = entropy.mean()
                loss = pg_loss - ent_coef * entropy_loss + v_loss * vf_coef

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

        y_pred, y_true = b_values.cpu().numpy(), b_returns.cpu().numpy()
        var_y = np.var(y_true)
        explained_var = np.nan if var_y == 0 else 1 - np.var(y_true - y_pred) / var_y

        print(f"Training episode {episode}")
        print(f"Episodic Return: {np.mean(total_episodic_return)}")
        print(f"Episode Length: {end_step}")
        print("")
        print(f"Value Loss: {v_loss.item()}")
        print(f"Policy Loss: {pg_loss.item()}")
        print(f"Old Approx KL: {old_approx_kl.item()}")
        print(f"Approx KL: {approx_kl.item()}")
        print(f"Clip Fraction: {np.mean(clip_fracs)}")
        print(f"Explained Variance: {explained_var.item()}")
        print("\n-------------------------------------------\n")
