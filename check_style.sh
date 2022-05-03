# See setup.cfg for codespell and flake8 settings
set -e

codespell pettingzoo/*/*.py pettingzoo/*/*/*.py --ignore-words-list magent --skip *.css,*.js,*.map,*.scss,*svg
flake8 pettingzoo/ --ignore E203,W503,E501,F401 --max-line-length 88
flake8 test/ --ignore E203,W503,E741,E501,F401,F405 --max-line-length 88
isort -w 100 -o magent -p pettingzoo -c pettingzoo --profile black --line-length 88
