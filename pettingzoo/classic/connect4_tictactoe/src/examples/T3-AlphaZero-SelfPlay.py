#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  2 19:02:25 2018

@author: Arpit
"""

from games.t3Game import T3Game
from environment import Environment
from players.zeroPlayer import ZeroPlayer
from memory.dictTree import DictTree
from brains.zeroBrain import ZeroBrain
from collections import deque

game = T3Game(3, isConv=False)
layers = [
	{'filters':32, 'kernel_size': (2,2), 'size':24}
	 , {'filters':32, 'kernel_size': (2,2), 'size':24}
	]

player_config = {"tree":DictTree(), "longTermMem":deque(maxlen=5000), 
                 "epsilon":0.20, "dirAlpha":0.3, "simCnt":40, "iterEvery":40,
                 "turnsToTau0":4, "miniBatchSize":2048, "sampleCnt":10}
brain_config = {"learning_rate":0.001, "momentum":0.9, "batch_size":32, "epochs":5,
                "layers":layers, "load_weights":False, "plotModel":True}
env_config = {"switchFTP":False, "evaluate":True, "evalEvery":200}

brain = ZeroBrain("1", game, **brain_config)

p1 = ZeroPlayer(1, game, brain=brain, **player_config)
p2 = ZeroPlayer(2, game, brain=brain, **player_config)
env = Environment(game, p1, p2, **env_config)
env.run()
