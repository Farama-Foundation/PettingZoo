# PettingZoo docs

This folder contains the documentation for [PettingZoo](https://github.com/Farama-Foundation/PettingZoo).

## Instructions for editing content

Our documentation is written in Markdown (more precisely, MyST - Markedly Structured Text) and built using [Sphinx](https://www.sphinx-doc.org/en/master/).
All content present in the documentation website can be found in this directory except for the environments.

### Editing an environment page

Environemnts' documentation can be found at the top of the file python file where the environment is declared, for example, the documentation for the chess environment can be at [/pettingzoo/classic/chess/chess.py](https://github.com/Farama-Foundation/PettingZoo/blob/master/pettingzoo/classic/chess/chess.py)

To generate the environments pages you need to execute the `_scripts/gen_envs_mds.py` script.

## Build the Documentation

Install the required packages and PettingZoo:

```
pip install -e .
cd docs/
pip install -r requirements.txt
```

To build the documentation once:

```
cd docs
make dirhtml _build
```

To rebuild the documentation automatically every time a change is made:

```
cd docs
sphinx-autobuild -b dirhtml . _build
```
