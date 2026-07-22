---
title: Recording Agents
---

# Recording Agents

## Why Record Your Agent?

Recording agent behavior serves several important purposes in RL development:

**🎥 Visual Understanding**: See exactly what your agent is doing - sometimes a 10-second video reveals issues that hours of staring at reward plots miss.

**📊 Performance Tracking**: Collect systematic data about episode rewards, lengths, and timing to understand training progress.

**🐛 Debugging**: Identify specific failure modes, unusual behaviors, or environments where your agent struggles.

**📈 Evaluation**: Compare different training runs, algorithms, or hyperparameters objectively.

**🎓 Communication**: Share results with collaborators, include in papers, or create educational content.

## When to Record

**During Evaluation** (Record Every Episode):
- Testing a trained agent's final performance
- Creating demonstration videos
- Detailed analysis of specific behaviors

**During Training** (Record Periodically):
- Monitor learning progress over time
- Catch training issues early
- Create timelapse videos of learning

```{eval-rst}
.. py:currentmodule: pettingzoo.utils.wrappers

PettingZoo provides :class:`RecordVideo` for AEC environments and :class:`RecordVideoParallel` for `Parallel` environments. Both wrappers function the same, using the underlying `render()` function of the environment, but `AEC` and `Parallel` environments have different interfaces. They generate MP4 videos from environment renderings. Create the environment with an image-producing render mode such as ``rgb_array`` and install the optional dependency with ``pip install "pettingzoo[other]"``.

We'll show how to record every episode during evaluation and periodically during training using an AEC environment.
```

## Recording Every Episode (Evaluation)

```{eval-rst}
.. py:currentmodule: pettingzoo.utils.wrappers

When evaluating a trained agent, you typically want to record several episodes to understand average performance and consistency. Here is how to use :class:`RecordVideo` with an AEC environment.
```

```python
from pettingzoo.classic import connect_four_v3
from pettingzoo.utils.wrappers import RecordVideo
import numpy as np

# Configuration
num_eval_episodes = 4

# rgb_array is needed for video recording
env = connect_four_v3.env(render_mode="rgb_array")

# Add video recording for every episode
env = RecordVideo(
    env,
    video_folder="connect-four-agent",  # Folder to save videos
    name_prefix="eval",                  # Prefix for video filenames
    episode_trigger=lambda x: True,       # Record every episode
)

print(f"Starting evaluation for {num_eval_episodes} episodes...")
print("Videos will be saved to: connect-four-agent/")

episode_returns = []
episode_lengths = []

for episode_num in range(num_eval_episodes):
    env.reset(seed=episode_num)
    rewards = {agent: 0 for agent in env.possible_agents}
    step_count = 0

    for agent in env.agent_iter():
        observation, reward, termination, truncation, info = env.last()
        rewards[agent] += reward

        if termination or truncation:
            action = None
        else:
            # Replace this with your trained agent's policy.
            action = env.action_space(agent).sample(observation["action_mask"])

        env.step(action)
        step_count += 1

    episode_returns.append(rewards["player_0"])
    episode_lengths.append(step_count)
    print(f"Episode {episode_num + 1}: {step_count} steps, rewards = {rewards}")

env.close()

# Calculate some useful aggregate metrics
avg_reward = np.mean(episode_returns)
avg_length = np.mean(episode_lengths)
std_reward = np.std(episode_returns)

print(f"\nEvaluation Summary:")
print(f"Average player_0 reward: {avg_reward:.2f} ± {std_reward:.2f}")
print(f"Average episode length: {avg_length:.1f} steps")
```

### Understanding the Output

After running this code, you'll find:

**Video Files**: `connect-four-agent/eval-episode-0.mp4`, `eval-episode-1.mp4`, etc.
- Each file shows one complete episode from start to finish
- Useful for seeing exactly how your agents behave
- Can be shared, embedded in presentations, or analyzed frame-by-frame

**Console Output**: Episode-by-episode rewards plus summary statistics
```
Episode 1: 42 steps, rewards = {'player_0': 1, 'player_1': -1}
Episode 2: 38 steps, rewards = {'player_0': -1, 'player_1': 1}

Average player_0 reward: 0.00 ± 1.00
Average episode length: 40.0 steps
```

```{eval-rst}
.. py:currentmodule: pettingzoo.utils.wrappers

In the script above, :class:`RecordVideo` saves videos with filenames like ``eval-episode-0.mp4`` in the specified folder. The ``episode_trigger=lambda x: True`` ensures every episode is recorded. PettingZoo does not include a ``RecordEpisodeStatistics`` wrapper, so the example collects its own per-episode returns and lengths.
```

## Recording During Training (Periodic)

During training, you'll run hundreds or thousands of episodes, so recording every one isn't practical. Instead, record periodically to track learning progress:

```python
import logging

from pettingzoo.classic import connect_four_v3
from pettingzoo.utils.wrappers import RecordVideo

# Training configuration
training_period = 250           # Record video every 250 episodes
num_training_episodes = 10_000  # Total training episodes

# Set up logging for episode statistics
logging.basicConfig(level=logging.INFO, format="%(message)s")

# Create environment with periodic video recording
env = connect_four_v3.env(render_mode="rgb_array")
env = RecordVideo(
    env,
    video_folder="connect-four-training",
    name_prefix="training",
    episode_trigger=lambda x: x % training_period == 0,
)

episode_returns = []
episode_lengths = []

print(f"Starting training for {num_training_episodes} episodes")
print(f"Videos will be recorded every {training_period} episodes")
print("Videos saved to: connect-four-training/")

for episode_num in range(num_training_episodes):
    env.reset()
    episode_return = 0
    step_count = 0

    for agent in env.agent_iter():
        observation, reward, termination, truncation, info = env.last()
        if agent == "player_0":
            episode_return += reward

        if termination or truncation:
            action = None
        else:
            # Replace with your actual training agent.
            action = env.action_space(agent).sample(observation["action_mask"])

        env.step(action)
        step_count += 1

    episode_returns.append(episode_return)
    episode_lengths.append(step_count)
    logging.info(
        f"Episode {episode_num}: reward={episode_return:.1f}, length={step_count}"
    )

    # Additional analysis for milestone episodes
    if episode_num % 1000 == 0:
        recent_rewards = episode_returns[-100:]
        if recent_rewards:
            avg_recent = sum(recent_rewards) / len(recent_rewards)
            print(f"  -> Average reward over last 100 episodes: {avg_recent:.1f}")

env.close()
```

### Training Recording Benefits

**Progress Videos**: Watch your agent improve over time
- `training-episode-0.mp4`: Random initial behavior
- `training-episode-250.mp4`: Some patterns emerging
- `training-episode-500.mp4`: Clear improvement
- `training-episode-1000.mp4`: Competent performance

**Learning Curves**: Plot episode statistics over time
```python
import matplotlib.pyplot as plt

# Plot learning progress
# Use the episode returns collected during training. This sample data keeps the
# plotting example runnable on its own.
episode_returns = [0.0, 0.2, -0.1, 0.5, 0.7, 0.9]
episodes = range(len(episode_returns))
rewards = episode_returns

plt.figure(figsize=(10, 6))
plt.plot(episodes, rewards, alpha=0.3, label="Episode Rewards")

# Add moving average for clearer trend
window = 100
if len(rewards) > window:
    moving_avg = [sum(rewards[i:i+window])/window
                  for i in range(len(rewards)-window+1)]
    plt.plot(range(window-1, len(rewards)), moving_avg,
             label=f"{window}-Episode Moving Average", linewidth=2)

plt.xlabel("Episode")
plt.ylabel("Reward")
plt.title("Learning Progress")
plt.legend()
plt.grid(True, alpha=0.3)
# Use plt.show() or plt.savefig(...) in an interactive training script.
plt.close()
```

## Integration with Experiment Tracking

For more sophisticated projects, integrate your experiment-tracking tool of
choice (such as `wandb`) by logging the episode return, episode length, and paths to the videos created by `RecordVideo`. See the `wandb` example in the [Gymnasium documentation](https://gymnasium.farama.org/introduction/record_agent/#integration-with-experiment-tracking).

## Best Practices Summary

**For Evaluation**:
- Record every episode to get complete performance picture
- Use multiple seeds for statistical significance
- Save both videos and numerical data
- Calculate confidence intervals for metrics

**For Training**:
- Record periodically (every 100-1000 episodes)
- Focus on episode statistics over videos during training
- Use adaptive recording triggers for interesting episodes
- Monitor memory usage for long training runs

**For Analysis**:
- Create moving averages to smooth noisy learning curves
- Look for patterns in both success and failure episodes
- Compare agent behavior at different stages of training
- Save raw data for later analysis and comparison

## More Information

* [Training an agent](train_agent) - Learn how to build the agents you're recording
* [Basic usage](basic_usage) - Understand PettingZoo fundamentals
* {doc}`More training tutorials </tutorials/training_agents/index>` - Advanced training techniques
* [Custom environments](create_custom_env) - Create your own environments to record

Recording agent behavior is an essential skill for RL practitioners. It helps you understand what your agents are actually learning, debug training issues, and communicate results effectively. Start with simple recording setups and gradually add more sophisticated analysis as your projects grow in complexity!
