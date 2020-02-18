#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 19:47:06 2018

@author: Arpit
"""
from games.game import Game
import logger as lg

class C4Game(Game):
    
    DRAW_R = 0

    def __init__(self, rows=6, columns=7, **kwargs):
        super().__init__(**kwargs)
        
        self.rows = rows
        self.columns = columns
        self.stateCnt = rows * columns if not self.isConv else (2, rows, columns)
        self.actionCnt = columns
        
        lg.main.info("Initialized C4game! \n %s", self.__dict__)

    def newGame(self):
        super().newGame()
        self.filledColumns = set()
        
    def step(self, column):
        if (super().step(column) < 0):
            return -1
        
        row = 0
        while row < self.rows:
            if self.gameState[row][column] != 0:
                break
            row += 1
        
        row -= 1
        if row == 0:
            self.filledColumns.add(column)
            
        self.updateGameState(row, column)
    
    def updateGameState(self, row, column):
        self.gameState[row][column] = self.toPlay
        self.updateStateForm(row, column)
        self.checkEndStates(row, column)
        self.switchTurn()
    
    def checkEndStates(self, row, column):
        if self.xInARow(row, column, 4):
            self.setWinner(self.toPlay)
            return
            
        self.checkDrawState()
        
    def getIllMoves(self):
        return list(self.filledColumns)
