#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 16 20:26:39 2018

@author: Arpit
"""

from games.c4Game import C4Game
from environment import Environment
from players.minimaxC4Player import MinimaxC4Player
from players.qPlayer import QPlayer
from brains.qBrain import QBrain

isConv = False
layers = [
        {'filters':16, 'kernel_size': (2,2), 'size':24}
        , {'filters':16, 'kernel_size': (2,2), 'size':24}
	]

game = C4Game(4, 5, isConv=isConv)
brain = QBrain('c4DDQN', game, layers=layers, load_weights=False, plotModel=True)
tBrain = QBrain('c4DDQN', game, layers=layers)

player_config = {"mem_size":25000, "brain":brain, "tBrain":tBrain,
                 "batch_size":64, "gamma":0.90, "n_step":11}

p1 = QPlayer(1, game, **player_config)
p2 = MinimaxC4Player(2, game, epsilon=0)
env = Environment(game, p1, p2)
env.run()