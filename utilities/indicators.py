import pandas as pd


def rsi(dataframe, n=14):  # relative strength index
    delta = dataframe["Close"].astype(float).diff()
    delta_up, delta_down = delta.copy(), delta.copy()
    delta_up[delta_up < 0] = 0
    delta_down[delta_down > 0] = 0

    roll_up = delta_up.rolling(n).mean()
    roll_down = delta_down.rolling(n).mean().abs()

    return 100 - (100 / (1 + (roll_up / roll_down)))


def moving_avg(dataframe, n=14):
    if isinstance(dataframe, pd.DataFrame):  # Series vs DataFrame
        rolling_mean = dataframe["Close"].astype(float).rolling(n).mean()
    else:
        rolling_mean = dataframe.rolling(n).mean()  # different methods

    return rolling_mean
