---
title: "Tutorial: Testing Your Environment"
---

# Tutorial: Testing Your Environment

## Introduction

Now that our environment is complete, we can test it to make sure it works as intended. PettingZoo has a built-in testing suite that can be used to test your environment.

## Code

Note: This code can be added to the bottom of the same file, without using any imports, but it is best practice to keep tests in a separate file, and use modular imports, as shown below..

Relative importing is used for simplicity, and assumes your custom environment is in the same directory. If your test is in another location (e.g., a root-level `/test/` directory), it is recommended to import using absolute path.

```{eval-rst}
.. literalinclude:: ../../../tutorials/CustomEnvironment/tutorial4_testing_the_environment.py
   :language: python
   :caption: /custom-environment/env/custom_environment.py
```
