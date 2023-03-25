# -*- coding: utf-8 -*-
"""ResNet.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1VOu-YtbSDcuF7HGvHtqqjgF-_lTUfdoO
"""

import tensorflow as tf
import numpy as np
from keras.models import Model
from keras.layers import Dense, Flatten, BatchNormalization, Dropout
from keras.optimizers import Adam

class ResNet(tf.keras.Model):
    def __init__(self, dropout_rate=0.2):
        super().__init__()

        self.res = tf.keras.applications.ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

        for layer in self.res.layers[:-10]:
            layer.trainable = False

        self.optimizer = Adam(learning_rate=0.0001)
        self.loss_function = tf.keras.losses.CategoricalCrossentropy()
        self.metrics_list = [
            tf.keras.metrics.Mean(name='loss'),
            tf.keras.metrics.CategoricalAccuracy(name='accuracy')
            ]
        
        self.dropout_rate = dropout_rate

        self.custom_layers = [
                         Flatten(),
                         Dense(512, activation='relu'),
                         BatchNormalization(),
                         Dropout(self.dropout_rate),
                         Dense(256, activation='relu'),
                         BatchNormalization(),
                         Dropout(self.dropout_rate),
                         Dense(4, activation='softmax')
                         ]
        
    def call(self, x, training=False):
        
        for layer in self.custom_layers:
            if isinstance(layer, (BatchNormalization, Dropout)):
                x = layer(x, trainable=training)
            else:
                x = layer(x)             
        return x
    
    def reset_metrics(self):
        """Function to reset every metric. Necessary for train_loop"""
        for metric in self.metrics_list:
            metric.reset_states()

    @tf.function
    def train(self, input):
        """Training step for ResNet"""
        x,t = input

        with tf.GradientTape() as tape:
            output = self(x, training=True)
            loss = self.loss_function(t, output) + tf.reduce_sum(self.losses)
        gradients = tape.gradient(loss, self.trainable_variables)
        self.optimizer.apply_gradients(zip(gradients, self.trainable_variables))

        self.metrics_list[0].update_state(values=loss)
        self.metrics_list[1].update_state(t, output)
        
        return {m.name:m.result() for m in self.metrics_list}
    
    @tf.function
    def test(self, input):
        """Testing step for ResNet"""
        x,t = input
        output = self(x, training=False)
        loss = self.loss_function(t, output) + tf.reduce_sum(self.losses)

        self.metrics_list[0].update_state(values=loss)
        self.metrics_list[1].update_state(t, output)
        
        return {m.name:m.result() for m in self.metrics_list}
    
    def training_loop(self, train_ds, test_ds, epochs, train_summary_writer, test_summary_writer):
        for e in range(epochs):
            #training
            for data in tqdm.tqdm(train_ds, position = 0, leave = True):
                metrics = self.train_step(data)
                #for scalar metrics: save logs
            with train_summary_writer.as_default(): 
                for metric in self.metrics:
                    tf.summary.scalar(f"{metric.name}", metric.result(), step=e)

            print([f"{key}: {value.numpy()}" for (key, value) in metrics.items()])

            self.reset_metrics()

            #testing
            for data in test_ds:
                metrics = self.test_step(data)

            with val_summary_writer.as_default():
                # for scalar metrics:
                for metric in self.metrics:
                    tf.summary.scalar(f"{metric.name}", metric.result(), step=e)

            print([f"val_{key}: {value.numpy()}" for (key, value) in metrics.items()])

            # reset metric objects
            self.reset_metrics()
