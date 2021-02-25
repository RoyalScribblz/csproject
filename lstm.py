from numpy import array
import tensorflow
from keras.models import Sequential
from keras.layers import LSTM, Dense

# define input sequence
raw_seq = [10, 20, 30, 40, 50, 60, 70, 80, 90]

# choose a number of time steps
steps = 3

# split into samples
x, y = list(), list()
for i in range(len(raw_seq)):
    # find the end of this pattern
    end_ix = i + steps
    # check if we are beyond the sequence
    if end_ix > len(raw_seq) - 1:
        break
    # gather input and output parts of the pattern
    seq_x, seq_y = raw_seq[i:end_ix], raw_seq[end_ix]
    x.append(seq_x)
    y.append(seq_y)
x, y = array(x), array(y)

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

# demonstrate prediction
x_input = array([90, 100, 110])
x_input = x_input.reshape((1, steps, n_features))
y_hat = model.predict(x_input, verbose=0)
print(y_hat)

# clear session
tensorflow.keras.backend.clear_session()
