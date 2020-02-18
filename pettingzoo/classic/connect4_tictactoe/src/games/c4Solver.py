#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 18:50:06 2018

@author: Arpit
"""
import requests, yaml, os, random, threading
from cache import cached
from functools import lru_cache
from threading import Thread

FIFO = "games/c4solver67-pipe-in"
FIFO_OUT = "games/c4solver67-pipe-out"
FILE = "games/out.txt"
LOCK = "games/lock"
debug = False

threadLock = threading.Lock()

def readFifo():
    global output, mod
    
    while True:
        with open(FIFO_OUT) as fifo:
            output = fifo.read()
            mod = True

mod = False
output = ""
#thread = Thread(target = readFifo)
#thread.start()

def solve(game, rand):
    gameString = ""
    for i in game.toString():
        gameString += str(int(i) + 1)

    if game.rows == 6 and game.columns == 7:
        moves = miniMax6X7Shell(gameString)  
    elif game.rows == 5 and game.columns == 6:
        moves = miniMax5X6Shell(gameString)
    elif game.rows == 4 and game.columns == 5:
        moves = miniMax4X5Shell(gameString)

    if rand:
        action = random.sample(moves, 1)[0]
    else:
        action = moves[0]
        
    return action

def miniMax5X6Ntuple(gameString):
    return nTuple(gameString, True)

def miniMax6X7Ntuple(gameString):
    return nTuple(gameString, False)

def nTuple(gameString, invertScores=False):
    with threadLock:
        if os.path.exists(FILE):
            modTime = os.path.getmtime(FILE)
        else:
            modTime = 0
            
        command = "echo \"" + gameString + "\" > " + FIFO
        os.popen(command)
    
        while not os.path.exists(FILE) or modTime == os.path.getmtime(FILE) or os.path.exists(LOCK):
            pass
    
        file = open(FILE, "r")
        scores = list(map(int, file.read().split()))

        if invertScores:
            scores = [i * -1 for i in scores]    
    
        return getBestMoves(scores)

def fifoOut(gameString):
    global mod;
    
    with threadLock:
        mod = False
    
        command = "echo \"" + gameString + "\" > " + FIFO
        os.popen(command)
    
        while not mod: pass

        scores = list(map(int, output.split()))
        scores = [i * -1 for i in scores]    
        return getBestMoves(scores)

@cached
def miniMax4X5Shell(gameString):
    if debug: print("miniMax4X5Shell called")
    scores = getScores("./games/c4solver45", gameString)
    return getBestMoves(scores)

@cached
def miniMax5X6Shell(gameString):
    if debug: print("miniMax5X6Shell called")
    return miniMax5X6Ntuple(gameString)

#    scores = getScores("./games/c4solver56", gameString)
#    return getBestMoves(scores)

@cached
def miniMax6X7Shell(gameString):
    if debug: print("miniMax6X7Shell called")
    if False and len(gameString) > 11:
        scores = getScores("./games/c4solver67", gameString)
    else:
        return miniMax6X7API(gameString)
    return getBestMoves(scores)

def miniMax6X7API(gameString):
    if debug: print("miniMax6X7API called")
    r = requests.get('http://connect4.gamesolver.org/solve?pos=' + str(gameString))
    data = yaml.safe_load(r.text)
    scores = [-99 if i == 100 else i for i in data['score']]
    if debug: print(scores)

    return getBestMoves(scores)

def getScores(solver, gameString):
    if gameString == "":
        gameString = "null"
    
    command = solver + " " + gameString
    if debug: print(command)

    moves = os.popen(command).read().split()
    moves = list(map(int, moves))
    moves = [i * -1 for i in moves]    
    
    if debug: print(moves)
    return moves
    
def getBestMoves(moves):
    choices = []
    maxi = float("-inf")
    for index, value in enumerate(moves):
        if maxi <= value:
            if maxi<value:
                choices = [index]
                maxi = value
            else:
                choices.append(index)
    
    if debug: print(choices)
    return choices
