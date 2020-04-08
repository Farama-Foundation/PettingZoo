# Classic
flake8 pettingzoo/classic --ignore E501,E731,E741,E402,F401
# python3 -m pettingzoo.tests.ci_test classic/backgammon
# python3 -m pettingzoo.tests.ci_test classic/checkers
python3 -m pettingzoo.tests.ci_test classic/chess
# python3 -m pettingzoo.tests.ci_test classic/connect_four
python3 -m pettingzoo.tests.ci_test classic/dou_dizhu
# python3 -m pettingzoo.tests.ci_test classic/gin_rummy
# python3 -m pettingzoo.tests.ci_test classic/go
# python3 -m pettingzoo.tests.ci_test classic/hanabi
python3 -m pettingzoo.tests.ci_test classic/leduc_holdem
python3 -m pettingzoo.tests.ci_test classic/mahjong
python3 -m pettingzoo.tests.ci_test classic/rps
python3 -m pettingzoo.tests.ci_test classic/rpsls
python3 -m pettingzoo.tests.ci_test classic/texas_holdem
python3 -m pettingzoo.tests.ci_test classic/texas_holdem_no_limit
python3 -m pettingzoo.tests.ci_test classic/tictactoe
python3 -m pettingzoo.tests.ci_test classic/uno

# Gamma
flake8 pettingzoo/gamma --ignore E501,E731,E741,E402,F401
python3 -m pettingzoo.tests.ci_test gamma/cooperative_pong
# python3 -m pettingzoo.tests.ci_test gamma/knights_archers_zombies
# python3 -m pettingzoo.tests.ci_test gamma/pistonball
python3 -m pettingzoo.tests.ci_test gamma/prison
# python3 -m pettingzoo.tests.ci_test gamma/prospector

# MPE
flake8 pettingzoo/mpe --ignore E501,E731,E741,E402,F401
python3 -m pettingzoo.tests.ci_test mpe/simple
python3 -m pettingzoo.tests.ci_test mpe/simple_adversary
python3 -m pettingzoo.tests.ci_test mpe/simple_crypto
python3 -m pettingzoo.tests.ci_test mpe/simple_push
python3 -m pettingzoo.tests.ci_test mpe/simple_reference
python3 -m pettingzoo.tests.ci_test mpe/simple_speaker_listener
python3 -m pettingzoo.tests.ci_test mpe/simple_spread
python3 -m pettingzoo.tests.ci_test mpe/simple_tag
python3 -m pettingzoo.tests.ci_test mpe/simple_world_comm

# SISL
flake8 pettingzoo/sisl --ignore E501,E731,E741,E402,F401
python3 -m pettingzoo.tests.ci_test sisl/multiwalker
python3 -m pettingzoo.tests.ci_test sisl/pursuit
python3 -m pettingzoo.tests.ci_test sisl/waterworld

#MAgent
flake8 pettingzoo/magent --ignore E501,E731,E741,E402,F401
python3 -m pettingzoo.tests.ci_test magent
