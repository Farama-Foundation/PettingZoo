#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 17:53:30 2018

@author: Arpit
"""

from brains.brain import Brain
from keras.layers import Input, LeakyReLU, Flatten
from keras.models import Model
import tensorflow as tf
from keras import backend as K

class QBrain(Brain):
    def __init__(self, name, game, **kwargs):
        super().__init__(name, game, **kwargs)

        self.session = tf.Session()
        K.set_session(self.session)
        K.manual_variable_initialization(True)

        self.model._make_predict_function()
        self.model._make_train_function()
        
        self.session.run(tf.global_variables_initializer())
        if "load_weights" in kwargs and kwargs['load_weights']: self.load_weights()

        self.default_graph = tf.get_default_graph()

    def _build_model(self):
        if self.conv:
            main_input, x = self.get_conv_layers(bn=False, reg=None)
            x = self.conv_layer(x, 2, (1,1), bn=False, reg=None)
            x = Flatten()(x)
        else:
            main_input = Input(batch_shape=(None, self.stateCnt))
            
            x = main_input
            if len(self.layers) > 0:
                for h in self.layers:
                    x = self.dense_layer(x, h['size'], reg=None)
                    x = LeakyReLU()(x)
        
        out_actions = self.dense_layer(x, self.actionCnt, reg=None)
        model = Model(inputs=[main_input], outputs=[out_actions])
        model.compile(loss='logcosh', optimizer='rmsprop', metrics=['accuracy'])

        return model
    
    def predict(self, s):
        with self.default_graph.as_default():
            return self.model.predict(s)

    def train(self, x, y, batch_size, verbose):
        with self.default_graph.as_default():
            self.model.fit(x, y, batch_size=batch_size, verbose=verbose)
        
