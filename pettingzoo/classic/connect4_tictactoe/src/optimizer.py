#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 19:36:30 2018

@author: Arpit
"""
import threading

class Optimizer(threading.Thread):
    cnt = 0
    stop_signal = False

    def __init__(self, brain):
        self.brain = brain
        threading.Thread.__init__(self)
        self.number = self.cnt
        Optimizer.cnt += 1    

    def run(self):
        print("Opt. thread " + str(self.number) + " started")
        while not self.stop_signal:
            self.brain.optimize()

    def stop(self):
        self.stop_signal = True
