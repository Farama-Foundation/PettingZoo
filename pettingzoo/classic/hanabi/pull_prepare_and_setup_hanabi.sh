#!/bin/bash

echo "Pulling hanabi submodule, if not existent"
git pull --recurse-submodules

echo "Installing gcc. First trying apt-get (linux). If not possible, try homebrew (macOS)"
apt-get install g++ || brew install gcc

cd env
pip install .
cd ..

echo "Verify hanabi wrapper is working"
python hanabi.py --test