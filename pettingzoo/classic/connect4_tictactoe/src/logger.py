#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 12 12:48:21 2018

@author: Arpit
"""
import logging

def setup_logger(name, log_file, level=logging.INFO):
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        logger.addHandler(handler)

    return logger

LOGGER_DISABLED = {
    'main':True
}

main = setup_logger('main', 'logs/main.log', logging.INFO)
main.disabled = LOGGER_DISABLED['main']