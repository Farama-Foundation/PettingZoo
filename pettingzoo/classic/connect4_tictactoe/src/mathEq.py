#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 17:29:15 2018

@author: Arpit
"""
import math

class MathEq:
    def __init__(self, params):
        self.type = params['type'] if "type" in params else 0

        if self.type == 1:
            self.eqNo = params['eqNo']
        else:
            self.min = params['min']
            self.max = params['max']
            self.rate = params['lambda']
        
    def getValue(self, x):
        if self.type == 1:
            if self.eqNo == 1:
                value = -0.8242347 + (0.99722 - -0.8242347)/(1 + (x/97103.41) ** 0.6462744)
            elif self.eqNo == 2:
                value = -0.2542789 + (0.9955262 - -0.2542789)/(1 + (x/50457.89) ** 0.9100507)
            elif self.eqNo == 3:
                value = -0.06603804 + (0.9999994 - -0.06603804)/(1 + (x/2580.584) ** 0.6631246)
            elif self.eqNo == 4:
                value = -0.4693555 + (0.9999012 - -0.4693555)/(1 + (x/30750.87) ** 0.4416366)
            elif self.eqNo == 5:
                value = -0.124753 + (0.3994527 - -0.124753)/(1 + (x/47209.89) ** 0.9580051)
        else:
            value = self.min + (self.max - self.min) * math.exp(-1 * self.rate * x)
        
        return value
