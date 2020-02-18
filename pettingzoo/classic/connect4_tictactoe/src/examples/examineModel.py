#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  2 19:20:07 2018

@author: Arpit
"""
from games.t3Game import T3Game
from games.c4Game import C4Game
from environment import Environment
from players.testPlayer import TestPlayer
from players.humanPlayer import HumanPlayer

scoreAgent = True
modelName = "test"
gameName = "C4"
isConv = False

if gameName == "C4":
    game = C4Game(6, 7, isConv=isConv)
else:
    game = T3Game(3, isConv=isConv)

p1 = TestPlayer(modelName, game)

if scoreAgent:
    if gameName == "C4":
        from players.minimaxC4Player import MinimaxC4Player as M2C4
        p2 = M2C4(1, game, epsilon=0.05)
    else:
        from players.minimaxT3Player import MinimaxT3Player as M2T3
        p2 = M2T3(1, game, epsilon=0.05)
else:
    p2 = HumanPlayer(2, game)

env = Environment(game, p1, p2, training=False, observing=False)
while game.gameCnt < 999:
    env.runGame()
#    if env.winner == 'p1': game.printGame()
env.printEnv()

