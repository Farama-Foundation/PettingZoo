#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 15:52:53 2018

@author: Arpit
"""
from players.player import Player
import games.c4Solver as C4Solver
import numpy as np

class MinimaxC4Player(Player):
    
    def __init__(self, name, game, **kwargs):
        super().__init__(name, game, **kwargs)
        
        self.solver = kwargs['solver'] if "solver" in kwargs else C4Solver
        self.rand = kwargs['rand'] if "rand" in kwargs else True
    
    def act(self, game):
        illActions = game.getIllMoves()

        if np.random.uniform() < self.epsilon:
            action = self.getRandomMove(illActions)
        else:
            if len(illActions) == self.actionCnt - 1:#only one legal move left
                action = list(set(range(self.actionCnt)) - set(illActions))[0]
            else:
                action = self.solver.solve(game, self.rand)

        return action
    
    def observe(self, sample, game):
        super().observe(game)
        
    def train(self, game):
        pass
