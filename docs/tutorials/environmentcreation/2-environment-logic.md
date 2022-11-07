---
title: "(WIP) Creating Environments: Environment Logic"
---

# (WIP) Creating Environments: Environment Logic

## Introduction

Now that we have a basic understanding of the structure of environment repositories, we can start thinking about the fun part - environment logic!

For this tutorial, we will be creating a two-player game consisting of a prisoner, trying to escape, and a guard, trying to catch the prisoner. This game will be played on a 7x7 grid, where:
- The prisoner starts in the top left corner,
- the guard starts in the bottom right corner,
- the escape door is randomly placed in the middle of the grid, and 
- Both the prisoner and the guard can move in any of the four cardinal directions (up, down, left, right).

## Code

```{eval-rst}
.. literalinclude:: ../../../tutorials/EnvironmentCreation/2-AddingGameLogic.py
   :language: python
   :caption: /custom-environment/env/custom_environment.py
```
