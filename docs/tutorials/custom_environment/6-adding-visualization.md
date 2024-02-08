---
title: "Tutorial: Adding visualization with pygame and a simple random policy"
---

# Tutorial: Adding visualization with pygame and a simple random policy

## Introduction

The standard library for adding graphics to your environments is [pygame](https://www.pygame.org/).

Here we present a simple visualization tool to see the guard and the prisoner in action.

They both have a very simple policy: they're just taking random actions. Occasionaly you can see that the prisoner is able to scape or tha guard is able to caught them. You can modify the amount of steps you want to run the simulation for and also write your own policy.

You can add the following file in the root of your directory. If you name it `visualization.py`, this is how it will look:

    Custom-Environment
    ├── custom-environment
        └── env
            └── custom_environment.py
        └── custom_environment_v0.py
    ├── README.md
    └── requirements.txt
    └── visualization.py

## Setup and execution

To run the visualization make sure you have `pygame` installed for the graphics and `numpy` to generate the random policy.

You can add both of these packages with pip or conda. `pip install pygame numpy` or `conda install pygame numpy`.

Now you can run the code with `python3 visualization.py`.

## Code

```{eval-rst}
.. literalinclude:: ../../../tutorials/CustomEnvironment/tutorial6_adding_visualization_and_policy.py
   :language: python
   :caption: /custom-environment/env/custom_environment.py
```
