#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 28 00:37:35 2018

@author: Arpit
"""

from games.c4Game import C4Game
from environment import Environment
from players.minimaxC4Player import MinimaxC4Player
from players.qPlayer import QPlayer
import games.c4Solver as C4Solver
from envThread import EnvThread
from memory.pMemory import PMemory
from brains.qBrain import QBrain

ROWS = 6
COLUMNS = 7
isConv = False
layers = [
	{'filters':32, 'kernel_size': (3,3), 'size':48}
	 , {'filters':32, 'kernel_size': (3,3), 'size':48}
	 , {'filters':32, 'kernel_size': (3,3), 'size':48}
	 , {'filters':32, 'kernel_size': (3,3), 'size':48}
	]

game = C4Game(ROWS, COLUMNS, isConv=isConv)
brain = QBrain('c4AsyncDQN', game, layers=layers, load_weights=False, plotModel=True)

player_config = {"memory":PMemory(25000), "goodMemory":PMemory(25000), "targetNet":False,
                "batch_size":32, "gamma":0.99, "n_step":22}
epsilons = [0.05, 0.15, 0.25, 0.35]

i = 0
threads = []
while i < 4:
    game = C4Game(ROWS, COLUMNS, name=i, isConv=isConv)
    p1 = QPlayer(i, game, brain=brain, epsilon=epsilons[i], **player_config)
    p2 = MinimaxC4Player(2, game, epsilon=0, solver=C4Solver)
    env = Environment(game, p1, p2)
    threads.append(EnvThread(env))
    i += 1

for t in threads:
    t.start()
