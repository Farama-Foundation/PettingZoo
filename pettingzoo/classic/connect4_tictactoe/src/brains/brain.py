#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  9 12:30:56 2018

@author: Arpit
"""
import os.path
from keras.models import load_model
from keras.layers import Dense, Conv2D, Flatten, BatchNormalization, LeakyReLU, add, Input
from keras import regularizers
import tensorflow as tf
from settings import charts_folder
from keras.utils import plot_model

LAYERS = [
	{'filters':25, 'kernel_size': (4,4), 'size':24}
	 , {'filters':25, 'kernel_size': (4,4), 'size':24}
	 , {'filters':25, 'kernel_size': (4,4), 'size':24}
	]

def softmax_cross_entropy_with_logits(y_true, y_pred):
    p = y_pred
    pi = y_true
    
    zero = tf.zeros(shape = tf.shape(pi), dtype=tf.float32)
    where = tf.equal(pi, zero)
    negatives = tf.fill(tf.shape(pi), -100.0)
    p = tf.where(where, negatives, p)
    loss = tf.nn.softmax_cross_entropy_with_logits(labels = pi, logits = p)
    
    return loss

class Brain:
    def __init__(self, name, game, **kwargs):
        self.name = name
        self.stateCnt, self.actionCnt = game.getStateActionCnt()
        self.filename = str(self.name) + '.h5'
        
        self.conv = True if type(self.stateCnt) is tuple else False
        
        self.layers = kwargs['layers'] if "layers" in kwargs else None
        if self.layers is None: self.layers = LAYERS

        self.batch_size = kwargs['batch_size'] if "batch_size" in kwargs else 64
        self.epochs = kwargs['epochs'] if "epochs" in kwargs else 1
        self.reg_const = kwargs['reg_const'] if "reg_const" in kwargs else 1e-4
        self.momentum = kwargs['momentum'] if "momentum" in kwargs else 0.9
        self.learning_rate = kwargs['learning_rate'] if "learning_rate" in kwargs else 1e-3

        self.gamma = kwargs['gamma'] if "gamma" in kwargs else 0.99
        self.n_step = kwargs['n_step'] if "n_step" in kwargs else 1
        self.gamma_n = self.gamma ** self.n_step
        self.min_batch = kwargs['min_batch'] if "min_batch" in kwargs else 256
        
        self.model = kwargs['model'] if "model" in kwargs else self._build_model()
        self.plotModel = kwargs['plotModel'] if "plotModel" in kwargs else False
        
        if self.plotModel:
            plot_model(self.model, show_shapes=True, to_file=charts_folder + 
                       str(self.name) + '_model.png')

    def get_conv_layers(self, bn=True, reg=-1):
        main_input = Input(shape = self.stateCnt, name = 'main_input')
        x = self.conv_layer(main_input, self.layers[0]['filters'], 
                            self.layers[0]['kernel_size'], bn, reg)
        
        if len(self.layers) > 1:
            for h in self.layers[1:]:
                x = self.residual_layer(x, h['filters'], h['kernel_size'], bn, reg)
                
        return main_input, x
        
    def conv_layer(self, x, filters, kernel_size, bn=True, reg=-1):
        if reg == -1:
            reg = regularizers.l2(self.reg_const)

        x = Conv2D(filters = filters, kernel_size = kernel_size, data_format="channels_first",
                   padding = 'same', use_bias=False, activation='linear', 
                   kernel_regularizer = reg)(x)
        if bn: x = BatchNormalization(axis=1)(x)
        x = LeakyReLU()(x)
        return x
    
    def residual_layer(self, input_block, filters, kernel_size, bn=True, reg=-1):
        if reg == -1:
            reg = regularizers.l2(self.reg_const)

        x = self.conv_layer(input_block, filters, kernel_size, bn, reg)
        x = Conv2D(filters = filters, kernel_size = kernel_size, data_format="channels_first",
                   padding = 'same', use_bias=False, activation='linear',
                   kernel_regularizer = reg)(x)
        if bn: x = BatchNormalization(axis=1)(x)
        x = add([input_block, x])
        x = LeakyReLU()(x)
        return x
    
    def dense_layer(self, x, size, activation='linear', name=None, reg=-1):
        if reg == -1:
            reg = regularizers.l2(self.reg_const)
        
        x = Dense(size, use_bias=False, activation=activation, name=name,
                  kernel_regularizer=reg)(x)
        return x
    
    def policy_head(self, x):
        x = self.conv_layer(x, 2, (1,1))
        x = Flatten()(x)
        x = self.dense_layer(x, self.actionCnt, 'softmax', 'policy_head')
        return x

    def predict(self, s):
        return self.model.predict(s)
    
    def predict_p(self, s):
        result = self.predict(s)
        if len(result) > 1:
            return result[0]
        else:
            return result

    def get_weights(self):
        return self.model.get_weights()
    
    def set_weights(self, weights):
        self.model.set_weights(weights)
    
    def load_weights(self, filename=None):
        filename = self.getFileName(filename)

        if os.path.exists(filename):
            self.model.load_weights(filename)
            print (filename + " weights loaded")
        else:
            print("Error: file " + filename + " not found")

    def save(self, filename=None):
        filename = self.getFileName(filename)
        self.model.save(filename)
        
    def getFileName(self, filename):
        if filename is not None:
            filename = str(filename) + '.h5'
        else:
            filename = self.filename

        return filename

    @staticmethod
    def load_model(filename):
        filename = str(filename) + '.h5'

        if os.path.exists(filename):
            model = load_model(filename, custom_objects={'softmax_cross_entropy_with_logits': softmax_cross_entropy_with_logits})
            print(filename + " model loaded")
        else:
            print("Error: file " + filename + " not found")
            
        return model
