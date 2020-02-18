#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 11 01:32:42 2018

@author: Arpit
"""
import numpy as np
from brains.brain import Brain
from players.player import Player

class TestPlayer(Player):
    def __init__(self, name, game, **kwargs):
        super().__init__(name, game, **kwargs)
        
        self.model = Brain.load_model(name)
        self.brain = kwargs['brain'] if "brain" in kwargs else Brain(name, game, model=self.model)

    def act(self, game):
        illActions = game.getIllMoves()
        
        if np.random.uniform() < self.epsilon:
            action = self.getRandomMove(illActions)
        else:
            moves = self.brain.predict_p(np.array([game.getCurrentState()]))[0]
            moves = self.filterIllMoves(np.copy(moves), illActions)
            action = np.argmax(moves)
        
        return action

    def observe(self, sample, game):
        pass
    
    def train(self, game):
        pass
