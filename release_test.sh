#!/bin/bash

render=True
manual_control=True
performance=True
save_obs=True
num_cycles=1000

pytest ./test/pytest_runner.py
bash ./check_style.sh
python3 -m test.print_test
pytest ./test/all_parameter_combs.py
python3 -m test.ci_test atari $num_cycles $render $manual_control $performance $save_obs
python3 -m test.ci_test classic $num_cycles $render $manual_control $performance $save_obs
python3 -m test.ci_test butterfly $num_cycles $render $manual_control $performance $save_obs
python3 -m test.ci_test mpe $num_cycles $render $manual_control $performance $save_obs
python3 -m test.ci_test magent $num_cycles $render $manual_control $performance $save_obs
python3 -m test.ci_test sisl $num_cycles $render $manual_control $performance $save_obs
