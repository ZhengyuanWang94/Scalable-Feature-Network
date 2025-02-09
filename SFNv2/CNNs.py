import math

import keras
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout, Flatten, Conv1D, MaxPooling1D, concatenate, Input
from keras.layers.recurrent import LSTM
from keras import losses, Model
from keras import optimizers
from keras import backend as K

opt = keras.optimizers.sgd(lr=0.0001, decay=1e-6)

def build_model_line(input):

    inputs = Input(shape=input)
    x = Dense(128, activation="relu", kernel_initializer="uniform")(inputs)
    x = Conv1D(filters=24, kernel_size=1, padding='same', activation='relu', kernel_initializer="uniform")(x)
    x = MaxPooling1D(pool_size=2, padding='same')(x)
    x = Conv1D(filters=48, kernel_size=2, padding='same', activation='relu', kernel_initializer="uniform")(x)
    x = MaxPooling1D(pool_size=2, padding='same')(x)
    x = LSTM(40, return_sequences=True)(x)
    x = LSTM(32, return_sequences=False)(x)
    x = Dense(32, activation="relu", kernel_initializer="uniform")(x)
    # model.add(Dropout(0.2))
    x = Dense(1, activation="relu", kernel_initializer="uniform")(x)
    model = Model(inputs=inputs, outputs=x)

    '''
    model = Sequential()
    model.add(Dense(128, input_shape=(input[1], input[0])))
    model.add(Conv1D(filters=24, kernel_size=1, padding='valid', activation='relu', kernel_initializer="uniform"))
    model.add(MaxPooling1D(pool_size=2, padding='same'))
    model.add(Conv1D(filters=48, kernel_size=2, padding='valid', activation='relu', kernel_initializer="uniform"))
    model.add(MaxPooling1D(pool_size=2, padding='same'))
    model.add(LSTM(40, return_sequences=True))
    model.add(LSTM(32, return_sequences=False))
    model.add(Dense(32, activation="relu", kernel_initializer="uniform"))
    # model.add(Dropout(0.2))
    model.add(Dense(1, activation="relu", kernel_initializer="uniform"))
    # model.outputs
    model.compile(loss='mse', optimizer=opt, metrics=['acc'])
    '''
    return model

def build_model_func(input):
    inputs = Input(shape=input)
    x = Dense(128, activation="relu", kernel_initializer="uniform")(inputs)
    x = Conv1D(filters=24, kernel_size=1, padding='same', activation='relu', kernel_initializer="uniform")(x)
    x = MaxPooling1D(pool_size=2, padding='same')(x)
    x = Conv1D(filters=48, kernel_size=2, padding='same', activation='relu', kernel_initializer="uniform")(x)
    x = MaxPooling1D(pool_size=2, padding='same')(x)
    x = LSTM(40, return_sequences=True)(x)
    x = LSTM(32, return_sequences=False)(x)
    x = Dense(32, activation="relu", kernel_initializer="uniform")(x)
    # model.add(Dropout(0.2))
    x = Dense(1, activation="relu", kernel_initializer="uniform")(x)
    model = Model(inputs=inputs, outputs=x)

    '''
    model = Sequential()
    model.add(Dense(128, input_shape=(input[1], input[0])))
    model.add(Conv1D(filters=24, kernel_size=1, padding='valid', activation='relu', kernel_initializer="uniform"))
    model.add(MaxPooling1D(pool_size=2, padding='valid'))
    model.add(Conv1D(filters=48, kernel_size=2, padding='valid', activation='relu', kernel_initializer="uniform"))
    model.add(MaxPooling1D(pool_size=2, padding='valid'))
    model.add(LSTM(40, return_sequences=True))
    model.add(LSTM(32, return_sequences=False))
    model.add(Dense(32, activation="relu", kernel_initializer="uniform"))
    # model.add(Dropout(0.2))
    model.add(Dense(1, activation="relu", kernel_initializer="uniform"))
    # model.outputs
    model.compile(loss='mse', optimizer=opt, metrics=['acc'])
    '''

    return model

'''以下注释掉的是可以单独跑CNN的'''

import keras
import pandas as pd
import numpy as np

dataset = pd.read_csv("./multiscale_dataset/cms/PU_dataset_1.csv", header=None)

amount_of_feature = len(dataset.columns)

# 添加过采样

dataset = dataset.values
print("values")
print(dataset)

# dt = []
# sequence_length = 22
# for index in range(len(dataset) - sequence_length):
#     dt.append(dataset[index : index + sequence_length])
# print(dt)
#

dataset = np.array(dataset)
print("array")
print(dataset)

lineData = dataset[:, :10]
funcData = dataset[:, 10:-1]
lableData = dataset[:, -1]
print(lineData)
print(funcData)
print(lableData)
print("===================")

print(lineData.shape)

print("===================")

print(lineData.shape[0])
print(lineData.shape[1])
print(funcData.shape[0])
print(funcData.shape[1])
print("===================")

print(amount_of_feature)

lineData = np.reshape(lineData, (lineData.shape[0], lineData.shape[1], 1))
funcData = np.reshape(funcData, (funcData.shape[0], funcData.shape[1], 1))
print(lineData.shape)
print(funcData.shape)
print(lableData.shape)

model_Line = build_model_line([10, 1])
# print(model_Line.summary())
model_func = build_model_func([11, 1])
# print(model_func.summary())

print(model_Line.outputs.__class__)

model_concat = concatenate([model_Line.output, model_func.output])
print(model_concat.__class__)
print("class: !!! : !!!： ",lineData.__class__)
print("class: !!! : !!!： ",[lineData, funcData].__class__)

#
model_concat = Dense(128,activation="relu", kernel_initializer="uniform")(model_concat)
model_concat = Dropout(0.25)(model_concat)
model_concat = Dense(16,activation="relu", kernel_initializer="uniform")(model_concat)
model_concat = Dropout(0.25)(model_concat)
model_concat = Dense(1,activation="relu", kernel_initializer="uniform")(model_concat)
#
model_concat = Model(inputs = [model_Line.input, model_func.input], outputs = model_concat)

opt = keras.optimizers.SGD(lr=0.0001, decay=1e-6)
model_concat.compile(loss='mse', optimizer=opt, metrics=['accuracy'])
from contextlib import redirect_stdout
with open('model_summary.txt', 'w') as f:
    with redirect_stdout(f):
        model_concat.summary()
print(model_concat.summary())
#
# model_concat = Dense(1, activation="softmax")(model_concat)
#
# model = Model(inputs = [model_Line.input,model_func.input], outputs = model_concat)

# # ==================concat train=======================

from timeit import default_timer as timer
start = timer()
history_concat = model_concat.fit([lineData, funcData],
                    lableData,
                    batch_size=32,
                    epochs=300,
                    validation_split=0.2,
                    verbose=1)
end = timer()
print("concat训练时间： ", end - start)
