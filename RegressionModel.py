import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn import preprocessing
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import math
import copy


class RegressionModel:
    def __init__(self):
        self.length_of_sequence = 50
        self.output_neuron = 1
        self.n_hidden = 100

    def train_model(self, x_train, y_train, batch_size, num_epochs):
        model = keras.models.Sequential()
        model.add(keras.layers.LSTM(self.n_hidden, input_shape=(self.length_of_sequence, self.output_neuron)))
        model.add(keras.layers.Dropout(rate=0.2))
        model.add(keras.layers.Dense(units = 1, activation='linear'))
        model.compile(optimizer='adam', loss='mse')
        model.fit(x_train, y_train, batch_size=batch_size, epochs=num_epochs, shuffle=True, verbose=True)
        return model

    def forecast(self, model: keras.models.Sequential, x_test, num_forecast):
        pred = []
        ini_pre = model.predict(x_test[0].reshape(1, x_test[0].shape[0],1))
        test = np.insert(x_test[0], x_test[0].shape[1], ini_pre)
        test = np.delete(test, 0).reshape(1, x_test[0].shape[1],1)
        for i in range(num_forecast):
            pre = model.predict(test)
            pred.append(pre[0][0])
            test = np.insert(test, x_test[0].shape[1], pre)
            test = np.delete(test,0).reshape(1,x_test[0].shape[1], 1)
        return pred


