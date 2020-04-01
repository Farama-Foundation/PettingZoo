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
if sys.argv[5] == 'True':
    save_obs = True

if sys.argv[1] == 'classic/backgammon':
    print('classic/backgammon')
    from pettingzoo.classic import backgammon
    _env = backgammon.env()
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = backgammon.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = backgammon.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'classic/checkers':
    print('classic/checkers')
    from pettingzoo.classic import checkers
    _env = checkers.env()
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = checkers.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = checkers.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'classic/chess':
    print('classic/chess')
    from pettingzoo.classic import chess
    _env = chess.env()
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = chess.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = chess.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'classic/connect_four':
    print('classic/connect_four')
    from pettingzoo.classic import connect_four
    _env = connect_four.env()
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = connect_four.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = connect_four.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'classic/dou_dizhu':
    print('classic/dou_dizhu')
    from pettingzoo.classic import dou_dizhu
    _env = dou_dizhu.env()
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = dou_dizhu.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = dou_dizhu.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'classic/gin_rummy':
    print('classic/gin_rummy')
    from pettingzoo.classic import gin_rummy
    _env = gin_rummy.env()
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = gin_rummy.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = gin_rummy.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'classic/go':
    print('classic/go')
    from pettingzoo.classic import go
    _env = go.env()
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = go.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = go.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'classic/hanabi':
    print('classic/hanabi')
    from pettingzoo.classic import hanabi
    _env = hanabi.env()
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = hanabi.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = hanabi.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'classic/leduc_holdem':
    print('classic/leduc_holdem')
    from pettingzoo.classic import leduc_holdem
    _env = leduc_holdem.env()
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = leduc_holdem.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = leduc_holdem.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'classic/mahjong':
    print('classic/mahjong')
    from pettingzoo.classic import mahjong
    _env = mahjong.env()
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = mahjong.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = mahjong.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'classic/rps':
    print('classic/rps')
    from pettingzoo.classic import rps
    _env = rps.env()
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = rps.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = rps.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'classic/rpsls':
    print('classic/rpsls')
    from pettingzoo.classic import rpsls
    _env = rpsls.env()
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = rpsls.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = rpsls.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'classic/texas_holdem':
    print('classic/texas_holdem')
    from pettingzoo.classic import texas_holdem
    _env = texas_holdem.env()
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = texas_holdem.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = texas_holdem.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'classic/texas_holdem_no_limit':
    print('classic/texas_holdem_no_limit')
    from pettingzoo.classic import texas_holdem_no_limit
    _env = texas_holdem_no_limit.env()
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = texas_holdem_no_limit.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = texas_holdem_no_limit.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'classic/tictactoe':
    print('classic/tictactoe')
    from pettingzoo.classic import tictactoe
    _env = tictactoe.env()
    if manual_control:
        _manual_control = tictactoe.manual_control
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = tictactoe.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = tictactoe.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'classic/uno':
    print('classic/uno')
    from pettingzoo.classic import uno
    _env = uno.env()
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = uno.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = uno.env()
        performance_benchmark.performance_benchmark(_env)

# gamma

if sys.argv[1] == 'gamma/cooperative_pong':
    print('gamma/cooperative_pong')
    from pettingzoo.gamma import cooperative_pong
    _env = cooperative_pong.env()
    if manual_control:
        _manual_control = cooperative_pong.manual_control
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = cooperative_pong.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = cooperative_pong.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'gamma/knights_archers_zombies':
    print('gamma/knights_archers_zombies')
    from pettingzoo.gamma import knights_archers_zombies
    _env = knights_archers_zombies.env()
    api_test.api_test(_env, render=render, manual_control=manual_control, save_obs=False)
    if bombardment:
        _env = knights_archers_zombies.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = knights_archers_zombies.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'gamma/pistonball':
    print('gamma/pistonball')
    from pettingzoo.gamma import pistonball
    _env = pistonball.env()
    api_test.api_test(_env, render=render, manual_control=manual_control, save_obs=False)
    if bombardment:
        _env = pistonball.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = pistonball.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'gamma/prison':
    print('gamma/prison')
    from pettingzoo.gamma import prison
    _env = prison.env()
    api_test.api_test(_env, render=render, manual_control=manual_control, save_obs=False)
    if bombardment:
        _env = prison.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = prison.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'gamma/prospector':
    print('gamma/prospector')
    from pettingzoo.gamma import prospector
    _env = prospector.env()
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = prospector.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = prospector.env()
        performance_benchmark.performance_benchmark(_env)

# mpe

if sys.argv[1] == 'mpe/simple':
    print('mpe/simple')
    from pettingzoo.mpe import simple
    _env = simple.env()
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = simple.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = simple.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'mpe/simple_adversary':
    print('mpe/simple_adversary')
    from pettingzoo.mpe import simple_adversary
    _env = simple_adversary.env()
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = simple_adversary.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = simple_adversary.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'mpe/simple_crypto':
    print('mpe/simple_crypto')
    from pettingzoo.mpe import simple_crypto
    _env = simple_crypto.env()
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = simple_crypto.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = simple_crypto.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'mpe/simple_push':
    print('mpe/simple_push')
    from pettingzoo.mpe import simple_push
    _env = simple_push.env()
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = simple_push.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = simple_push.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'mpe/simple_reference':
    print('mpe/simple_reference')
    from pettingzoo.mpe import simple_reference
    _env = simple_reference.env()
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = simple_reference.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = simple_reference.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'mpe/simple_speak_listener':
    print('mpe/simple_speak_listener')
    from pettingzoo.mpe import simple_speak_listener
    _env = simple_speak_listener.env()
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = simple_speak_listener.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = simple_speak_listener.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'mpe/simple_spread':
    print('mpe/simple_spread')
    from pettingzoo.mpe import simple_spread
    _env = simple_spread.env()
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = simple_spread.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = simple_spread.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'mpe/simple_tag':
    print('mpe/simple_tag')
    from pettingzoo.mpe import simple_tag
    _env = simple_tag.env()
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = simple_tag.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = simple_tag.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'mpe/simple_world_comm':
    print('mpe/simple_world_comm')
    from pettingzoo.mpe import simple_world_comm
    _env = simple_world_comm.env()
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = simple_world_comm.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = simple_world_comm.env()
        performance_benchmark.performance_benchmark(_env)

# sisl

if sys.argv[1] == 'sisl/multiwalker':
    print('sisl/multiwalker')
    from pettingzoo.sisl import multiwalker
    _env = multiwalker.env()
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = multiwalker.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = multiwalker.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'sisl/pursuit':
    print('sisl/pursuit')
    from pettingzoo.sisl import pursuit
    _env = pursuit.env()
    if manual_control:
        _manual_control = pursuit.manual_control
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = pursuit.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = pursuit.env()
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'sisl/waterworld':
    print('sisl/waterworld')
    from pettingzoo.sisl import waterworld
    _env = waterworld.env()
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = waterworld.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = waterworld.env()
        performance_benchmark.performance_benchmark(_env)
