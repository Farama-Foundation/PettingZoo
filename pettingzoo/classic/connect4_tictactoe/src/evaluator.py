#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 11 20:19:38 2018

@author: Arpit
"""
from players.testPlayer import TestPlayer
import logger as lg

class Evaluator:
    def __init__(self, game, model1, model2):
        self.game = game
        self.model1 = model1
        self.model2 = model2
        self.t1 = None
        self.t2 = None
        self.env = None
    
    def evaluate(self):
        if self.t1 is None:
            from environment import Environment
            self.t1 = TestPlayer(self.model1, self.game, epsilon=0.05)
            self.t2 = TestPlayer(self.model2, self.game, epsilon=0.05)
            self.env = Environment(self.game, self.t1, self.t2, training=False, observing=False)
        else:
            self.t1.brain.load_weights(self.model1)
            self.t2.brain.load_weights(self.model2)
        
        self.game.save()
        self.game.gameCnt = 0
        for _ in range(500):
           self.env.runGame()
           
        wins = self.env.getTotalWins()
        if wins[0]/(wins[0] + wins[1]) > 0.50:
            print("The new model is better!")
            result = True
        else:
            print("The new model is not better!")
            result = False
            
        self.env.printEnv()
        lg.main.info("Evaluator Result: %s", self.env.winStats)
        self.game.load()
        return result
