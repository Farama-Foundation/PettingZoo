# See setup.cfg for codespell and flake8 settings
set -e

codespell pettingzoo/*/*.py pettingzoo/*/*/*.py --ignore-words-list magent --skip *.css,*.js,*.map,*.scss,*svg
flake8 pettingzoo/ --ignore E203,E266,E501,W503,F403,F401,E402,E128,E741 --max-line-length 88
flake8 test/ --ignore E203,E266,E501,W503,F403,F401,E402,E128,E741,F405 --max-line-length 88
isort -w 100 -o magent -p pettingzoo -c pettingzoo --profile black --line-length 88
