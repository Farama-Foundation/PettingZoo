render=True
manual_control=True
bombardment=True
performance=True
save_obs=True

flake8 pettingzoo/classic --ignore E501,E731,E741,E402,F401,W503
echo
# python3 -m pettingzoo.tests.ci_test classic/backgammon $render $manual_control $bombardment $performance $save_obs
# python3 -m pettingzoo.tests.ci_test classic/checkers $render $manual_control $bombardment $performance $save_obs
python3 -m pettingzoo.tests.ci_test classic/chess $render $manual_control $bombardment $performance $save_obs
python3 -m pettingzoo.tests.ci_test classic/connect_four $render $manual_control $bombardment $performance $save_obs
python3 -m pettingzoo.tests.ci_test classic/dou_dizhu $render $manual_control $bombardment $performance $save_obs
python3 -m pettingzoo.tests.ci_test classic/gin_rummy $render $manual_control $bombardment $performance $save_obs
python3 -m pettingzoo.tests.ci_test classic/go $render $manual_control $bombardment $performance $save_obs
# python3 -m pettingzoo.tests.ci_test classic/hanabi $render $manual_control $bombardment $performance $save_obs
python3 -m pettingzoo.tests.ci_test classic/leduc_holdem $render $manual_control $bombardment $performance $save_obs
python3 -m pettingzoo.tests.ci_test classic/mahjong $render $manual_control $bombardment $performance $save_obs
python3 -m pettingzoo.tests.ci_test classic/rps $render $manual_control $bombardment $performance $save_obs
python3 -m pettingzoo.tests.ci_test classic/rpsls $render $manual_control $bombardment $performance $save_obs
python3 -m pettingzoo.tests.ci_test classic/texas_holdem $render $manual_control $bombardment $performance $save_obs
python3 -m pettingzoo.tests.ci_test classic/texas_holdem_no_limit $render $manual_control $bombardment $performance $save_obs
python3 -m pettingzoo.tests.ci_test classic/tictactoe $render $manual_control $bombardment $performance $save_obs
python3 -m pettingzoo.tests.ci_test classic/uno $render $manual_control $bombardment $performance $save_obs

# Gamma
flake8 pettingzoo/gamma --ignore E501,E731,E741,E402,F401,W503
echo
python3 -m pettingzoo.tests.ci_test gamma/cooperative_pong $render $manual_control $bombardment $performance $save_obs
python3 -m pettingzoo.tests.ci_test gamma/knights_archers_zombies $render $manual_control $bombardment $performance $save_obs
python3 -m pettingzoo.tests.ci_test gamma/pistonball $render $manual_control $bombardment $performance $save_obs
python3 -m pettingzoo.tests.ci_test gamma/prison $render $manual_control $bombardment $performance $save_obs
# python3 -m pettingzoo.tests.ci_test gamma/prospector $render $manual_control $bombardment $performance $save_obs

# MAgent
flake8 pettingzoo/magent --ignore E501,E731,E741,E402,F401,W503
echo
#python3 -m pettingzoo.tests.ci_test magent $render $manual_control $bombardment $performance $save_obs

# MPE
flake8 pettingzoo/mpe --ignore E501,E731,E741,E402,F401,W503
echo
python3 -m pettingzoo.tests.ci_test mpe/simple $render $manual_control $bombardment $performance $save_obs
python3 -m pettingzoo.tests.ci_test mpe/simple_adversary $render $manual_control $bombardment $performance $save_obs
python3 -m pettingzoo.tests.ci_test mpe/simple_crypto $render $manual_control $bombardment $performance $save_obs
python3 -m pettingzoo.tests.ci_test mpe/simple_push $render $manual_control $bombardment $performance $save_obs
python3 -m pettingzoo.tests.ci_test mpe/simple_reference $render $manual_control $bombardment $performance $save_obs
python3 -m pettingzoo.tests.ci_test mpe/simple_speaker_listener $render $manual_control $bombardment $performance $save_obs
python3 -m pettingzoo.tests.ci_test mpe/simple_spread $render $manual_control $bombardment $performance $save_obs
python3 -m pettingzoo.tests.ci_test mpe/simple_tag $render $manual_control $bombardment $performance $save_obs
python3 -m pettingzoo.tests.ci_test mpe/simple_world_comm $render $manual_control $bombardment $performance $save_obs

# SISL
flake8 pettingzoo/sisl --ignore E501,E731,E741,E402,F401,W503
echo
python3 -m pettingzoo.tests.ci_test sisl/multiwalker  $render $manual_control $bombardment $performance $save_obs
python3 -m pettingzoo.tests.ci_test sisl/pursuit $render $manual_control $bombardment $performance $save_obs
python3 -m pettingzoo.tests.ci_test sisl/waterworld $render $manual_control $bombardment $performance $save_obs

# Utils
flake8 pettingzoo/utils --ignore E501,E731,E741,E402,F401,W503
echo

# Tests
flake8 pettingzoo/tests --ignore E501,E731,E741,E402,F401,W503
echo

python3 -m pettingzoo.tests.print_test
