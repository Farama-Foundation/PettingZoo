#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 13:42:11 2018

@author: Arpit
"""

from abc import ABC, abstractmethod
import numpy as np
import copy
import logger as lg

class Game(ABC):
    WINNER_R = 1
    LOSER_R = -1
    DELTAS = {
            "N":(0, -1),
            "NE":(1, -1),
            "NW":(-1, -1),
            "E":(1, 0),
            "W":(-1, 0),
            "SE":(1, 1),
            "SW":(-1, 1),
            "S":(0, 1)
        }
    DIRECTIONS = [('N', 'S'), ('E', 'W'), ('NE', 'SW'), ('SE', 'NW')]

    def __init__(self, **kwargs):
        self.name = kwargs['name'] if "name" in kwargs else "game"
        self.isConv = kwargs['isConv'] if "isConv" in kwargs else False
        self.gameCnt = 0
    
    @abstractmethod
    def newGame(self):
        self.movesHistory = ""
        self.over = False
        self.rewards = {}
        self.gameCnt += 1
        self.toPlay = 1
        self.turnCnt = 0
        self.gameState = np.zeros((self.rows, self.columns), dtype=int)
        self.stateForm = np.zeros(self.stateCnt, dtype=float)
        self.stateForm[True] = 0.01
    
        lg.main.debug("New Game: %s", self.__dict__)
    @abstractmethod
    def step(self, action):
        if self.isOver():
            print ("Game's over already.")
            return -1

        if action in self.getIllMoves():
            print ("Illegal Move!!!!")
            print (self.gameState)
            print (self.movesHistory)
            print ("To play " + str(self.toPlay))
            print ("Wrong move " + str(action))
            self.over = True

            return -2
    
        self.movesHistory += str(action)
        return 1
    
    @abstractmethod
    def getIllMoves(self):
        pass

    def xInARow(self, row, column, length):
        for dpair in self.DIRECTIONS:
            cnt = 1
            for direction in dpair:
                (dy, dx) = self.DELTAS[direction]
                x = row + dx
                y = column + dy
                
                while y>=0 and y<self.columns and x>=0 and x<self.rows:
                    if self.toPlay == self.gameState[x][y]:
                        cnt += 1
                    else:
                        break

                    x += dx
                    y += dy
                
            if cnt >= length:
                return cnt

        return False
    
    def setWinner(self, player):
        self.over = player
        self.rewards[player] = self.WINNER_R
        self.rewards[self.getNextPlayer(player)] = self.LOSER_R
        
    def getWinner(self):
        if self.over:
            return self.over
        else:
            return -1
        
    def updateStateForm(self, row, column):
        if self.isConv:
            self.stateForm[self.toPlay-1][row][column] = 1
        else:
            pos = row * self.columns + column
            if self.toPlay == 2:
                self.stateForm[pos] = -1
            else:
                self.stateForm[pos] = 1
        
    def checkDrawState(self):
        if self.turnCnt == self.rows * self.columns - 1:
            self.over = 3
            self.rewards[self.toPlay] = self.DRAW_R
            self.rewards[self.getNextPlayer(self.toPlay)] = self.DRAW_R
            return True
        return False
    
    def getCurrentState(self):
        return np.copy(self.stateForm)
    
    def getStateID(self):
        return hash(tuple(self.gameState.flatten()))
        
    def getStateActionCnt(self):
        return (self.stateCnt, self.actionCnt)
    
    def isOver(self):
        return True if self.over else False
    
    def switchTurn(self):
        self.turnCnt += 1
        self.toPlay = self.getNextPlayer(self.toPlay)

    def getNextPlayer(self, player):
        if player == 1:
            return 2
        else:
            return 1

    def getReward(self, player):
        if player in self.rewards:
            return self.rewards[player]
        else:
            return 0
        
    def toString(self):
        return self.movesHistory
    
    def save(self):
        self.deleteSavedGame()
        self.savedGame = copy.deepcopy(self.__dict__)
        
    def load(self):
        self.__dict__.update(copy.deepcopy(self.savedGame))
        
    def deleteSavedGame(self):
        if 'savedGame' in self.__dict__:
            del self.__dict__['savedGame']

    def printGame(self):
        print ("Total Games Played: " + str(self.gameCnt))
        print ("Game " + str(self.gameCnt) + ":")
        for x in range(0, self.rows):
            for y in range(0, self.columns):
                print (str(self.gameState[x][y]) + "  ", end='')
            print ("\n")
        print ("Winner: " + str(self.over))
        print ("No. of turns: " + str(self.turnCnt))
