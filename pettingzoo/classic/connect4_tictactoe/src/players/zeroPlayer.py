#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 14:36:06 2018

@author: Arpit
"""
from players.player import Player
from brains.zeroBrain import ZeroBrain
import numpy as np
import random
import logger as lg

class ZeroPlayer(Player):
    def __init__(self, name, game, **kwargs):
        super().__init__(name, game, **kwargs)
        
        self.tree = kwargs['tree']
        self.longTermMem = kwargs['longTermMem']
        self.simCnt = kwargs["simCnt"] if "simCnt" in kwargs else 100
        self.iterEvery = kwargs['iterEvery'] if "iterEvery" in kwargs else 100
        self.sampleCnt = kwargs['sampleCnt'] if "sampleCnt" in kwargs else 1
        self.tau = kwargs['tau'] if "tau" in kwargs else 1
        self.turnsToTau0 = kwargs['turnsToTau0'] if "turnsToTau0" in kwargs else 4
        self.cpuct = kwargs['cpuct'] if "cpuct" in kwargs else 1
        self.epsilon = kwargs['epsilon'] if "epsilon" in kwargs else 0.25
        self.dirAlpha = kwargs['dirAlpha'] if "dirAlpha" in kwargs else 0.3
        self.miniBatchSize = kwargs['miniBatchSize'] if "miniBatchSize" in kwargs else 2048
        self.gameMem = []
        
        self.brain = kwargs['brain'] if "brain" in kwargs else ZeroBrain(name, game)
        if self.load_weights: self.brain.load_weights()

        lg.main.info("New Zero player initialised!\n%s", self.__dict__)

    def act(self, game):
        s = game.getStateID()
        
        game.save()
        for i in range(self.simCnt):
            self.MCTS(game)
            game.load()
        
        lg.main.debug("Game State:\n%s", game.gameState)
        lg.main.debug("Explored cnt for each action: %s", [self.tree['N'][(s, move)] if move not in game.getIllMoves() and (s, move) in self.tree['N']
               else 0 for move in range(game.actionCnt)])

        pi = [pow(self.tree['N'][(s, move)], 1.0/self.tau)
               if move not in game.getIllMoves() and (s, move) in self.tree['N']
               else 0 for move in range(game.actionCnt)]
        pi = [prob/sum(pi) for prob in pi]
        
        lg.main.debug("Pie: %s", pi)
        
        sample = (game.getCurrentState(), pi, None)
        self.gameMem.append(sample)
        
        lg.main.debug("To play %d", game.toPlay)
        if game.turnCnt > self.turnsToTau0:
            action = np.argmax(pi)
            lg.main.debug("Best action: %d", action)
        else:
            action = np.random.choice(game.actionCnt, p=pi)
            lg.main.debug("Action sample: %d", action)

        return action
    
    def observe(self, sample, game):
        if game.isOver():
            r = sample[2]
            
            idx = np.random.randint(len(self.gameMem))
            lg.main.debug("Game memory len %s", len(self.gameMem))
            lg.main.debug("Game memory sample before: %s", self.gameMem[idx])
            self.gameMem = [(mem[0], mem[1], r) for mem in self.gameMem]
            lg.main.debug("Game memory sample after: %s", self.gameMem[idx])

    def train(self, game):
        if game.isOver():
            lg.main.debug("long term memory len before %s", len(self.longTermMem))
            self.tree.flushDicts()
            self.longTermMem += self.gameMem
            self.gameMem = []
            lg.main.debug("long term memory len after %s", len(self.longTermMem))

            if game.gameCnt % self.iterEvery == 0:
                for _ in range(self.sampleCnt):
                    minibatch = random.sample(self.longTermMem, min(self.miniBatchSize, len(self.longTermMem)))
                    self.brain.train(minibatch)
    
    def MCTS(self, game):
        s = game.getStateID()
        edges = []
        
        addNoiseFlag = True
        while s in self.tree['P'] and not game.isOver():
            self.tree['N'][s] += 1
            
            epsilon = 0
            nu = [0] * game.actionCnt
            if addNoiseFlag:
                epsilon = self.epsilon
                nu = np.random.dirichlet([self.dirAlpha] * game.actionCnt)
                addNoiseFlag = False
            
            bestUCB = float("-inf")
            actions = [a for a in range(game.actionCnt) if a not in game.getIllMoves()]
            
            for a in actions:
                noisyP = (1-epsilon)*self.tree['P'][s][a] + epsilon*nu[a]
                U = self.cpuct * (noisyP) * np.sqrt(self.tree['N'][s])
                Q = 0
                
                if (s, a) in self.tree['Q']:
                    U = U/(1 + self.tree['N'][(s,a)])
                    Q = self.tree['Q'][(s,a)]
                    
                UCB = U + Q
                if UCB > bestUCB:
                    bestUCB = UCB
                    bestAction = a
            
            a = bestAction
            edges.append((s, a))
            game.step(a)
            s = game.getStateID()
                
        if game.isOver():
            V = game.getReward(game.toPlay)
            
        elif s not in self.tree['P']:
            P, V = self.brain.predict(np.array([game.getCurrentState()]))
            self.tree['P'][s] = P
            self.tree['V'][s] = V
            self.tree['N'][s] = 1
       
        lg.main.debug("chosen edges: %s", edges)
        for edge in reversed(edges):
            V *= -1
    
            if edge in self.tree['Q']:
                self.tree['Q'][edge] = (self.tree['Q'][edge] * 
                         self.tree['N'][edge] + V)/(self.tree['N'][edge] + 1)
                self.tree['N'][edge] += 1
            else:
                self.tree['Q'][edge] = V
                self.tree['N'][edge] = 1