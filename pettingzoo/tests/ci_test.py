import pettingzoo.tests.api_test as api_test
import pettingzoo.tests.bombardment_test as bombardment_test
import pettingzoo.tests.performance_benchmark as performance_benchmark
import sys

# classic
_manual_control = None

render = False
if sys.argv[2] == 'True':
    render = True
manual_control = False
if sys.argv[3] == 'True':
    manual_control = True
bombardment = False
if sys.argv[4] == 'True':
    bombardment = True
performance = False
if sys.argv[5] == 'True':
    performance = True
save_obs = False
if sys.argv[6] == 'True':
    save_obs = True

if sys.argv[1] == 'classic/backgammon':
    print('classic/backgammon')
    from pettingzoo.classic import backgammon_v0
    _env = backgammon_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = backgammon_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = backgammon_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'classic/checkers':
    print('classic/checkers_')
    from pettingzoo.classic import checkers_v0
    _env = checkers_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = checkers_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = checkers_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'classic/chess':
    print('classic/chess')
    from pettingzoo.classic import chess_v0
    _env = chess_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = chess_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = chess_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'classic/connect_four':
    print('classic/connect_four')
    from pettingzoo.classic import connect_four_v0
    _env = connect_four_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = connect_four_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = connect_four_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'classic/dou_dizhu':
    print('classic/dou_dizhu')
    from pettingzoo.classic import dou_dizhu_v0
    _env = dou_dizhu_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = dou_dizhu_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = dou_dizhu_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'classic/gin_rummy':
    print('classic/gin_rummy')
    from pettingzoo.classic import gin_rummy_v0
    _env = gin_rummy_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = gin_rummy_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = gin_rummy_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'classic/go':
    print('classic/go')
    from pettingzoo.classic import go_v0
    _env = go_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = go_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = go_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'classic/hanabi':
    print('classic/hanabi')
    from pettingzoo.classic import hanabi_v0
    _env = hanabi_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = hanabi_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = hanabi_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'classic/leduc_holdem':
    print('classic/leduc_holdem')
    from pettingzoo.classic import leduc_holdem_v0
    _env = leduc_holdem_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = leduc_holdem_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = leduc_holdem_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'classic/mahjong':
    print('classic/mahjong')
    from pettingzoo.classic import mahjong_v0
    _env = mahjong_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = mahjong_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = mahjong_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'classic/rps':
    print('classic/rps')
    from pettingzoo.classic import rps_v0
    _env = rps_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = rps_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = rps_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'classic/rpsls':
    print('classic/rpsls')
    from pettingzoo.classic import rpsls_v0
    _env = rpsls_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = rpsls_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = rpsls_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'classic/texas_holdem':
    print('classic/texas_holdem')
    from pettingzoo.classic import texas_holdem_v0
    _env = texas_holdem_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = texas_holdem_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = texas_holdem_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'classic/texas_holdem_no_limit':
    print('classic/texas_holdem_no_limit')
    from pettingzoo.classic import texas_holdem_no_limit_v0
    _env = texas_holdem_no_limit_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = texas_holdem_no_limit_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = texas_holdem_no_limit_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'classic/tictactoe':
    print('classic/tictactoe')
    from pettingzoo.classic import tictactoe_v0
    _env = tictactoe_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = tictactoe_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = tictactoe_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'classic/uno':
    print('classic/uno')
    from pettingzoo.classic import uno_v0
    _env = uno_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = uno_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = uno_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

# gamma

elif sys.argv[1] == 'gamma/cooperative_pong':
    print('gamma/cooperative_pong')
    from pettingzoo.gamma import cooperative_pong_v0
    _env = cooperative_pong_v0.env()
    if manual_control:
        _manual_control = cooperative_pong_v0.manual_control
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=save_obs)
    if bombardment:
        _env = cooperative_pong_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = cooperative_pong_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'gamma/knights_archers_zombies':
    print('gamma/knights_archers_zombies')
    from pettingzoo.gamma import knights_archers_zombies_v0
    _env = knights_archers_zombies_v0.env()
    if manual_control:
        _manual_control = knights_archers_zombies_v0.manual_control
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=save_obs)
    if bombardment:
        _env = knights_archers_zombies_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = knights_archers_zombies_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'gamma/pistonball':
    print('gamma/pistonball')
    from pettingzoo.gamma import pistonball_v0
    _env = pistonball_v0.env()
    if manual_control:
        _manual_control = pistonball_v0.manual_control
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=save_obs)
    if bombardment:
        _env = pistonball_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = pistonball_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'gamma/prison':
    print('gamma/prison')
    from pettingzoo.gamma import prison_v0
    _env = prison_v0.env()
    if manual_control:
        _manual_control = prison_v0.manual_control
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=save_obs)
    if bombardment:
        _env = prison_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = prison_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'gamma/prospector':
    print('gamma/prospector')
    from pettingzoo.gamma import prospector_v0
    _env = prospector_v0.env()
    if manual_control:
        _manual_control = prospector_v0.manual_control
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=save_obs)
    if bombardment:
        _env = prospector_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = prospector_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

# mpe

elif sys.argv[1] == 'mpe/simple':
    print('mpe/simple')
    from pettingzoo.mpe import simple_v0
    _env = simple_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = simple_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = simple_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'mpe/simple_adversary':
    print('mpe/simple_adversary')
    from pettingzoo.mpe import simple_adversary_v0
    _env = simple_adversary_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = simple_adversary_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = simple_adversary_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'mpe/simple_crypto':
    print('mpe/simple_crypto')
    from pettingzoo.mpe import simple_crypto_v0
    _env = simple_crypto_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = simple_crypto_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = simple_crypto_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'mpe/simple_push':
    print('mpe/simple_push')
    from pettingzoo.mpe import simple_push_v0
    _env = simple_push_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = simple_push_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = simple_push_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'mpe/simple_reference':
    print('mpe/simple_reference')
    from pettingzoo.mpe import simple_reference_v0
    _env = simple_reference_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = simple_reference_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = simple_reference_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'mpe/simple_speak_listener':
    print('mpe/simple_speak_listener')
    from pettingzoo.mpe import simple_speak_listener_v0
    _env = simple_speak_listener_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = simple_speak_listener_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = simple_speak_listener_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'mpe/simple_spread':
    print('mpe/simple_spread')
    from pettingzoo.mpe import simple_spread_v0
    _env = simple_spread_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = simple_spread_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = simple_spread_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'mpe/simple_tag':
    print('mpe/simple_tag')
    from pettingzoo.mpe import simple_tag_v0
    _env = simple_tag_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = simple_tag_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = simple_tag_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'mpe/simple_world_comm':
    print('mpe/simple_world_comm')
    from pettingzoo.mpe import simple_world_comm_v0
    _env = simple_world_comm_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = simple_world_comm_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = simple_world_comm_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

# sisl

elif sys.argv[1] == 'sisl/multiwalker':
    print('sisl/multiwalker')
    from pettingzoo.sisl import multiwalker_v0
    _env = multiwalker_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = multiwalker_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = multiwalker_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'sisl/pursuit':
    print('sisl/pursuit')
    from pettingzoo.sisl import pursuit_v0
    _env = pursuit_v0.env()
    if manual_control:
        _manual_control = pursuit_v0.manual_control
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = pursuit_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = pursuit_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'sisl/waterworld':
    print('sisl/waterworld')
    from pettingzoo.sisl import waterworld_v0
    _env = waterworld_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = waterworld_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = waterworld_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'magent':
    print("magent")
    from pettingzoo.magent import magent_env
    _env = magent_env.env("pursuit", map_size=100)
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = magent_env.env("pursuit", map_size=00)
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = magent_env.env("pursuit", map_size=100)
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] = 'magent':
    print('magent')
    from pettingzoo.magent import magent
    _env = magent.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = waterworld.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = waterworld.env()
        performance_benchmark.performance_benchmark(_env)
