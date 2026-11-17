---
title: "Tutorial: Environment Logic"
---

# Tutorial: Environment Logic

## Introduction

Now that we have a basic understanding of the structure of environment repositories, we can start thinking about the fun part - environment logic!

For this tutorial, we will be creating a two-player game consisting of a prisoner, trying to escape, and a guard, trying to catch the prisoner. This game will be played on a 7x7 grid, where:
- The prisoner starts in the top left corner,
- The guard starts in the bottom right corner,
- The escape door is randomly placed in the middle of the grid
- Both the prisoner and the guard can move in any of the four cardinal directions (up, down, left, right).

## Code

```{eval-rst}
.. literalinclude:: ../../../tutorials/CustomEnvironment/tutorial2_adding_game_logic.py
   :language: python
   :caption: /custom-environment/env/custom_environment.py
```


## Parallel and AEC environments

The example above implements a `ParallelEnv`. Its `step(actions)` accepts
actions for all active agents and returns the observations, rewards,
terminations, truncations, and infos together. When this game finishes, it
sets `self.agents = []`. It does **not** use the AEC-specific agent selector,
dead steps, or cumulative reward bookkeeping.

An `AECEnv` instead processes **one selected agent per step**. If you are
writing an AEC environment, you must account for two kinds of reward state:

- `self.rewards[agent]` is the reward assigned to that agent by the current
  transition. It is cleared when there is no new reward; it is **not** a running
  episode score.
- `self._cumulative_rewards[agent]` accumulates rewards until that agent
  next takes a turn. `env.last()` reads the cumulative reward for the
  currently selected agent. After its live action is processed, the
  environment resets that agent's cumulative entry, and
  `self._accumulate_rewards()` adds the transition's `self.rewards` to the
  cumulative entries for **all** agents.

For example, suppose the last move in a two-player AEC game gives the winner
`1` and the loser `0`, with no earlier rewards. That move sets
`self.rewards`, marks both agents terminated, and accumulates the rewards.
Each terminated agent can still be selected once more: the caller reads its
final reward and termination flag with `env.last()`, then calls
`env.step(None)`. That final *dead step* removes the agent and its reward
entries. Having empty reward dictionaries **after** both dead steps is
expected; the rewards were available through `last()` before removal.

An AEC environment's `step()` should handle a selected agent that is
already terminated or truncated with `self._was_dead_step(action)` and
return immediately. It must also update cumulative rewards after assigning
new rewards, including terminal rewards. For a concrete implementation, see
[the Rock–Paper–Scissors AEC `step()` method](https://github.com/Farama-Foundation/PettingZoo/blob/main/pettingzoo/classic/rps/rps.py);
for the dead-step lifecycle and a caller-side `agent_iter()` example, see
[Basic Usage: Variable Numbers of Agents (Death)](../../content/basic_usage.md#variable-numbers-of-agents-death).
