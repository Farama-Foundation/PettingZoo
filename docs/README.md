# PettingZoo docs

This folder contains the documentation for [PettingZoo](https://github.com/Farama-Foundation/PettingZoo).

For more information about how to contribute to the documentation go to our [CONTRIBUTING.md](https://github.com/Farama-Foundation/PettingZoo/blob/master/CONTRIBUTING.md)

## Editing an environment page

Environments' documentation can be found at the top of the file python file where the environment is declared, for example, the documentation for the chess environment can be at [/pettingzoo/classic/chess/chess.py](https://github.com/Farama-Foundation/PettingZoo/blob/master/pettingzoo/classic/chess/chess.py)

To generate the environments pages you need to execute the `docs/_scripts/gen_envs_mds.py` script:

```
cd docs
python _scripts/gen_envs_mds.py
```

## Build the Documentation

Install the required packages and PettingZoo:

```
pip install -e .
pip install -r docs/requirements.txt
```

To build the documentation once:

```
cd docs
make dirhtml
```

To rebuild the documentation automatically every time a change is made:

```
cd docs
sphinx-autobuild -b dirhtml . _build
```

## Test the documentation
The plugin [pytest-markdown-docs](https://github.com/modal-labs/pytest-markdown-docs) allows us to test our documentation to ensure that example code runs successfully. To test, run the following command:
pytest docs --markdown-docs -m markdown-docs
