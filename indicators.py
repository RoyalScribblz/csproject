import pandas as pd


def rsi(dataframe, n=14):
    delta = dataframe["Close"].astype(float).diff()
    delta_up, delta_down = delta.copy(), delta.copy()
    delta_up[delta_up < 0] = 0
    delta_down[delta_down > 0] = 0

    roll_up = delta_up.rolling(n).mean()
    roll_down = delta_down.rolling(n).mean().abs()

    return 100 - (100 / 1 + roll_up / roll_down)
