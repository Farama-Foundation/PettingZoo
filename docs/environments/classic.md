---
title: Classic Environments
firstpage:
---

# Classic

```{toctree}
:hidden:
classic/chess
classic/connect_four
classic/gin_rummy
classic/go
classic/hanabi
classic/leduc_holdem
classic/rps
classic/texas_holdem_no_limit
classic/texas_holdem
classic/tictactoe
```

```{raw} html
    :file: classic/list.html
```

Classic environments represent implementations of popular turn-based human games and are mostly competitive.


### Installation

The unique dependencies for this set of environments can be installed via:

````bash
pip install 'pettingzoo[classic]'
````

### Usage

To launch a [Connect Four](/environments/classic/connect_four/) environment with random agents:
``` python
from pettingzoo.classic import connect_four_v3

env = connect_four_v3.env(render_mode="human")
env.reset(seed=42)

for agent in env.agent_iter():
    observation, reward, termination, truncation, info = env.last()

    if termination or truncation:
        action = None
    else:
        mask = observation["action_mask"]
        action = env.action_space(agent).sample(mask)  # this is where you would insert your policy

    env.step(action)
env.close()
```

The classic environments have a few differences from others in this library:

* No classic environments currently take any environment arguments.
* All classic environments are rendered solely via printing to terminal.
* Most environments only give rewards at the end of the games once an agent wins or losses, with a reward of 1 for winning and -1 for losing.
* Many classic environments have illegal moves in the action space. These environments communicate the legal moves at any given time as part of the observation. This is done with dictionary observations where the `observation` element is the observation and the `action_mask` element is a binary vector which is 1 if the action is legal. Note that the `action_mask` observation will only have non-zero values right before the agents takes its step.
* In environments with illegal moves, taking an illegal move will give a reward equal to losing the game to the illegally moving player and 0 to the other players before ending the game.


Many of the classic environments are based on [RLCard](https://github.com/datamllab/rlcard). If you use these libraries in your research, please cite them:

```
@article{zha2019rlcard,
  title={RLCard: A Toolkit for Reinforcement Learning in Card Games},
  author={Zha, Daochen and Lai, Kwei-Herng and Cao, Yuanpu and Huang, Songyi and Wei, Ruzhe and Guo, Junyu and Hu, Xia},
  journal={arXiv preprint arXiv:1910.04376},
  year={2019}
}
```
