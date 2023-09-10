---
title: "LangChain: Creating LLM agents"
---

# LangChain: Creating LLM agents

This tutorial will demonstrate how to use LangChain to create LLM agents that can interact with PettingZoo environments.

This tutorial was created from LangChain's documentation: [Simulated Environment: PettingZoo](https://python.langchain.com/en/latest/use_cases/agent_simulations/petting_zoo.html).

> For many applications of LLM agents, the environment is real (internet, database, REPL, etc). However, we can also define agents to interact in simulated environments like text-based games. This is an example of how to create a simple agent-environment interaction loop with PettingZoo.


## Environment Setup
To follow this tutorial, you will need to install the dependencies shown below. It is recommended to use a newly-created virtual environment to avoid dependency conflicts.
```{eval-rst}
.. literalinclude:: ../../../tutorials/LangChain/requirements.txt
   :language: text
```

## Environment Loop
```{eval-rst}
.. literalinclude:: ../../../tutorials/LangChain/langchain_example.py
   :pyobject: main
   :language: python
```


## Gymnasium Agent
Here we reproduce the same `GymnasiumAgent` defined from the [LangChain Gymnasium example](https://python.langchain.com/en/latest/use_cases/agent_simulations/gymnasium.html). If after multiple retries it does not take a valid action, it simply takes a random action.
```{eval-rst}
.. literalinclude:: ../../../tutorials/LangChain/gymnasium_agent.py
   :language: python
```
## PettingZoo Agent
The `PettingZooAgent` extends the `GymnasiumAgent` to the multi-agent setting. The main differences are:
- `PettingZooAgent` takes in a `name` argument to identify it among multiple agents
- the function `get_docs` is implemented differently because the `PettingZoo` repo structure is structured differently from the `Gymnasium` repo

```{eval-rst}
.. literalinclude:: ../../../tutorials/LangChain/pettingzoo_agent.py
   :language: python
```

### Rock-Paper-Scissors
We can now run a simulation of a multi-agent rock, paper, scissors game using the `PettingZooAgent`.

```{eval-rst}
.. literalinclude:: ../../../tutorials/LangChain/langchain_example.py
   :pyobject: rock_paper_scissors
   :language: python
```

```text
Observation: 3
Reward: 0
Termination: False
Truncation: False
Return: 0

Action: 1

Observation: 3
Reward: 0
Termination: False
Truncation: False
Return: 0

Action: 1

Observation: 1
Reward: 0
Termination: False
Truncation: False
Return: 0

Action: 2

Observation: 1
Reward: 0
Termination: False
Truncation: False
Return: 0

Action: 1

Observation: 1
Reward: 1
Termination: False
Truncation: False
Return: 1

Action: 0

Observation: 2
Reward: -1
Termination: False
Truncation: False
Return: -1

Action: 0

Observation: 0
Reward: 0
Termination: False
Truncation: True
Return: 1

Action: None

Observation: 0
Reward: 0
Termination: False
Truncation: True
Return: -1

Action: None
```


## Action Masking Agent
Some `PettingZoo` environments provide an `action_mask` to tell the agent which actions are valid. The `ActionMaskAgent` subclasses `PettingZooAgent` to use information from the `action_mask` to select actions.

```{eval-rst}
.. literalinclude:: ../../../tutorials/LangChain/action_masking_agent.py
   :language: python
```
### Tic-Tac-Toe
Here is an example of a Tic-Tac-Toe game that uses the `ActionMaskAgent`.
```{eval-rst}
.. literalinclude:: ../../../tutorials/LangChain/langchain_example.py
   :pyobject: tic_tac_toe
   :language: python
```

```text
Observation: {'observation': array([[[0, 0],
        [0, 0],
        [0, 0]],

       [[0, 0],
        [0, 0],
        [0, 0]],

       [[0, 0],
        [0, 0],
        [0, 0]]], dtype=int8), 'action_mask': array([1, 1, 1, 1, 1, 1, 1, 1, 1], dtype=int8)}
Reward: 0
Termination: False
Truncation: False
Return: 0

Action: 0
     |     |
  X  |  -  |  -
_____|_____|_____
     |     |
  -  |  -  |  -
_____|_____|_____
     |     |
  -  |  -  |  -
     |     |

Observation: {'observation': array([[[0, 1],
        [0, 0],
        [0, 0]],

       [[0, 0],
        [0, 0],
        [0, 0]],

       [[0, 0],
        [0, 0],
        [0, 0]]], dtype=int8), 'action_mask': array([0, 1, 1, 1, 1, 1, 1, 1, 1], dtype=int8)}
Reward: 0
Termination: False
Truncation: False
Return: 0

Action: 1
     |     |
  X  |  -  |  -
_____|_____|_____
     |     |
  O  |  -  |  -
_____|_____|_____
     |     |
  -  |  -  |  -
     |     |

Observation: {'observation': array([[[1, 0],
        [0, 1],
        [0, 0]],

       [[0, 0],
        [0, 0],
        [0, 0]],

       [[0, 0],
        [0, 0],
        [0, 0]]], dtype=int8), 'action_mask': array([0, 0, 1, 1, 1, 1, 1, 1, 1], dtype=int8)}
Reward: 0
Termination: False
Truncation: False
Return: 0

Action: 2
     |     |
  X  |  -  |  -
_____|_____|_____
     |     |
  O  |  -  |  -
_____|_____|_____
     |     |
  X  |  -  |  -
     |     |

Observation: {'observation': array([[[0, 1],
        [1, 0],
        [0, 1]],

       [[0, 0],
        [0, 0],
        [0, 0]],

       [[0, 0],
        [0, 0],
        [0, 0]]], dtype=int8), 'action_mask': array([0, 0, 0, 1, 1, 1, 1, 1, 1], dtype=int8)}
Reward: 0
Termination: False
Truncation: False
Return: 0

Action: 3
     |     |
  X  |  O  |  -
_____|_____|_____
     |     |
  O  |  -  |  -
_____|_____|_____
     |     |
  X  |  -  |  -
     |     |

Observation: {'observation': array([[[1, 0],
        [0, 1],
        [1, 0]],

       [[0, 1],
        [0, 0],
        [0, 0]],

       [[0, 0],
        [0, 0],
        [0, 0]]], dtype=int8), 'action_mask': array([0, 0, 0, 0, 1, 1, 1, 1, 1], dtype=int8)}
Reward: 0
Termination: False
Truncation: False
Return: 0

Action: 4
     |     |
  X  |  O  |  -
_____|_____|_____
     |     |
  O  |  X  |  -
_____|_____|_____
     |     |
  X  |  -  |  -
     |     |

Observation: {'observation': array([[[0, 1],
        [1, 0],
        [0, 1]],

       [[1, 0],
        [0, 1],
        [0, 0]],

       [[0, 0],
        [0, 0],
        [0, 0]]], dtype=int8), 'action_mask': array([0, 0, 0, 0, 0, 1, 1, 1, 1], dtype=int8)}
Reward: 0
Termination: False
Truncation: False
Return: 0

Action: 5
     |     |
  X  |  O  |  -
_____|_____|_____
     |     |
  O  |  X  |  -
_____|_____|_____
     |     |
  X  |  O  |  -
     |     |

Observation: {'observation': array([[[1, 0],
        [0, 1],
        [1, 0]],

       [[0, 1],
        [1, 0],
        [0, 1]],

       [[0, 0],
        [0, 0],
        [0, 0]]], dtype=int8), 'action_mask': array([0, 0, 0, 0, 0, 0, 1, 1, 1], dtype=int8)}
Reward: 0
Termination: False
Truncation: False
Return: 0

Action: 6
     |     |
  X  |  O  |  X
_____|_____|_____
     |     |
  O  |  X  |  -
_____|_____|_____
     |     |
  X  |  O  |  -
     |     |

Observation: {'observation': array([[[0, 1],
        [1, 0],
        [0, 1]],

       [[1, 0],
        [0, 1],
        [1, 0]],

       [[0, 1],
        [0, 0],
        [0, 0]]], dtype=int8), 'action_mask': array([0, 0, 0, 0, 0, 0, 0, 1, 1], dtype=int8)}
Reward: -1
Termination: True
Truncation: False
Return: -1

Action: None

Observation: {'observation': array([[[1, 0],
        [0, 1],
        [1, 0]],

       [[0, 1],
        [1, 0],
        [0, 1]],

       [[1, 0],
        [0, 0],
        [0, 0]]], dtype=int8), 'action_mask': array([0, 0, 0, 0, 0, 0, 0, 1, 1], dtype=int8)}
Reward: 1
Termination: True
Truncation: False
Return: 1

Action: None
```

### Texas Holdem' No Limit
Here is an example of a Texas Hold'em No Limit game that uses the `ActionMaskAgent`.
```{eval-rst}
.. literalinclude:: ../../../tutorials/LangChain/langchain_example.py
   :pyobject: texas_holdem_no_limit
   :language: python
```

```text
Observation: {'observation': array([0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 1., 0., 0., 0., 0.,
       0., 0., 2.], dtype=float32), 'action_mask': array([1, 1, 0, 1, 1], dtype=int8)}
Reward: 0
Termination: False
Truncation: False
Return: 0

Action: 1

Observation: {'observation': array([0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0.,
       0., 0., 2.], dtype=float32), 'action_mask': array([1, 1, 0, 1, 1], dtype=int8)}
Reward: 0
Termination: False
Truncation: False
Return: 0

Action: 1

Observation: {'observation': array([0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 1.,
       0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 1., 2.], dtype=float32), 'action_mask': array([1, 1, 1, 1, 1], dtype=int8)}
Reward: 0
Termination: False
Truncation: False
Return: 0

Action: 1

Observation: {'observation': array([0., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 2., 2.], dtype=float32), 'action_mask': array([1, 1, 1, 1, 1], dtype=int8)}
Reward: 0
Termination: False
Truncation: False
Return: 0

Action: 0

Observation: {'observation': array([0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 1.,
       0., 0., 0., 0., 0., 1., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 2., 2.], dtype=float32), 'action_mask': array([1, 1, 1, 1, 1], dtype=int8)}
Reward: 0
Termination: False
Truncation: False
Return: 0

Action: 2

Observation: {'observation': array([0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 0., 0., 0., 0., 1., 0., 0., 1., 1., 0., 0., 1., 0., 0., 0., 0.,
       0., 2., 6.], dtype=float32), 'action_mask': array([1, 1, 1, 1, 1], dtype=int8)}
Reward: 0
Termination: False
Truncation: False
Return: 0

Action: 2

Observation: {'observation': array([0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 0., 0., 0., 0., 1., 0., 0., 1., 0., 0., 0., 0., 0., 1., 0., 0.,
       0., 2., 8.], dtype=float32), 'action_mask': array([1, 1, 1, 1, 1], dtype=int8)}
Reward: 0
Termination: False
Truncation: False
Return: 0

Action: 3

Observation: {'observation': array([ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,
        0.,  0.,  0.,  0.,  0.,  0.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,
        0.,  0.,  0.,  0.,  1.,  0.,  0.,  1.,  0.,  0.,  0.,  0.,  0.,
        1.,  0.,  0.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,
        6., 20.], dtype=float32), 'action_mask': array([1, 1, 1, 1, 1], dtype=int8)}
Reward: 0
Termination: False
Truncation: False
Return: 0

Action: 4

Observation: {'observation': array([  0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   1.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   1.,   0.,   0.,   1.,   1.,
         0.,   0.,   1.,   0.,   0.,   0.,   0.,   0.,   8., 100.],
      dtype=float32), 'action_mask': array([1, 1, 0, 0, 0], dtype=int8)}
Reward: 0
Termination: False
Truncation: False
Return: 0

Action: 4
[WARNING]: Illegal move made, game terminating with current player losing.
obs['action_mask'] contains a mask of all legal moves that can be chosen.

Observation: {'observation': array([  0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   1.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   1.,   0.,   0.,   1.,   1.,
         0.,   0.,   1.,   0.,   0.,   0.,   0.,   0.,   8., 100.],
      dtype=float32), 'action_mask': array([1, 1, 0, 0, 0], dtype=int8)}
Reward: -1.0
Termination: True
Truncation: True
Return: -1.0

Action: None

Observation: {'observation': array([  0.,   0.,   1.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   1.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   1.,   0.,   0.,   1.,   0.,
         0.,   0.,   0.,   0.,   1.,   0.,   0.,   0.,  20., 100.],
      dtype=float32), 'action_mask': array([1, 1, 0, 0, 0], dtype=int8)}
Reward: 0
Termination: True
Truncation: True
Return: 0

Action: None

Observation: {'observation': array([  0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   1.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   1.,   0.,   0.,
         1.,   0.,   0.,   0.,   0.,   0.,   1.,   0.,   0.,   1.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0., 100., 100.],
      dtype=float32), 'action_mask': array([1, 1, 0, 0, 0], dtype=int8)}
Reward: 0
Termination: True
Truncation: True
Return: 0

Action: None

Observation: {'observation': array([  0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   1.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   1.,   1.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   1.,   0.,   0.,   1.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   2., 100.],
      dtype=float32), 'action_mask': array([1, 1, 0, 0, 0], dtype=int8)}
Reward: 0
Termination: True
Truncation: True
Return: 0

Action: None
```



## Full Code

The following code should run without any issues. The comments are designed to help you understand how to use PettingZoo with LangChain. If you have any questions, please feel free to ask in the [Discord server](https://discord.gg/nhvKkYa6qX).

```{eval-rst}

.. literalinclude:: ../../../tutorials/LangChain/langchain_example.py
   :language: python

```
