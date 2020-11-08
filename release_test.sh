#!/bin/bash

render=True
manual_control=True
performance=True
save_obs=True
num_cycles=1000

# runs all tests in .travis.yml
pytest pettingzoo/tests/pytest_runner.py
bash ./check_style.sh
python3 -m pettingzoo.tests.print_test
pytest ./pettingzoo/tests/all_parameter_combs.py
python3 -m pettingzoo.tests.ci_test atari $num_cycles $render $manual_control $performance $save_obs
python3 -m pettingzoo.tests.ci_test classic $num_cycles $render $manual_control $performance $save_obs
python3 -m pettingzoo.tests.ci_test butterfly $num_cycles $render $manual_control $performance $save_obs
python3 -m pettingzoo.tests.ci_test mpe $num_cycles $render $manual_control $performance $save_obs
python3 -m pettingzoo.tests.ci_test magent $num_cycles $render $manual_control $performance $save_obs
python3 -m pettingzoo.tests.ci_test sisl $num_cycles $render $manual_control $performance $save_obs
