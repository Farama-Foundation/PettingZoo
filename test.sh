#!/bin/bash

render=${pz_render:-True}
manual_control=$render
performance=True
save_obs=$render

python3 -m pettingzoo.tests.ci_test $pz_module $render $manual_control $performance $save_obs

python3 -m pettingzoo.tests.print_test
if [[ -z $(grep '[^[:space:]]' test_output.txt) ]]
then
    echo "Test Passed"
    exit 0
else
    echo "Test Failed"
    exit 1
fi