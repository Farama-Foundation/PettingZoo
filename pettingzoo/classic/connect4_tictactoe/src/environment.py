#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 14:29:37 2018

@author: Arpit
"""
from graphPlot import GraphPlot
import time, os
from evaluator import Evaluator
import numpy as np
import threading
import logger as lg

class Environment():
    lock = threading.Lock()

    def __init__(self, game, p1, p2, **kwargs):
        self.startTime = time.time()

        self.game = game
        self.p1 = p1
        self.p2 = p2
        self.clearStats()
        self.training = kwargs['training'] if "training" in kwargs else True
        self.observing = kwargs['observing'] if "observing" in kwargs else True
        self.thread = kwargs['thread'] if "thread" in kwargs else False

        self.ePlotFlag = kwargs['ePlotFlag'] if "ePlotFlag" in kwargs else False
        self.gPlotFlag = kwargs['gPlotFlag'] if "gPlotFlag" in kwargs else True
        if self.ePlotFlag:
            self.ePlot = GraphPlot("e-rate-" + str(self.game.name), 1, 2, ["p1-e", "p2-e"])
        if self.gPlotFlag:
            self.gPlot = GraphPlot("game-stats-" + str(self.game.name), 1, 3, list(self.winStats[1].keys()))
        
        self.switchFTP = kwargs['switchFTP'] if "switchFTP" in kwargs else True
        self.switchFlag = 0

        self.evaluate = kwargs['evaluate'] if "evaluate" in kwargs else False
        if self.evaluate:
            self.newModel = self.p1.brain.name
            self.oldModel = str(self.newModel) + "_old"
            self.evaluator = Evaluator(self.game, self.newModel, self.oldModel)
            self.evalEvery = kwargs['evalEvery'] if "evalEvery" in kwargs else 100

    def run(self):
        while True:
            self.runGame()
            lg.main.info("Game Finished\n%s", self.game.gameState)
            lg.main.info("Win Stats: %s", self.winStats)

            if self.game.gameCnt % 100 == 0:
                self.printEnv()
                if self.ePlotFlag: self.ePlot.save()
                if self.gPlotFlag: self.gPlot.save()
                with self.lock:
                    if self.game.gameCnt % 1000 == 0: self.p1.brain.save()

            if self.evaluate and self.game.gameCnt % self.evalEvery == 0:
                if os.path.exists(self.oldModel + ".h5"):
                    self.p1.brain.save()
                    result = self.evaluator.evaluate()
                    if not result:
                        self.p1.brain.load_weights(self.oldModel)
                
                self.p1.brain.save(self.oldModel)

            if self.thread: break
        
    def runGame(self):
        self.game.newGame()
        
        if self.switchFTP:
            self.switchFlag = 1 if self.game.gameCnt % 2 == 0 else 0
            
        lastS = None
        lastA = None
        while not self.game.isOver():
            p = self.getNextPlayer()
            
            s = self.game.getCurrentState()
            a = p.act(self.game)
            self.game.step(a)
    
            if lastS is not None:
                self.teachLastPlayer(lastS, lastA)
            
            lastS = s
            lastA = a
        
        """
        Dummy switch so that the player who made the last action could take the reward.
        """
        self.game.switchTurn() 
        self.teachLastPlayer(lastS, lastA)
        
        winner = self.game.getWinner()
        self.updateStats(winner)

    """
    If a player has played then the previous turn player can get their rewards,
    observe sample and train.
    """
    def teachLastPlayer(self, lastS, lastA):
        p = self.getNextPlayer()
        
        r = self.game.getReward(self.game.toPlay)
        s_ = self.game.getCurrentState() if not self.game.isOver() else None
    
        sample = (lastS, lastA, r, s_)
        
        if self.observing:
            p.observe(sample, self.game)
        if self.training:
            p.train(self.game)
        
    def getNextPlayer(self):
        return self.p1 if (self.game.turnCnt + self.switchFlag) % 2 == 0 else self.p2
    
    def getTotalWins(self, player=None):
        wins = np.add(list(self.winStats[1].values()), list(self.winStats[2].values()))
        if player is None:
            return wins
        else:
            return wins[player - 1]
        
    def updateStats(self, winner):
        """
        If winner is 1 but p2 was first to play(FTP) then the winner is p2.
        """
        if (winner == 1 or winner == 2) and self.switchFlag == 1:
            winner = 1 if winner == 2 else 2
            
        if winner == 1:
            self.winner = 'p1'
        elif winner == 2:
            self.winner = 'p2'
        else:
            self.winner = 'Draw'
            
        self.winStats[1 if self.switchFlag == 0 else 2][self.winner] += 1
        
    def clearStats(self):
        self.winStats = {1:{'p1':0, 'p2':0, 'Draw':0}, 2:{'p1':0, 'p2':0, 'Draw':0}}

    def printEnv(self):
        self.game.printGame()
        print ("p1-e: " + str(self.p1.epsilon))
        print ("p2-e: " + str(self.p2.epsilon))
        if self.p1.alpha is not None:
            print ("Learning Rate: " + str(self.p1.alpha))
        print(self.winStats)
        print("Time since beginning: " + str(time.time() - self.startTime))
        print("#"*50)
        
        if self.ePlotFlag: self.ePlot.add(self.game.gameCnt, [self.p1.epsilon, self.p2.epsilon])
        if self.gPlotFlag: self.gPlot.add(self.game.gameCnt, self.getTotalWins())
        self.clearStats()
