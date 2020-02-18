#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 22:37:40 2018

@author: Arpit
"""
__all__ = ["cached"]

import os, pickle

debug = False

def cached(func):
    func.cacheInfo = {'hits':0, 'misses':0}
    dictName = "dicts/" + func.__name__ + ".pickle"
    if debug: print(dictName)
    
    def cache_info():
        print(func.cacheInfo)
    
    def wrapper(*args):
        try:
            result =  func.cache[args]
            if debug: print("Hit the cache for args: " + str(args))
            func.cacheInfo['hits'] += 1
            return result
        
        except KeyError:
            func.cacheInfo['misses'] += 1
            if debug: print("Missed the cache for args: " + str(args))
            func.cache[args] = result = func(*args)
            
            if func.cacheInfo['misses'] % 1000 == 0:
                try:
                    with open(dictName, 'wb') as handle:
                        if debug: print("Dumping the cache")
                        if len(func.cache):
                            pickle.dump(func.cache, handle, protocol=pickle.HIGHEST_PROTOCOL)
                except Exception as e:
                    print("Pickle dump error: " + str(e))
                
            return result 

    #Setting up cache to wrapper so that it's accessible from outside.
    #Loading existing cache or setting a new one.
    if os.path.exists(dictName):
        print("Dict " + dictName + " loaded")
        with open(dictName, 'rb') as handle:
            wrapper.cache = func.cache = pickle.load(handle)
    else:
        if debug: print("No cache was found")
        wrapper.cache = func.cache = {}

    wrapper.cache_info = cache_info
    
    return wrapper
