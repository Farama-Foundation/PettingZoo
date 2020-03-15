import pettingzoo.tests.api_test as api_test
import pettingzoo.tests.bombardment_test as bombardment_test
import pettingzoo.tests.performance_benchmark as performance_benchmark
import sys

# classic

if sys.argv[1] == 'classic/backgammon':
    print('classic/backgammon')
    from pettingzoo.classic import backgammon
    backgammon = backgammon.env()
    api_test.api_test(backgammon)
    bombardment_test.bombardment_test(backgammon)
    performance_benchmark.performance_benchmark(backgammon)

if sys.argv[1] == 'classic/checkers':
    print('classic/checkers')
    from pettingzoo.classic import checkers
    checkers = checkers.env()
    api_test.api_test(checkers)
    bombardment_test.bombardment_test(checkers)
    performance_benchmark.performance_benchmark(checkers)

if sys.argv[1] == 'classic/chess':
    print('classic/chess')
    from pettingzoo.classic import chess
    chess = chess.env()
    api_test.api_test(chess)
    bombardment_test.bombardment_test(chess)
    performance_benchmark.performance_benchmark(chess)

if sys.argv[1] == 'classic/connect_four':
    print('classic/connect_four')
    from pettingzoo.classic import connect_four
    connect_four = connect_four.env()
    api_test.api_test(connect_four)
    bombardment_test.bombardment_test(connect_four)
    performance_benchmark.performance_benchmark(connect_four)

if sys.argv[1] == 'classic/dou_dizhu':
    from pettingzoo.classic import dou_dizhu
    dou_dizhu = dou_dizhu.env()
    api_test.api_test(dou_dizhu)
    print('classic/dou_dizhu')
    bombardment_test.bombardment_test(dou_dizhu)
    performance_benchmark.performance_benchmark(dou_dizhu)

if sys.argv[1] == 'classic/go':
    print('classic/go')
    from pettingzoo.classic import go
    go = go.env()
    api_test.api_test(go)
    bombardment_test.bombardment_test(go)
    performance_benchmark.performance_benchmark(go)

if sys.argv[1] == 'classic/hanabi':
    print('classic/hanabi')
    from pettingzoo.classic import hanabi
    hanabi = hanabi.env()
    api_test.api_test(hanabi)
    bombardment_test.bombardment_test(hanabi)
    performance_benchmark.performance_benchmark(hanabi)

if sys.argv[1] == 'classic/leduc_holdem':
    print('classic/leduc_holdem')
    from pettingzoo.classic import leduc_holdem
    leduc_holdem = leduc_holdem.env()
    api_test.api_test(leduc_holdem)
    bombardment_test.bombardment_test(leduc_holdem)
    performance_benchmark.performance_benchmark(leduc_holdem)

if sys.argv[1] == 'classic/mahjong':
    print('classic/mahjong')
    from pettingzoo.classic import mahjong
    mahjong = mahjong.env()
    api_test.api_test(mahjong)
    bombardment_test.bombardment_test(mahjong)
    performance_benchmark.performance_benchmark(mahjong)

if sys.argv[1] == 'classic/rps':
    print('classic/rps')
    from pettingzoo.classic import rps
    rps = rps.env()
    api_test.api_test(rps)
    bombardment_test.bombardment_test(rps)
    performance_benchmark.performance_benchmark('classic/rps')

if sys.argv[1] == 'classic/rpsls':
    print('classic/rpsls')
    from pettingzoo.classic import rpsls
    rpsls = rpsls.env()
    api_test.api_test(rpsls)
    bombardment_test.bombardment_test(rpsls)
    performance_benchmark.performance_benchmark(rpsls)

if sys.argv[1] == 'classic/texas_holdem':
    print('classic/texas_holdem')
    from pettingzoo.classic import texas_holdem
    texas_holdem = texas_holdem.env()
    api_test.api_test(texas_holdem)
    bombardment_test.bombardment_test(texas_holdem)
    performance_benchmark.performance_benchmark(texas_holdem)

if sys.argv[1] == 'classic/texas_holdem_no_limit':
    print('classic/texas_holdem_no_limit')
    from pettingzoo.classic import texas_holdem_no_limit
    texas_holdem_no_limit = texas_holdem_no_limit.env()
    api_test.api_test(texas_holdem_no_limit)
    bombardment_test.bombardment_test(texas_holdem_no_limit)
    performance_benchmark.performance_benchmark(texas_holdem_no_limit)

if sys.argv[1] == 'classic/tic_tac_toe':
    print('classic/tic_tac_toe')
    from pettingzoo.gamma import tic_tac_toe
    tic_tac_toe = tic_tac_toe.env()
    api_test.api_test(tic_tac_toe)
    bombardment_test.bombardment_test(tic_tac_toe)
    performance_benchmark.performance_benchmark(tic_tac_toe)

if sys.argv[1] == 'classic/uno':
    print('classic/uno')
    from pettingzoo.classic import uno
    uno = uno.env()
    api_test.api_test(uno)
    bombardment_test.bombardment_test(uno)
    performance_benchmark.performance_benchmark(uno)

# gamma

if sys.argv[1] == 'gamma/cooperative_pong':
    print('gamma/cooperative_pong')
    from pettingzoo.gamma import cooperative_pong
    _env = cooperative_pong.env()
    api_test.api_test(_env, render=True, manual_control=True)
    _env = cooperative_pong.env()
    bombardment_test.bombardment_test(_env)
    _env = cooperative_pong.env()
    performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'gamma/knights_archers_zombies':
    print('gamma/knights_archers_zombies')
    from pettingzoo.gamma import knights_archers_zombies
    knights_archers_zombies = knights_archers_zombies.env()
    api_test.api_test(knights_archers_zombies, render=True, manual_control=True)
    bombardment_test.bombardment_test(knights_archers_zombies)
    performance_benchmark.performance_benchmark(knights_archers_zombies)

if sys.argv[1] == 'gamma/pistonball':
    print('gamma/pistonball')
    from pettingzoo.gamma import pistonball
    pistonball = pistonball.env()
    api_test.api_test(pistonball, render=True, manual_control=True)
    bombardment_test.bombardment_test(pistonball)
    performance_benchmark.performance_benchmark(pistonball)

if sys.argv[1] == 'gamma/prison':
    print('gamma/prison')
    from pettingzoo.gamma import prison
    prison = prison.env()
    api_test.api_test(prison, render=True, manual_control=True)
    bombardment_test.bombardment_test(prison)
    performance_benchmark.performance_benchmark(prison)

if sys.argv[1] == 'gamma/prospector':
    print('gamma/prospector')
    from pettingzoo.gamma import prospector
    prospector = prospector.env()
    api_test.api_test(prospector, render=True, manual_control=True)
    bombardment_test.bombardment_test(prospector)
    performance_benchmark.performance_benchmark(prospector)

# mpe

if sys.argv[1] == 'mpe/simple':
    print('mpe/simple')
    from pettingzoo.mpe import simple
    simple = simple.env()
    api_test.api_test(simple, render=True, manual_control=False)
    bombardment_test.bombardment_test(simple)
    performance_benchmark.performance_benchmark(simple)

if sys.argv[1] == 'mpe/simple_adversary':
    print('mpe/simple_adversary')
    from pettingzoo.mpe import simple_adversary
    simple_adversary = simple_adversary.env()
    api_test.api_test(simple_adversary, render=True, manual_control=False)
    bombardment_test.bombardment_test(simple_adversary)
    performance_benchmark.performance_benchmark(simple_adversary)

if sys.argv[1] == 'mpe/simple_crypto':
    print('mpe/simple_crypto')
    from pettingzoo.mpe import simple_crypto
    simple_crypto = simple_crypto.env()
    api_test.api_test(simple_crypto, render=True, manual_control=False)
    bombardment_test.bombardment_test(simple_crypto)
    performance_benchmark.performance_benchmark(simple_crypto)

if sys.argv[1] == 'mpe/simple_push':
    print('mpe/simple_push')
    from pettingzoo.mpe import simple_push
    simple_push = simple_push.env()
    api_test.api_test(simple_push, render=True, manual_control=False)
    bombardment_test.bombardment_test(simple_push)
    performance_benchmark.performance_benchmark(simple_push)

if sys.argv[1] == 'mpe/simple_reference':
    print('mpe/simple_reference')
    from pettingzoo.mpe import simple_reference
    simple_reference = simple_reference.env()
    api_test.api_test(simple_reference, render=True, manual_control=False)
    bombardment_test.bombardment_test(simple_reference)
    performance_benchmark.performance_benchmark(simple_reference)

if sys.argv[1] == 'mpe/simple_speak_listener':
    print('mpe/simple_speak_listener')
    from pettingzoo.mpe import simple_speak_listener
    simple_speak_listener = simple_speak_listener.env()
    api_test.api_test(simple_speak_listener, render=True, manual_control=False)
    bombardment_test.bombardment_test(simple_speak_listener)
    performance_benchmark.performance_benchmark(simple_speak_listener)

if sys.argv[1] == 'mpe/simple_spread':
    print('mpe/simple_spread')
    from pettingzoo.mpe import simple_spread
    simple_spread = simple_spread.env()
    api_test.api_test(simple_spread, render=True, manual_control=False)
    bombardment_test.bombardment_test(simple_spread)
    performance_benchmark.performance_benchmark(simple_spread)

if sys.argv[1] == 'mpe/simple_tag':
    print('mpe/simple_tag')
    from pettingzoo.mpe import simple_tag
    simple_tag = simple_tag.env()
    api_test.api_test(simple_tag, render=True, manual_control=False)
    bombardment_test.bombardment_test(simple_tag)
    performance_benchmark.performance_benchmark(simple_tag)

if sys.argv[1] == 'mpe/simple_world_comm':
    print('mpe/simple_world_comm')
    from pettingzoo.mpe import simple_world_comm
    simple_world_comm = simple_world_comm.env()
    api_test.api_test(simple_world_comm, render=True, manual_control=False)
    bombardment_test.bombardment_test(simple_world_comm)
    performance_benchmark.performance_benchmark(simple_world_comm)

# sisl

if sys.argv[1] == 'sisl/multiwalker':
    print('sisl/multiwalker')
    from pettingzoo.sisl import multiwalker
    multiwalker = multiwalker.env()
    api_test.api_test(multiwalker, render=True, manual_control=False)
    bombardment_test.bombardment_test(multiwalker)
    performance_benchmark.performance_benchmark(multiwalker)

if sys.argv[1] == 'sisl/pursuit':
    print('sisl/pursuit')
    from pettingzoo.sisl import pursuit
    pursuit = pursuit.env()
    api_test.api_test(pursuit, render=True, manual_control=False)
    bombardment_test.bombardment_test(pursuit)
    performance_benchmark.performance_benchmark(pursuit)

if sys.argv[1] == 'sisl/waterworld':
    print('sisl/waterworld')
    from pettingzoo.sisl import waterworld
    waterworld = waterworld.env()
    api_test.api_test(waterworld, render=True, manual_control=False)
    bombardment_test.bombardment_test(waterworld)
    performance_benchmark.performance_benchmark(waterworld)
