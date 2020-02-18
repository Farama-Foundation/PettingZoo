#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  4 23:11:45 2018

@author: Arpit
"""

from games.c4Game import C4Game
from environment import Environment
from players.zeroPlayer import ZeroPlayer
from memory.dictTree import DictTree
from brains.zeroBrain import ZeroBrain
from collections import deque

game = C4Game(6, 7, isConv=True)
layers = [
	{'filters':64, 'kernel_size': (4,4)}
	 , {'filters':64, 'kernel_size': (4,4)}
	 , {'filters':64, 'kernel_size': (4,4)}
	 , {'filters':64, 'kernel_size': (4,4)}
	]

player_config = {"tree":DictTree(), "longTermMem":deque(maxlen=20000), 
                 "epsilon":0.25, "dirAlpha":0.3, "simCnt":50, "iterEvery":20,
                 "turnsToTau0":8, "miniBatchSize":2048, "sampleCnt":10}
brain_config = {"learning_rate":0.001, "momentum":0.9, "batch_size":32, "epochs":1,
                "layers":layers, "load_weights":True, "plotModel":True}
env_config = {"switchFTP":False, "evaluate":True, "evalEvery":100}

brain = ZeroBrain("1", game, **brain_config)

p1 = ZeroPlayer(1, game, brain=brain, **player_config)
p2 = ZeroPlayer(2, game, brain=brain, **player_config)
env = Environment(game, p1, p2, **env_config)
env.run()