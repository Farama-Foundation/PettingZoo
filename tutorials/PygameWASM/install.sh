#!/bin/bash
mkdir -p modules
cd modules

python -m pip download numpy==1.22.4 gymnasium==0.27.1 pettingzoo==1.22.3 pygame==2.2.0  chess==1.9.4

unzip -o '*.whl'
rm *.whl