#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 28 00:37:35 2018

@author: Arpit
"""

from games.t3Game import T3Game
from environment import Environment
from players.minimaxT3Player import MinimaxT3Player
from players.qPlayer import QPlayer
from brains.qBrain import QBrain
from envThread import EnvThread
from memory.pMemory import PMemory

isConv = False
layers = [
	{'filters':16, 'kernel_size': (2,2), 'size':24}
	 , {'filters':16, 'kernel_size': (2,2), 'size':24}
	]

game = T3Game(3, isConv=isConv)

brain = QBrain('t3ADQN', game, layers=layers, load_weights=False, plotModel=True)

player_config = {"memory":PMemory(1000), "goodMemory":PMemory(1000), "targetNet":False,
                "batch_size":64, "gamma":0.90, "n_step":6}
epsilons = [0.05, 0.10, 0.15, 0.20]

i = 0
threads = []
while i < 4:
    game = T3Game(3, name=i, isConv=isConv)
    p1 = QPlayer(i, game, brain=brain, epsilon=epsilons[i], **player_config)
    p2 = MinimaxT3Player(2, game, epsilon=0)
    env = Environment(game, p1, p2)
    threads.append(EnvThread(env))
    i += 1

for t in threads:
    t.start()
