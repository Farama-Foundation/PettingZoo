---
title: "Tutorial: Testing Your Environment"
---

# Tutorial: Testing Your Environment

## Introduction

Now that our environment is complete, we can test it to make sure it works as intended. PettingZoo has a built-in testing suite that can be used to test your environment.

## Code

Note: This code can be added to the bottom of the same file, without using any imports, but it is best practice to keep tests in a separate file, as shown below. 

Tests are generally kept in a root level `/test/` folder, but we don't have to worry about where this script is located, as it imports using absolute path rather than relative path. 

```{eval-rst}
.. literalinclude:: ../../../tutorials/EnvironmentCreation/tutorial4_testing_the_environment.py
   :language: python
   :caption: /custom-environment/env/custom_environment.py
```