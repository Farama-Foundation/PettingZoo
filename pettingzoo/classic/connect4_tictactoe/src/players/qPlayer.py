#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 17:52:18 2018

@author: Arpit
"""
import numpy as np
from brains.qBrain import QBrain
from memory.pMemory import PMemory
from players.player import Player
from mathEq import MathEq
import logger as lg

class QPlayer(Player):
    
    def __init__(self, name, game, **kwargs):
        super().__init__(name, game, **kwargs)
                
        self.verbosity = 0
        self.nullState = np.zeros(self.stateCnt)
        self.targetNet = kwargs['targetNet'] if 'targetNet' in kwargs else True
        self.updateTNEvery = kwargs['updateTNEvery'] if 'updateTNEvery' in kwargs else 4000
        
        self.memory = PMemory(self.mem_size) if 'memory' not in kwargs else kwargs['memory']
        self.goodMemory = PMemory(self.mem_size) if 'goodMemory' not in kwargs else kwargs['goodMemory']
        
        if self.brain is None:
            self.brain = QBrain(name, game)
            if self.targetNet:
                self.tBrain = QBrain(str(name) + "_target", game)
        
        if self.load_weights: self.brain.load_weights()
        if self.targetNet: self.updateTargetBrain()
        
        if self.aEq is None and "alpha" not in kwargs:
            self.aEq = MathEq({"min":0.1, "max":0.5, "lambda":0.001})
        if self.aEq is not None:
            self.alpha = self.aEq.getValue(0)

        if self.eEq is None and "epsilon" not in kwargs:
            self.eEq = MathEq({"min":0.05, "max":1, "lambda":0.001})
        if self.eEq is not None:
            self.epsilon = self.eEq.getValue(0)

    def act(self, game):
        state = game.getCurrentState()
        illActions = game.getIllMoves()
        
        if np.random.uniform() < self.epsilon:
            action = self.getRandomMove(illActions)
        else:
            actions = self.brain.predict(np.array([state]))[0]
            lg.main.debug("predicted actions %s", actions)
            fActions = self.filterIllMoves(np.copy(actions), illActions)
            action = np.argmax(fActions)
                
        lg.main.debug("chosen action %d", action)
        return action

    def observe(self, sample, game):
        super().observe(game)
        gameCnt = game.gameCnt
        
        self.sarsaMem.append(sample)
        self.updateR(sample[2])
        
        if game.isOver():
            if len(self.sarsaMem) < self.n_step: # if game ends before n steps
                self.increaseR()
            
            while len(self.sarsaMem) > 0:
                sample = self.getNSample(len(self.sarsaMem))
                self.addToReplayMemory(sample)
                self.R = (self.R - self.sarsaMem[0][2]) / self.gamma
                self.sarsaMem.pop(0)

            self.R = 0
            
            if self.targetNet and gameCnt % self.updateTNEvery == 0:
                self.updateTargetBrain()

        if len(self.sarsaMem) >= self.n_step:
            sample = self.getNSample(len(self.sarsaMem))
            self.addToReplayMemory(sample)
            self.R = self.R - self.sarsaMem[0][2]
            self.sarsaMem.pop(0)
        
    def train(self, game):
        batch = self.goodMemory.sample(int(self.batch_size/2))
        goodMemLen = len(batch)
        
        batch += self.memory.sample(int(self.batch_size - goodMemLen))
        
        if len(batch):
            x, y, errors = self.getTargets(batch)
        
        #update errors
        for i in range(len(batch)):
            idx = batch[i][0]
            memory = self.goodMemory if i < goodMemLen else self.memory 
            memory.update(idx, errors[i])
        
        self.memory.releaseLock()
        self.goodMemory.releaseLock()
        
        if len(batch):
            verbosity = 2 if game.gameCnt % 100 == 0 and not game.isOver() else 0
            self.brain.train(x, y, self.batch_size, verbosity)
        
    def addToReplayMemory(self, sample):
        _, _, errors = self.getTargets([(0, sample)])
        memory = self.goodMemory if sample[2] > 0 else self.memory
        memory.add(errors[0], sample)
        
    def getTargets(self, batch):
        batchLen = len(batch)
        
        states = np.array([ o[1][0] for o in batch ])
        states_ = np.array([ (self.nullState if o[1][3] is None else o[1][3]) for o in batch ])

        p = self.brain.predict(states)
        p_ = self.brain.predict(states_)
        if self.targetNet:
            tp_ = self.tBrain.predict(states_)
        
        x = None
        if type(self.stateCnt) is tuple:
            x = np.zeros((batchLen, *self.stateCnt[0:len(self.stateCnt)]))
        else:
            x = np.zeros((batchLen, self.stateCnt))
        
        y = np.zeros((batchLen, self.actionCnt))
        errors = np.zeros(batchLen)

        for i in range(batchLen):
            o = batch[i][1]
            s = o[0]; a = o[1]; r = o[2]; s_ = o[3]
            
            t = p[i]
            oldVal = t[a]
            if s_ is None:
                t[a] += (r - t[a]) * self.alpha
            else:
                if self.targetNet:
                    t[a] += (max(-1, min(1, r + self.gamma_n * tp_[i][np.argmax(p_[i])])) - t[a]) * self.alpha
                else:
                    t[a] += (max(-1, min(1, r + self.gamma_n * p_[i][np.argmax(p_[i])])) - t[a]) * self.alpha

            x[i] = s
            y[i] = t
            errors[i] = abs(oldVal - t[a])
        
        return (x, y, errors)
            
    def updateTargetBrain(self):
        self.tBrain.set_weights(self.brain.get_weights())
