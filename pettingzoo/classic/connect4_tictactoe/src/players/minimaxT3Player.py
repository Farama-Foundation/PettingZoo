#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 16:53:32 2018

@author: Arpit
"""
from players.player import Player
from games.t3MinMax import TicTacToeBrain as T3M2
from functools import lru_cache
import numpy as np
import random

class MinimaxT3Player(Player):
    
    def __init__(self, name, game, **kwargs):
        super().__init__(name, game, **kwargs)
        self.rand = kwargs['rand'] if "rand" in kwargs else True
        self.solver = T3M2()
    
    def act(self, game):
        if np.random.uniform() < self.epsilon:
            action = self.getRandomMove(game.getIllMoves())
        else:
            action = self.getBestMove(game.toString())
        
        return action
    
    def observe(self, sample, game):
        super().observe(game)
        
    def train(self, game):
        pass
    
    def getBestMove(self, gameStr):
        moves = self.getBestMoves(gameStr)
        action = moves[0] if not self.rand else random.sample(moves, 1)[0]
        return action
    
    @lru_cache(maxsize=None)
    def getBestMoves(self, gameStr):
        moves = self.solver.getScores(gameStr)
        
        choices = []
        maxi = float("-inf")
        for index, value in enumerate(moves):
            if maxi <= value:
                if maxi < value:
                    choices = [index]
                    maxi = value
                else:
                    choices.append(index)
        
        return choices
