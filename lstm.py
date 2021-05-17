import numpy
import tensorflow
from keras.models import Sequential
from keras.layers import LSTM, Dense
import random


def noisy(num):
    factor = (numpy.random.gamma(1, 2.0) * 5) / 10000
    pos_neg = random.randint(0, 1)  # decide to add or minus
    if pos_neg == 0:
        multiplier = 1 + factor
    else:
        multiplier = 1 - factor
    return num * multiplier


def lstm(data, n=3):
    # choose a number of time steps
    steps = 3

    # split into samples
    x, y = list(), list()
    for i in range(len(data)):
        # find the end of this pattern
        end_ix = i + steps
        # check if we are beyond these sequence
        if end_ix > len(data) - 1:
            break
        # gather input and output parts of the pattern
        seq_x, seq_y = data[i:end_ix], data[end_ix]
        x.append(seq_x)
        y.append(seq_y)
    x, y = numpy.array(x), numpy.array(y)

    # reshape from [samples, time_steps] into [samples, time_steps, features]
    n_features = 1
    x = x.reshape((x.shape[0], x.shape[1], n_features))

    # define model
    model = Sequential()
    model.add(LSTM(50, activation='relu', input_shape=(steps, n_features)))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')

    # fit model
    model.fit(x, y, epochs=200, verbose=0)

    inp = data[-3:]
    results = []
    for num in range(n):
        result_results = []
        for i in range(10):  # make an average of 10 results
            x_input = numpy.array(inp).reshape((1, steps, n_features))
            y_hat = model.predict(x_input, verbose=0)
            result_results.append(y_hat[0][0])
        avg_result = sum(result_results) / len(result_results)
        inp.append(avg_result)
        inp = inp[1:]
        results.append(noisy(avg_result))

    # clear session
    tensorflow.keras.backend.clear_session()
    return results
