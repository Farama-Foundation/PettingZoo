#!/bin/bash
mkdir -p modules
cd modules

python -m pip download pettingzoo[all]

unzip -o '*.whl'
rm *.whl