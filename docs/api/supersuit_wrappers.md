---
title: Supersuit Wrappers
---

# Supersuit Wrappers

PettingZoo include wrappers via the SuperSuit companion package (`pip install supersuit`). These can be applied to both AECEnv and ParallelEnv environments. Using it to convert space invaders to have a grey scale observation space and stack the last 4 frames looks like:

``` python
import gymnasium as gym
from supersuit import color_reduction_v0, frame_stack_v1

env = gym.make('SpaceInvaders-v0')

env = frame_stack_v1(color_reduction_v0(env, 'full'), 4)
```

Similarly, using SuperSuit with PettingZoo environments looks like

``` python
from pettingzoo.butterfly import pistonball_v0
env = pistonball_v0.env()

env = frame_stack_v1(color_reduction_v0(env, 'full'), 4)
```

## Included Functions

Supersuit includes the following wrappers:


```{eval-rst}
.. py:function:: clip_reward_v0(env, lower_bound=-1, upper_bound=1)

  Clips rewards to between lower_bound and upper_bound. This is a popular way of handling rewards with significant variance of magnitude, especially in Atari environments.

.. py:function:: clip_actions_v0(env)

  Clips Box actions to be within the high and low bounds of the action space. This is a standard transformation applied to environments with continuous action spaces to keep the action passed to the environment within the specified bounds.

.. py:function:: color_reduction_v0(env, mode='full')

  Simplifies color information in graphical ((x,y,3) shaped) environments. `mode='full'` fully greyscales of the observation. This can be computationally intensive. Arguments of 'R', 'G' or 'B' just take the corresponding R, G or B color channel from observation. This is much faster and is generally sufficient.

.. py:function:: dtype_v0(env, dtype)

  Recasts your observation as a certain dtype. Many graphical games return `uint8` observations, while neural networks generally want `float16` or `float32`. `dtype` can be anything NumPy would except as a dtype argument (e.g. np.dtype classes or strings).

.. py:function:: flatten_v0(env)

  flattens observations into a 1D array.

.. py:function:: frame_skip_v0(env, num_frames)

  Skips `num_frames` number of frames by reapplying old actions over and over. Observations skipped over are ignored. Rewards skipped over are accumulated. Like Gymnasium Atari's frameskip parameter, `num_frames` can also be a tuple `(min_skip, max_skip)`, which indicates a range of possible skip lengths which are randomly chosen from (in single agent environments only).

.. py:function:: delay_observations_v0(env, delay)

  Delays observation by `delay` frames. Before `delay` frames have been executed, the observation is all zeros. Along with frame_skip, this is the preferred way to implement reaction time for high FPS games.

.. py:function:: sticky_actions_v0(env, repeat_action_probability)

  Assigns a probability of an old action "sticking" to the environment and not updating as requested. This is to prevent agents from learning predefined action patterns in highly deterministic games like Atari. Note that the stickiness is cumulative, so an action has a repeat_action_probability^2 chance of an action sticking for two turns in a row, etc. This is the recommended way of adding randomness to Atari by *"Machado et al. (2018), "Revisiting the Arcade Learning Environment: Evaluation Protocols and Open Problems for General Agents"*

.. py:function:: frame_stack_v1(env, num_frames=4)

  Stacks the most recent frames. For vector games observed via plain vectors (1D arrays), the output is just concatenated to a longer 1D array. 2D or 3D arrays are stacked to be taller 3D arrays. At the start of the game, frames that don't yet exist are filled with 0s. `num_frames=1` is analogous to not using this function.

.. py:function:: max_observation_v0(env, memory)

  The resulting observation becomes the max over `memory` number of prior frames. This is important for Atari environments, as many games have elements that are intermitently flashed on the instead of being constant, due to the peculiarities of the console and CRT TVs. The OpenAI baselines MaxAndSkip Atari wrapper is equivalent to doing `memory=2` and then a  `frame_skip` of 4.

.. py:function:: normalize_obs_v0(env, env_min=0, env_max=1)

  Linearly scales observations to the range `env_min` (default 0) to `env_max` (default 1), given the known minimum and maximum observation values defined in the observation space. Only works on Box observations with float32 or float64 dtypes and finite bounds. If you wish to normalize another type, you can first apply the dtype wrapper to convert your type to float32 or float64.

.. py:function:: reshape_v0(env, shape)

  Reshapes observations into given shape.

.. py:function:: resize_v1(env, x_size, y_size, linear_interp=False)

  Performs interpolation to up-size or down-size observation image using area interpolation by default. Linear interpolation is also available by setting `linear_interp=True` (it's faster and better for up-sizing). This wrapper is only available for 2D or 3D observations, and only makes sense if the observation is an image.

.. py:function:: nan_noop_v0(env)

  If an action is a NaN value for a step, the following wrapper will trigger a warning and perform a no operation action in its place. The noop action is accepted as an argument in the `step(action, no_op_action)` function.

.. py:function:: nan_zeros_v0(env)

  If an action is a NaN value for a step, the following wrapper will trigger a warning and perform a zeros action in its place.

.. py:function:: nan_random_v0(env)

  If an action is a NaN value for a step, the following wrapper will trigger a warning and perform a random action in its place. The random action will be retrieved from the action mask.

.. py:function:: scale_actions_v0(env, scale)

  Scales the high and low bounds of the action space by the `scale` argument in __init__(). Additionally, scales any actions by the same value when step() is called.

```
## Included Multi-Agent Only Functions

```{eval-rst}
.. py:function:: agent_indicator_v0(env, type_only=False)

  Adds an indicator of the agent ID to the observation, only supports discrete and 1D, 2D, and 3D box. For 1d spaces, the agent ID is converted to a 1-hot vector and appended to the observation (increasing the size of the observation space as necessary). 2d and 3d spaces are treated as images (with channels last) and the ID is converted to *n* additional channels with the channel that represents the ID as all 1s and the other channel as all 0s (a sort of one hot encoding). This allows MADRL methods like parameter sharing to learn policies for heterogeneous agents since the policy can tell what agent it's acting on. Set the `type_only` parameter to parse the name of the agent as `<type>_<n>` and have the appended 1-hot vector only identify the type, rather than the specific agent name. This is useful for games where there are many agents in an environment but few types of agents. Agent indication for MADRL was first introduced in *Cooperative Multi-Agent Control Using Deep Reinforcement Learning.*

.. py:function:: black_death_v2(env)

  Instead of removing dead actions, observations and rewards are 0 and actions are ignored. This can simplify handling agent death mechanics. The name "black death" does not come from the plague, but from the fact that you see a black image (an image filled with zeros) when you die.

.. py:function:: pad_action_space_v0(env)

  Pads the action spaces of all agents to be be the same as the biggest, per the algorithm posed in *Parameter Sharing is Surprisingly Useful for Deep Reinforcement Learning*.  This enables MARL methods that require homogeneous action spaces for all agents to work with environments with heterogeneous action spaces. Discrete actions inside the padded region will be set to zero, and Box actions will be cropped down to the original space.

.. py:function:: pad_observations_v0(env)

  Pads observations to be of the shape of the largest observation of any agent with 0s, per the algorithm posed in *Parameter Sharing is Surprisingly Useful for Deep Reinforcement Learning*. This enables MARL methods that require homogeneous observations from all agents to work in environments with heterogeneous observations. This currently supports Discrete and Box observation spaces.
```

[//]: # (## Environment Vectorization)

[//]: # ()
[//]: # (* `concat_vec_envs_v0&#40;vec_env, num_vec_envs, num_cpus=0, base_class='gym'&#41;` takes in an `vec_env` which is vector environment &#40;should not have multithreading enabled&#41;. Creates a new vector environment with `num_vec_envs` copies of that vector environment concatenated together and runs them on `num_cpus` cpus as balanced as possible between cpus. `num_cpus=0` or `num_cpus=1` means to create 0 new threads, i.e. run the process in an efficient single threaded manner. A use case for this function is given below. If the base class of the resulting vector environment matters as it does for stable baselines, you can use the `base_class` parameter to switch between `"gym"` base class and `"stable_baselines3"`'s base class. Note that both have identical functionality.)

[//]: # (### Parallel Environment Vectorization)

[//]: # ()
[//]: # (Note that a multi-agent environment has a similar interface to a vector environment. Give each possible agent an index in the vector and the vector of agents can be interpreted as a vector of "environments":)

[//]: # ()
[//]: # (``` python)

[//]: # (agent_1)

[//]: # (agent_2)

[//]: # (agent_3)

[//]: # (...)

[//]: # (```)

[//]: # ()
[//]: # (Where each agent's observation, reward, done, and info will be that environment's data.)

[//]: # ()
[//]: # (The following function performs this conversion.)

[//]: # ()
[//]: # (* `pettingzoo_env_to_vec_env_v0&#40;env&#41;`: Takes a PettingZoo ParallelEnv with the following assumptions: no agent death or generation, homogeneous action and observation spaces. Returns a gymnasium vector environment where each "environment" in the vector represents one agent. An arbitrary PettingZoo parallel environment can be enforced to have these assumptions by wrapping it with the pad_action_space, pad_observations, and the black_death wrapper&#41;. This conversion to a vector environment can be used to train appropriate pettingzoo environments with standard single agent RL methods such as stable baselines's A2C out of box &#40;example below&#41;.)

[//]: # ()
[//]: # (You can also use the `concat_vec_envs_v0` functionality to train on several vector environments in parallel, forming a vector which looks like)

[//]: # ()
[//]: # (``` python)

[//]: # (env_1_agent_1)

[//]: # (env_1_agent_2)

[//]: # (env_1_agent_3)

[//]: # (env_2_agent_1)

[//]: # (env_2_agent_2)

[//]: # (env_2_agent_3)

[//]: # (...)

[//]: # (```)

[//]: # ()
[//]: # (So you can for example train 4 copies of pettingzoo's pistonball environment in parallel with some code like:)

[//]: # ()
[//]: # (``` python)

[//]: # (from stable_baselines3 import PPO)

[//]: # (from pettingzoo.butterfly import pistonball_v6)

[//]: # (import supersuit as ss)

[//]: # (env = pistonball_v6.parallel_env&#40;&#41;)

[//]: # (env = ss.color_reduction_v0&#40;env, mode='B'&#41;)

[//]: # (env = ss.resize_v1&#40;env, x_size=84, y_size=84&#41;)

[//]: # (env = ss.frame_stack_v1&#40;env, 3&#41;)

[//]: # (env = ss.pettingzoo_env_to_vec_env_v0&#40;env&#41;)

[//]: # (env = ss.concat_vec_envs_v0&#40;env, 8, num_cpus=4, base_class='stable_baselines3'&#41;)

[//]: # (model = PPO&#40;'CnnPolicy', env, verbose=3, n_steps=16&#41;)

[//]: # (model.learn&#40;total_timesteps=2000000&#41;)

[//]: # (```)

[//]: # ()
[//]: # (* `vectorize_aec_env_v0&#40;aec_env, num_envs, num_cpus=0&#41;` creates an AEC Vector env &#40;API documented in source [here]&#40;https://github.com/Farama-Foundation/SuperSuit/blob/master/supersuit/aec_vector/base_aec_vec_env.py&#41;&#41;. `num_cpus=0` indicates that the process will run in a single thread. Values of 1 or more will spawn at most that number of processes.)

[//]: # ()
[//]: # (#### Note on multiprocessing)

[//]: # (Turning on multiprocessing runs each environment in it's own process. Turning this on is typically much slower for fast environments &#40;like card games&#41;, but much faster for slow environments &#40;like robotics simulations&#41;. Determining which case you are will require testing.)

[//]: # ()
[//]: # (On MacOS with python3.8 or higher, you will need to change the default multiprocessing setting to use fork multiprocessing instead of spawn multiprocessing, as shown below, before the multiprocessing environment is created.)

[//]: # ()
[//]: # (``` python)

[//]: # (import multiprocessing)

[//]: # (multiprocessing.set_start_method&#40;"fork"&#41;)

[//]: # (```)

[//]: # ()
[//]: # (## Lambda Functions)

[//]: # ()
[//]: # (If none of the included in micro-wrappers are suitable for your needs, you can use a lambda function &#40;or submit a PR&#41;.)

[//]: # ()
[//]: # (* `action_lambda_v1&#40;env, change_action_fn, change_space_fn&#41;` allows you to define arbitrary changes to the actions via `change_action_fn&#40;action, space&#41; : action` and to the action spaces with `change_space_fn&#40;action_space&#41; : action_space`. Remember that you are transforming the actions received by the wrapper to the actions expected by the base environment. In multi-agent environments only, the lambda functions can optionally accept an extra `agent` parameter, which lets you know the agent name of the action/action space, e.g. `change_action_fn&#40;action, space, agent&#41; : action`.)

[//]: # ()
[//]: # (* `observation_lambda_v0&#40;env, observation_fn, observation_space_fn&#41;` allows you to define arbitrary changes to the via `observation_fn&#40;observation, obs_space&#41; : observation`, and `observation_space_fn&#40;obs_space&#41; : obs_space`. For Box-Box transformations the space transformation will be inferred from `change_observation_fn` if `change_obs_space_fn=None` by passing the `high` and `low` bounds through the `observation_space_fn`. In multi-agent environments only, the lambda functions can optionally accept an `agent` parameter, which lets you know the agent name of the observation/observation space, e.g. `observation_fn&#40;observation, obs_space, agent&#41; : observation`.)

[//]: # ()
[//]: # (* `reward_lambda_v0&#40;env, change_reward_fn&#41;` allows you to make arbitrary changes to rewards by passing in a `change_reward_fn&#40;reward&#41; : reward` function. For Gymnasium environments this is called every step to transform the returned reward. For AECEnv, this function is used to change each element in the rewards dictionary every step.)

[//]: # ()
[//]: # (### Lambda Function Examples)

[//]: # ()
[//]: # (Adding noise to a Box observation looks like:)

[//]: # ()
[//]: # (``` python)

[//]: # (env = observation_lambda_v0&#40;env, lambda x : x + np.random.normal&#40;size=x.shape&#41;&#41;)

[//]: # (```)

[//]: # ()
[//]: # (Adding noise to a box observation and increasing the high and low bounds to accommodate this extra noise looks like:)

[//]: # ()
[//]: # (``` python)

[//]: # (env = observation_lambda_v0&#40;env,)

[//]: # (    lambda x : x + np.random.normal&#40;size=x.shape&#41;,)

[//]: # (    lambda obs_space : gym.spaces.Box&#40;obs_space.low-5,obs_space.high+5&#41;&#41;)

[//]: # (```)

[//]: # ()
[//]: # (Changing 1d box action space to a Discrete space by mapping the discrete actions to one-hot vectors looks like:)

[//]: # ()
[//]: # (``` python)

[//]: # (def one_hot&#40;x,n&#41;:)

[//]: # (    v = np.zeros&#40;n&#41;)

[//]: # (    v[x] = 1)

[//]: # (    return v)

[//]: # ()
[//]: # (env = action_lambda_v1&#40;env,)

[//]: # (    lambda action, act_space : one_hot&#40;action, act_space.shape[0]&#41;,)

[//]: # (    lambda act_space : gym.spaces.Discrete&#40;act_space.shape[0]&#41;&#41;)

[//]: # (```)

[//]: # ()
[//]: # (Note that many of the supersuit wrappers are implemented with a lambda wrapper behind the scenes. See [here]&#40;https://github.com/Farama-Foundation/SuperSuit/blob/master/supersuit/generic_wrappers/basic_wrappers.py&#41; for some examples.)

## Citation

If you use this in your research, please cite:

```
@article{SuperSuit,
  Title = {SuperSuit: Simple Microwrappers for Reinforcement Learning Environments},
  Author = {Terry, J K and Black, Benjamin and Hari, Ananth},
  journal={arXiv preprint arXiv:2008.08932},
  year={2020}
}
```
