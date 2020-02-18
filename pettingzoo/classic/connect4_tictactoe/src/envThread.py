#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 28 20:09:40 2018

@author: Arpit
"""
import threading

class EnvThread(threading.Thread):
    cnt = 0

    def __init__(self, env):
        threading.Thread.__init__(self)
        self.env = env
        self.env.thread = True
        self.stop_signal = False
        self.number = self.cnt
        EnvThread.cnt += 1    
        
    def run(self):
        print("thread " + str(self.number) + " started")
        while not self.stop_signal:
            self.env.run()
        
    def stop(self):
        self.stop_signal = True
