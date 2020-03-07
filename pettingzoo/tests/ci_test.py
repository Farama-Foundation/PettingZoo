import pettingzoo.tests.api_test as api_test
import sys

# classic

if sys.argv[1] == 'classic/backgammon':
    from pettingzoo.classic import backgammon
    backgammon = backgammon.env()
    api_test.api_test(backgammon)

if sys.argv[1] == 'classic/checkers':
    from pettingzoo.classic import checkers
    checkers = checkers.env()
    api_test.api_test(checkers)

if sys.argv[1] == 'classic/chess':
    from pettingzoo.classic import chess
    chesd = chess.env()
    api_test.api_test(chess)

if sys.argv[1] == 'classic/connect_four':
    from pettingzoo.classic import connect_four
    connect_four = connect_four.env()
    api_test.api_test(connect_four)

if sys.argv[1] == 'classic/dou_dizhu':
    from pettingzoo.classic import dou_dizhu
    dou_dizhu = dou_dizhu.env()
    api_test.api_test(dou_dizhu)

if sys.argv[1] == 'classic/go':
    from pettingzoo.classic import go
    go = go.env()
    api_test.api_test(go)

if sys.argv[1] == 'classic/leduc_holdem':
    from pettingzoo.classic import leduc_holdem
    leduc_holdem = leduc_holdem.env()
    api_test.api_test(leduc_holdem)

if sys.argv[1] == 'classic/mahjong':
    from pettingzoo.classic import mahjong
    mahjong = mahjong.env()
    api_test.api_test(mahjong)

if sys.argv[1] == 'classic/rps':
    from pettingzoo.classic import rps
    rps = rps.env()
    api_test.api_test(rps)

if sys.argv[1] == 'classic/rpsls':
    from pettingzoo.classic import rpsls
    rpsls = rpsls.env()
    api_test.api_test(rpsls)

if sys.argv[1] == 'classic/texas_holdem':
    from pettingzoo.classic import texas_holdem
    texas_holdem = texas_holdem.env()
    api_test.api_test(texas_holdem)

if sys.argv[1] == 'classic/texas_holdem_no_limit':
    from pettingzoo.classic import texas_holdem_no_limit
    texas_holdem_no_limit = texas_holdem_no_limit.env()
    api_test.api_test(texas_holdem_no_limit)

if sys.argv[1] == 'classic/tic_tac_toe':
    from pettingzoo.gamma import tic_tac_toe
    tic_tac_toe = tic_tac_toe.env()
    api_test.api_test(tic_tac_toe)

if sys.argv[1] == 'classic/uno':
    from pettingzoo.classic import uno
    uno = uno.env()
    api_test.api_test(uno)

# gamma

if sys.argv[1] == 'gamma/cooperative_pong':
    from pettingzoo.gamma import cooperative_pong
    cooperative_pong = cooperative_pong.env()
    api_test.api_test(cooperative_pong, render=True, manual_control=True)

if sys.argv[1] == 'gamma/knights_archers_zombies':
    from pettingzoo.gamma import knights_archers_zombies
    knights_archers_zombies = knights_archers_zombies.env()
    api_test.api_test(knights_archers_zombies, render=True, manual_control=True)

if sys.argv[1] == 'gamma/pistonball':
    from pettingzoo.gamma import pistonball
    pistonball = pistonball.env()
    api_test.api_test(pistonball, render=True, manual_control=True)

if sys.argv[1] == 'gamma/prison':
    from pettingzoo.gamma import prison
    prison = prison.env()
    api_test.api_test(prison, render=True, manual_control=True)

if sys.argv[1] == 'gamma/prospector':
    from pettingzoo.gamma import prospector
    prospector = prospector.env()
    api_test.api_test(prospector, render=True, manual_control=True)

# mpe

if sys.argv[1] == 'mpe/simple':
    from pettingzoo.mpe import simple
    simple = simple.env()
    api_test.api_test(simple, render=True, manual_control=False)

if sys.argv[1] == 'mpe/simple_adversary':
    from pettingzoo.mpe import simple_adversary
    simple_adversary = simple_adversary.env()
    api_test.api_test(simple_adversary, render=True, manual_control=False)

if sys.argv[1] == 'mpe/simple_crypto':
    from pettingzoo.mpe import simple_crypto
    simple_crypto = simple_crypto.env()
    api_test.api_test(simple_crypto, render=True, manual_control=False)

if sys.argv[1] == 'mpe/simple_push':
    from pettingzoo.mpe import simple_push
    simple_push = simple_push.env()
    api_test.api_test(simple_push, render=True, manual_control=False)

if sys.argv[1] == 'mpe/simple_reference':
    from pettingzoo.mpe import simple_reference
    simple_reference = simple_reference.env()
    api_test.api_test(simple_reference, render=True, manual_control=False)

if sys.argv[1] == 'mpe/simple_speak_listener':
    from pettingzoo.mpe import simple_speak_listener
    simple_speak_listener = simple_speak_listener.env()
    api_test.api_test(simple_speak_listener, render=True, manual_control=False)

if sys.argv[1] == 'mpe/simple_spread':
    from pettingzoo.mpe import simple_spread
    simple_spread = simple_spread.env()
    api_test.api_test(simple_spread, render=True, manual_control=False)

if sys.argv[1] == 'mpe/simple_tag':
    from pettingzoo.mpe import simple_tag
    simple_tag = simple_tag.env()
    api_test.api_test(simple_tag, render=True, manual_control=False)

if sys.argv[1] == 'mpe/simple_world_comm':
    from pettingzoo.mpe import simple_world_comm
    simple_world_comm = simple_world_comm.env()
    api_test.api_test(simple_world_comm, render=True, manual_control=False)

# sisl

if sys.argv[1] == 'sisl/multiwalker':
    from pettingzoo.sisl import multiwalker
    multiwalker = multiwalker.env()
    api_test.api_test(multiwalker, render=True, manual_control=False)

if sys.argv[1] == 'sisl/pursuit':
    from pettingzoo.sisl import pursuit
    pursuit = pursuit.env()
    api_test.api_test(pursuit, render=True, manual_control=False)

if sys.argv[1] == 'sisl/waterworld':
    from pettingzoo.sisl import waterworld
    waterworld = waterworld.env()
    api_test.api_test(waterworld, render=True, manual_control=False)