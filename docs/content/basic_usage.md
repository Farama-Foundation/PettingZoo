---
title: API
---
# Basic Usage

## Initializing Environments

Using environments in PettingZoo is very similar to using them in Gymnasium. You initialize an environment via:

``` python
from pettingzoo.butterfly import pistonball_v6
env = pistonball_v6.env()
```

Environments are generally highly configurable via arguments at creation, i.e.:

``` python
cooperative_pong.env(ball_speed=18, left_paddle_speed=25,
right_paddle_speed=25, is_cake_paddle=True, max_cycles=900, bounce_randomness=False)
```

## Interacting With Environments

Environments can be interacted with using a similar interface to Gymnasium:

``` python
env.reset()
for agent in env.agent_iter():
    observation, reward, termination, truncation, info = env.last()
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

`num_agents`: The length of the agents list.

`agent_selection` an attribute of the environment corresponding to the currently selected agent that an action can be taken for.

`observation_space(agent)` a function that retrieves the observation space for a particular agent. This space should never change for a particular agent ID.

`action_space(agent)` a function that retrieves the action space for a particular agent. This space should never change for a particular agent ID.

`terminations`: A dict of the termination state of every current agent at the time called, keyed by name. `last()` accesses this attribute. Note that agents can be added or removed from this dict. The returned dict looks like:

`terminations = {0:[first agent's termination state], 1:[second agent's termination state] ... n-1:[nth agent's termination state]}`

`truncations`: A dict of the truncation state of every current agent at the time called, keyed by name. `last()` accesses this attribute. Note that agents can be added or removed from this dict. The returned dict looks like:

`truncations = {0:[first agent's truncation state], 1:[second agent's truncation state] ... n-1:[nth agent's truncation state]}`

`infos`: A dict of info for each current agent, keyed by name. Each agent's info is also a dict. Note that agents can be added or removed from this attribute. `last()` accesses this attribute. The returned dict looks like:

`infos = {0:[first agent's info], 1:[second agent's info] ... n-1:[nth agent's info]}`

`observe(agent)`: Returns the observation an agent currently can make. `last()` calls this function.

`rewards`: A dict of the rewards of every current agent at the time called, keyed by name. Rewards the instantaneous reward generated after the last step. Note that agents can be added or removed from this attribute. `last()` does not directly access this attribute, rather the returned reward is stored in an internal variable. The rewards structure looks like:

`{0:[first agent's reward], 1:[second agent's reward] ... n-1:[nth agent's reward]}`

`seed(seed=None)`: Reseeds the environment. `reset()` must be called after `seed()`, and before `step()`.

`render()`: Returns a rendered frame from the environment using render mode specified at initialization. In the case render mode is`'rgb_array'`, returns a numpy array, while with `'ansi'` returns the strings printed. There is no need to call `render()` with `human` mode.

`close()`: Closes the rendering window.

### Optional API Components

While not required by the base API, most downstream wrappers and utilities depend on the following attributes and methods, and they should be added to new environments except in special circumstances where adding one or more is not possible.

`possible_agents`: A list of all possible_agents the environment could generate. Equivalent to the list of agents in the observation and action spaces. This cannot be changed through play or resetting.

`max_num_agents`: The length of the possible_agents list.

`observation_spaces`: A dict of the observation spaces of every agent, keyed by name. This cannot be changed through play or resetting.

`action_spaces`: A dict of the action spaces of every agent, keyed by name. This cannot be changed through play or resetting.

`state()`: Returns a global observation of the current state of the environment. Not all environments will support this feature.

`state_space`: The space of a global observation of the environment. Not all environments will support this feature.

## Notable Idioms

### Checking if the entire environment is done

When an agent is terminated or truncated, it's removed from `agents`, so when the environments done `agents` will be an empty list. This means `not env.agents` is a simple condition for the environment being done.

### Unwrapping an environment

If you have a wrapped environment, and you want to get the unwrapped environment underneath all the layers of wrappers (so that you can manually call a function or change some underlying aspect of the environment), you can use the `.unwrapped` attribute. If the environment is already a base environment, the `.unwrapped` attribute will just return itself.

``` python
base_env = knights_archers_zombies_v10.env().unwrapped
```

### Variable Numbers of Agents (Death)

Agents can die and generate during the course of an environment. If an agent dies, then its entry in the `terminated` dictionary is set to `True`, it become the next selected agent (or after another agent that is also terminated or truncated), and the action it takes is required to be `None`. After this vacuous step is taken, the agent will be removed from `agents` and other changeable attributes. Agent generation can just be done with appending it to `agents` and the other changeable attributes (with it already being in the possible agents and action/observation spaces), and transitioning to it at some point with agent_iter.

### Environment as an Agent

In certain cases, separating agent from environment actions is helpful for studying. This can be done by treating the environment as an agent. We encourage calling the environment actor `env` in env.agents, and having it take `None` as an action.


## Raw Environments

Environments are by default wrapped in a handful of lightweight wrappers that handle error messages and ensure reasonable behavior given incorrect usage (i.e. playing illegal moves or stepping before resetting). However, these add a very small amount of overhead. If you want to create an environment without them, you can do so by using the `raw_env()` constructor contained within each module:

``` python
env = knights_archers_zombies_v10.raw_env(<environment parameters>)
```
