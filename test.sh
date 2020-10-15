#!/bin/bash

render=True
manual_control=True
performance=True
save_obs=False

# runs all tests in .travis.yml
pytest ./pettingzoo/tests/pytest_runner.py
bash ./check_style.sh
pytest ./pettingzoo/tests/all_parameter_combs.py
python3 -m pettingzoo.tests.ci_test atari $render $manual_control $performance $save_obs
python3 -m pettingzoo.tests.ci_test classic $render $manual_control $performance $save_obs
python3 -m pettingzoo.tests.ci_test butterfly $render $manual_control $performance $save_obs
python3 -m pettingzoo.tests.ci_test mpe $render $manual_control $performance $save_obs
python3 -m pettingzoo.tests.ci_test magent $render $manual_control $performance $save_obs
python3 -m pettingzoo.tests.ci_test sisl $render $manual_control $performance $save_obs
