---
title: "(WIP) Creating Environments: Action Masking"
---

# (WIP) Creating Environments: Action Masking

## Introduction

In many environments, it is natural for some actions to be invalid at certain times. For example, in a game of chess, it is impossible to move a pawn forward if it is already at the front of the board. In PettingZoo, we can use action masking to prevent invalid actions from being taken.

Action masking is a more natural way of handling invalid actions than having an action have no effect, which was how we handled bumping into walls in the previous tutorial.

## Code

```{eval-rst}
.. literalinclude:: ../../../tutorials/EnvironmentCreation/3-ActionMasking.py
   :language: python
   :caption: /custom-environment/env/custom_environment.py
   :lines: -147
```