#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  9 14:54:24 2018

@author: Arpit
"""

class DictTree():
    def __init__(self):
        self.flushDicts()
    
    def __getitem__(self, item):
        if item == "P":
            return self.P
        elif item == "Q":
            return self.Q
        elif item == "V":
            return self.V
        elif item == "N":
            return self.N
    
    def flushDicts(self):
        self.P = {}
        self.Q = {}
        self.V = {}
        self.N = {}
