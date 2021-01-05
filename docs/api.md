# API

## Initializing Environments

Using environments in PettingZoo is very similar to using them in OpenAI's Gym. You initialize an environment via:

```python
from pettingzoo.butterfly import pistonball_v1
env = pistonball_v1.env()
```

Environments are generally highly configurable via arguments at creation, i.e.:

```python
cooperative_pong.env(ball_speed=18, left_paddle_speed=25,
right_paddle_speed=25, is_cake_paddle=True, max_cycles=900, bounce_randomness=False)
```

## Interacting with Environments

Environments can be interacted with using a similar interface to Gym:

```python
env.reset()
for agent in env.agent_iter():
    observation, reward, done, info = env.last()
    action = policy(observation, agent)
    env.step(action)
```

The commonly used methods are:

`agent_iter(max_iter=2**63)` returns an iterator that yields the current agent of the environment. It terminates when all agents in the environment are done or when `max_iter` (steps have been executed).

`last(observe=True)` returns observation, reward, done, and info for the agent currently able to act. The returned reward is the cumulative reward that the agent has received since it last acted. If `observe` is set to False, the observation will not be computed, and None will be returned in its place. Note that a single agent being done does not imply the environment is done.

`reset()` resets the environment and sets it up for use when called the first time.

`step(action)` takes and executes the action of the agent in the environment, automatically switches control to the next agent.

## Additional Environment API

PettingZoo models games as *Agent Environment Cycle* (AEC) games, and thus can support any game multi-agent RL can consider, allowing for fantastically weird cases. Because of this, our API includes lower level functions and attributes that you probably won't need but are very important when you do. Their functionality is used to implement the high-level functions above though, so including them is just a matter of code factoring.

`agents`: A list of the names of all current agents, typically integers. These may be changed as an environment progresses (i.e. agents can be added or removed).

`possible_agents`: A list of all possible_agents the environment could generate. Equivalent to the list of agents in the observation and action spaces. This cannot be changed through play or reseting.

`agent_selection` an attribute of the environment corresponding to the currently selected agent that an action can be taken for.

`observation_spaces`: A dict of the observation spaces of every agent, keyed by name. This cannot be changed through play or reseting.

`action_spaces`: A dict of the action spaces of every agent, keyed by name. This cannot be changed through play or reseting.

`dones`: A dict of the done state of every current agent at the time called, keyed by name. `last()` accesses this attribute. Note that agents can be added or removed from this dict. The returned dict looks like:

`dones = {0:[first agent's done state], 1:[second agent's done state] ... n-1:[nth agent's done state]}`

`infos`: A dict of info for each current agent, keyed by name. Each agent's info is also a dict. Note that agents can be added or removed from this attribute. `last()` accesses this attribute. The returned dict looks like:

`infos = {0:[first agent's info], 1:[second agent's info] ... n-1:[nth agent's info]}`

`observe(agent)`: Returns the observation an agent currently can make. `last()` calls this function.

`rewards`: A dict of the rewards of every current agent at the time called, keyed by name. Rewards the instantaneous reward generated after the last step. Note that agents can be added or removed from this attribute. `last()` does not directly access this attribute, rather the returned reward is stored in an internal variable. The rewards structure looks like:

`{0:[first agent's reward], 1:[second agent's reward] ... n-1:[nth agent's reward]}`

`seed(seed=None)`: Reseeds the environment. `reset()` must be called after `seed()`, and before `step()`.

`render(mode='human')`: Displays a rendered frame from the environment, if supported. Environments may support different render modes.

`close()`: Closes the rendering window.


## Noteable Idioms

### Checking if the entire environment is done

When an agent is done, it's removed from `agents`, so when the environments done `agents` will be an empty list. This means `not env.agents` is a simple condition for the environment being done

### Variable Numbers of Agents (Death)

Agents can die and generate during the course of an environment. If an agent dies, then its entry in the `dones` dictionary is set to `True`, it become the next selected agent (or after another agent that is also done), and the action it takes is required to be `None`. After this vacuous step is taken, the agent will be removed from `agents` and other changeable attributes. Agent generation can just be done with appending it to `agents` and the other changeable attributes (with it already being in the possible agents and action/observation spaces), and transitioning to it at some point with agent_iter.

### Number of agents

You can get the number of agents with `len(env.agents)`, and the maximum possible number of agents with `len(env.possible_agents)`.

### Environment as agent

In certain cases, separating agent from environment actions is helpful for studying. This can be done by treating the environment as an agent. We encourage calling the environment actor `env` in env.agents, and having it take `None` as an action.


## Raw Environments

Environments are by default wrapped in a handful of lightweight wrappers that handle error messages and ensure reasonable behavior given incorrect usage (i.e. playing illegal moves or stepping before resetting). However, these add a very small amount of overhead. If you want to create an environment without them, you can do so by using the `raw_env()` constructor contained within each module:

```python
env = prospector_v3.raw_env(<environment parameters>)
```

## Parallel API

In addition to the main API, we have a secondary parallel API for environments where all agents have simultaneous actions and observations. An environment with parallel API support can be created via `<game>.parallel_env()`. This API is based around the paradigm of *Partially Observable Stochastic Games* (POSGs) and the details are similar to [RLLib's MultiAgent environment specification](https://docs.ray.io/en/latest/rllib-env.html#multi-agent-and-hierarchical), except we allow for different observation and action spaces between the agents.

### Example Usage

Environments can be interacted with as follows:

```python
parallel_env = pistonball_v1.parallel_env()
observations = parallel_env.reset()
max_cycles = 500
for step in range(max_cycles):
    actions = {agent: policy(observations[agent], agent) for agent in parallel_env.agents}
    observations, rewards, dones, infos = parallel_env.step(actions)
```

### Full API

`agents`, `num_agents`, `observation_spaces`, and `action_spaces` attributes are available and are as described above in the main API description.

`render(mode='human')`, `seed(seed=None)`, `close()` are methods as described above in the main API description.

`step(actions)`: receives a dictionary of actions keyed by the agent name. Returns the observation dictionary, reward dictionary, done dictionary, and info dictionary, where each dictionary is keyed by the agent.

`reset()`: resets the environment and returns a dictionary of observations (keyed by the agent name)

## SuperSuit

[SuperSuit](https://github.com/PettingZoo-Team/SuperSuit) contains nice wrappers to do common preprocessing actions, like frame stacking or changing RGB observations to greyscale. It also supports Gym environments, in addition to PettingZoo.

## Utils

### Manual Control

Often, you want to be able to play before trying to learn it to get a better feel for it. Some of our games directly support this:

```python
from pettingzoo.butterfly import prison_v2
prison_v2.manual_control(<environment parameters>)
```

Environments say if they support this functionality in their documentation, and what the specific controls are.

### Random Demo

You can also easily get a quick impression of them by watching a random policy control all the actions:

```python
from pettingzoo.utils import random_demo
random_demo(env, render=True, cycles=100000000)
```

### Observation Saving

If the agents in a game make observations that are images then the observations can be saved to an image file. This function takes in the environment, along with a specified agent. If no `agent` is specified, then the current selected agent for the environment is chosen. If `all_agents` is passed in as `True`, then the observations of all agents in the environment is saved. By default, the images are saved to the current working directory in a folder matching the environment name. The saved image will match the name of the observing agent. If `save_dir` is passed in, a new folder is created where images will be saved to.

```python
from pettingzoo.utils import save_observation
save_observation(env, agent=agent, all_agents=False, save_dir=os.getcwd())
save_observation(env, agent=None, all_agents=False, save_dir=os.getcwd())
save_observation(env, agent=None, all_agents=True, save_dir=os.getcwd())
```

The first function will save the current observation for the specified agent. The second function will save the current observation based on the currently selected agent. The last function will save the current observations of all agents in the environment.
