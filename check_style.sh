# See setup.cfg for codespell and flake8 settings
bandit --recursive --skip B101,B301,B303,B311,B403,B404,B603,B607 .
codespell || true  # Adjust after pull request #448 lands
flake8 pettingzoo/ test/
