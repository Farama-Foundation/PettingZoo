# See setup.cfg for codespell and flake8 settings
set -e

codespell pettingzoo/*/*.py pettingzoo/*/*/*.py
flake8 pettingzoo/ test/
isort -w 100 -o magent -p pettingzoo -c pettingzoo
