---
title: "(WIP) Creating Environments: Repository Structure"
---

# (WIP) Creating Environments: Repository Structure

## Introduction

Welcome to the first of five short tutorials, guiding you through the process of creating your own PettingZoo environment, from conception to deployment.

We will be creating a parallel environment, meaning that each agent acts simultaneously.

Before thinking about the environment logic, we should understand the structure of environment repositories.

## Tree structure
Environment repositories are usually laid out using the following structure:

    Custom-Environment
    ├── custom-environment
        └── env
            └── custom_environment.py
        └── custom_environment_v0.py
    ├── README.md
    └── requirements.txt

- `/custom-environment/env` is where your environment will be stored, along with any helper functions (in the case of a complicated environment).
- `/custom-environment/custom_environment_v0.py` is a file that imports the environment - we use the file name for environment version control.
- `/README.md` is a file used to describe your environment.
- `/requirements.txt` is a file used to keep track of your environment dependencies. At the very least, `pettingzoo` should be in there. **Please version control all your dependencies via `==`**.

### Advanced: Additional (optional) files
The above file structure is minimal. A more deployment-ready environment would include 
- `/docs/` for documentation, 
- `/setup.py` for packaging, 
- `/custom-environment/__init__.py` for depreciation handling, and 
- Github actions for continuous integration of environment tests. 

Implementing these are outside the scope of this tutorial.

## Skeleton code
The entirety of your environment logic is stored within `/custom-environment/env`

```{eval-rst}
.. literalinclude:: ../../../tutorials/EnvironmentCreation/1-SkeletonCreation.py
   :language: python
   :caption: /custom-environment/env/custom_environment.py
```
