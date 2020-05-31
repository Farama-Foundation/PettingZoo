render=True
manual_control=True
bombardment=True
performance=True
save_obs=True

python3 -m pettingzoo.tests.ci_test $pz_module $render $manual_control $bombardment $performance $save_obs

python3 -m pettingzoo.tests.print_test
