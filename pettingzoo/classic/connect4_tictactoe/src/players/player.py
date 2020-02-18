#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 15:47:32 2018

@author: Arpit
"""
from abc import ABC, abstractmethod
import numpy as np

class Player(ABC):
    
    def __init__(self, name, game, **kwargs):
        self.name = name
        self.stateCnt, self.actionCnt = game.getStateActionCnt()
        
        self.R = 0
        self.sarsaMem = []
        self.load_weights = kwargs['load_weights'] if 'load_weights' in kwargs else False

        self.eEq = kwargs['eEq'] if "eEq" in kwargs else None
        self.aEq = kwargs['aEq'] if "aEq" in kwargs else None
        self.epsilon = kwargs['epsilon'] if "epsilon" in kwargs else 0
        self.alpha = kwargs['alpha'] if "alpha" in kwargs else 0.5
        
        self.batch_size = kwargs['batch_size'] if "batch_size" in kwargs else 64
        self.mem_size = kwargs['mem_size'] if "mem_size" in kwargs else 1000
        self.gamma = kwargs['gamma'] if "gamma" in kwargs else 0.99
        self.n_step = kwargs['n_step'] if "n_step" in kwargs else 1
        self.gamma_n = self.gamma ** self.n_step

        self.brain = kwargs['brain'] if 'brain' in kwargs else None
        self.tBrain = kwargs['tBrain'] if 'tBrain' in kwargs else None
        
    @abstractmethod
    def act(self):
        pass
    
    @abstractmethod
    def observe(self, game):
        if game.isOver():
            if self.eEq is not None: self.epsilon = self.eEq.getValue(game.gameCnt)
            if self.aEq is not None: self.alpha = self.aEq.getValue(game.gameCnt)
    
    @abstractmethod
    def train(self):
        pass
    
    def getRandomMove(self, illActions):
        while True:
            action = np.random.choice(self.actionCnt, 1)[0]
            if action not in illActions:
                break

        return action
    
    def updateR(self, r):
        self.R = (self.R + self.gamma_n*r)/self.gamma
        
    def increaseR(self):
        cnt = self.n_step - len(self.sarsaMem)
        while cnt:
            self.R /= self.gamma
            cnt -= 1
                    
    def getNSample(self, n):
        s, a, _, _  = self.sarsaMem[0]
        _, _, _, s_ = self.sarsaMem[n-1]

        return (s, a, self.R, s_)
    
    def filterIllMoves(self, moves, illMoves):
        for index, move in enumerate(moves):
            if index in illMoves:
                moves[index] = float("-inf")
        
        return moves
