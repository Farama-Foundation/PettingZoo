#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 16 20:08:09 2018

@author: Arpit
"""

from games.t3Game import T3Game
from environment import Environment
from players.qPlayer import QPlayer
from brains.qBrain import QBrain
from memory.pMemory import PMemory

isConv = False
layers = [
        {'filters':16, 'kernel_size': (2,2), 'size':24}
        , {'filters':16, 'kernel_size': (2,2), 'size':24}
	]

game = T3Game(3, isConv=isConv)
brain = QBrain('t3DQNSelf', game, layers=layers, load_weights=False, plotModel=True)
tBrain = QBrain('t3DQNSelf', game, layers=layers)

player_config = {"memory":PMemory(5000), "goodMemory":PMemory(5000), "brain":brain, 
                 "tBrain":tBrain, "batch_size":64, "gamma":0.90, "n_step":6, "epsilon":0.1}

p1 = QPlayer(1, game, **player_config)
p2 = QPlayer(2, game, **player_config)
env = Environment(game, p1, p2, switchFTP=False)
env.run()