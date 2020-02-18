#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  2 16:15:02 2018

@author: Arpit
"""
from players.player import Player
import time

class HumanPlayer(Player):
    def __init__(self, name, game, **kwargs):
        super().__init__(name, game, **kwargs)

    def act(self, game):
        game.printGame()
        
        while True:
            action = input("Your turn hooman!\nWhere do you wanna play?\nHit [0-" 
                        + str(game.actionCnt - 1) + "]\n")
    
            if not self.hasNumbers(action) or int(action) not in range(game.actionCnt) or int(action) in game.getIllMoves():
                print("Play a legal move!")
                time.sleep(2)
            else:
                break
            
        return int(action)
    
    def observe(self, sample, game):
        pass
    
    def train(self):
        pass
    
    def hasNumbers(self, inputString):
        return any(char.isdigit() for char in inputString)
