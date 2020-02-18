#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 17:52:18 2018

@author: Arpit
"""
import numpy as np
from players.player import Player

class PGPlayer(Player):
    
    def __init__(self, name, game, **kwargs):
        super().__init__(name, game, **kwargs)
        
        if self.brain is None: print("Error: All policy gradient players requrie a master brain")
            
    def act(self, game):
        state = game.getCurrentState()
        illActions = game.getIllMoves()

        if np.random.uniform() < self.epsilon:
            action = self.getRandomMove(illActions)
        else:
            actions = self.brain.predict_p(np.array([state]))[0]
            fActions = self.filterIllMoves(np.copy(actions), illActions)
            action = np.random.choice(self.actionCnt, p=fActions)
            
        return action

    def observe(self, sample, game): # where sample is (s, a, r, s_)
        super().observe(game)
        
        a_cats = np.zeros(self.actionCnt) # turn action into one-hot representation
        a_cats[sample[1]] = 1
        
        self.sarsaMem.append((sample[0], a_cats, sample[2], sample[3]))
        self.updateR(sample[2])
        
        if game.isOver():
            if len(self.sarsaMem) < self.n_step: # if game ends before n steps
                self.increaseR()

            while len(self.sarsaMem) > 0:
                self.brain.train_push(self.getNSample(len(self.sarsaMem)))
                self.R = (self.R - self.sarsaMem[0][2]) / self.gamma
                self.sarsaMem.pop(0)
                
            self.R = 0
            
        if len(self.sarsaMem) >= self.n_step:
            self.brain.train_push(self.getNSample(self.n_step))
            self.R = self.R - self.sarsaMem[0][2]
            self.sarsaMem.pop(0)
        
    def train(self, game):
        pass
    
    def filterIllMoves(self, moves, illMoves):
        for index, move in enumerate(moves):
            if index in illMoves:
                moves[index] = 0 # since this time it's probabilities
            else:
                moves[index] += 1e-5 # in case all legal moves are zero
        
        moves /= moves.sum() # normalize
        return moves
