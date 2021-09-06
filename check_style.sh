# See setup.cfg for codespell and flake8 settings
bandit --recursive --skip B101,B301,B303,B311,B403,B404,B603,B607 .
codespell
flake8 pettingzoo/ test/
isort -w 100 -o magent -p pettingzoo -c pettingzoo
