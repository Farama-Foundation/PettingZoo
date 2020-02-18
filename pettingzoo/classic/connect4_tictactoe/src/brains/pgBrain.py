#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 17:53:30 2018

@author: Arpit
"""

from brains.brain import Brain
import threading, time
import numpy as np
import tensorflow as tf
from keras import backend as K
from keras.models import Model
from keras.layers import Input, Flatten, LeakyReLU

LOSS_V = .5 # v loss coefficient
LOSS_ENTROPY = .01 # entropy coefficient

class PGBrain(Brain):
    train_queue = [ [], [], [], [], [] ] # s, a, r, s', s' terminal mask
    lock_queue = threading.Lock()
    
    def __init__(self, name, game, **kwargs):
        super().__init__(name, game, **kwargs)

        self.session = tf.Session()
        K.set_session(self.session)
        K.manual_variable_initialization(True)

        self.graph = self._build_graph()
        
        self.session.run(tf.global_variables_initializer())
        if "load_weights" in kwargs and kwargs['load_weights']: self.load_weights()
        
        self.default_graph = tf.get_default_graph()
        self.default_graph.finalize()

    def _build_model(self):
        if self.conv:
            main_input, x = self.get_conv_layers()
            out_value = self.conv_layer(x, 1, (1,1))
            out_value = Flatten()(out_value)
            out_value = self.dense_layer(out_value, 1)
            out_actions = self.policy_head(x)
        else:
            main_input = Input(batch_shape=(None, self.stateCnt))
            
            x = main_input
            if len(self.layers) > 0:
                for h in self.layers:
                    x = self.dense_layer(x, h['size'], reg=None)
                    x = LeakyReLU()(x)
            
            out_value = self.dense_layer(x, 1, reg=None)
            out_actions = self.dense_layer(x, self.actionCnt, 'softmax', 'policy_head', reg=None)

        model = Model(inputs=[main_input], outputs=[out_actions, out_value])
        model._make_predict_function() # have to initialize before threading
        
        return model
    
    def _build_graph(self):
        if type(self.stateCnt) is tuple:
            s_t = tf.placeholder(tf.float32, shape=(None, *self.stateCnt[0:len(self.stateCnt)]))
        else:
            s_t = tf.placeholder(tf.float32, shape=(None, self.stateCnt))

        a_t = tf.placeholder(tf.float32, shape=(None, self.actionCnt))
        q_t = tf.placeholder(tf.float32, shape=(None, 1)) # not immediate, but discounted n step reward
        
        p, v = self.model(s_t)
        
        log_prob = tf.log( tf.reduce_sum(p * a_t, axis=1, keepdims=True) + 1e-10)
        advantage = q_t - v
        
        loss_policy = - log_prob * tf.stop_gradient(advantage) # maximize policy
        loss_value  = LOSS_V * tf.square(advantage) # minimize value error
        entropy = LOSS_ENTROPY * tf.reduce_sum(p * tf.log(p + 1e-10), axis=1, keepdims=True) # maximize entropy (regularization)
        
        loss_total = tf.reduce_mean(loss_policy + loss_value + entropy)
        
        optimizer = tf.train.RMSPropOptimizer(self.learning_rate, decay=.99)
        minimize = optimizer.minimize(loss_total)
        
        return s_t, a_t, q_t, minimize

    def optimize(self):
        if len(self.train_queue[0]) < self.min_batch:
            time.sleep(0) # yield
            return

        with self.lock_queue:
            if len(self.train_queue[0]) < self.min_batch:
                return

            s, a, r, s_, s_mask = self.train_queue
            self.train_queue = [ [], [], [], [], [] ]

        s = np.stack(s)
        a = np.vstack(a)
        r = np.vstack(r)
        s_ = np.stack(s_)
        s_mask = np.vstack(s_mask)

        if len(s) > 5*self.min_batch: print("Optimizer alert! Minimizing batch of %d" % len(s))
        
        v = self.predict_v(s_)
        q = r + self.gamma_n * v * s_mask # set v to 0 where s_ is terminal state
        
        s_t, a_t, q_t, minimize = self.graph
        
        for _ in range(self.epochs):
            self.session.run(minimize, feed_dict={s_t: s, a_t: a, q_t: q})

    def train_push(self, sample):
        s = sample[0]
        a = sample[1]
        r = sample[2]
        s_ = sample[3]

        with self.lock_queue:
            self.train_queue[0].append(s)
            self.train_queue[1].append(a)
            self.train_queue[2].append(r)

            if s_ is None:
                self.train_queue[3].append(np.zeros(self.stateCnt))
                self.train_queue[4].append(0.)
            else:	
                self.train_queue[3].append(s_)
                self.train_queue[4].append(1.)
                
    def predict(self, s):
        with self.default_graph.as_default():
            p, v = self.model.predict(s)
            return p, v

    def predict_p(self, s):
        with self.default_graph.as_default():
            p, v = self.model.predict(s)		
            return p

    def predict_v(self, s):
        with self.default_graph.as_default():
            p, v = self.model.predict(s)		
            return v
