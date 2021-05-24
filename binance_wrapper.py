import requests
import pandas as pd

millis_time = {"m": 60000, "h": 3600000, "d": 86400000, "w": 604800000, "M": 2592000000}  # symbols for time intervals


def is_code(response):  # error catching to prevent overloading the API
    if type(response) is dict:
        print("[Binance] Error " + str(response["code"]) + ", " + response["msg"])  # output the error
        return True
    return False


def get_klines(symbol, interval_num, interval_letter, limit):
    interval = str(interval_num) + interval_letter
    if not interval.endswith(("m", "h", "d", "w", "M")):  # require interval format
        raise Exception("Kline interval must be m, h, d, w, or M")

    millis_interval = interval_num * millis_time[interval_letter]  # convert to correct time format

    remainder = limit % 1000 if limit % 1000 != 0 else 1000  # make sure the request gets data

    responses = []

    response = requests.get("https://api.binance.com/api/v3/klines?symbol=" + symbol.upper() + "&interval="
                            + interval + "&limit=" + str(remainder)).json()  # send a web request

    if is_code(response):
        return None  # exit function if there is an error code

    responses.extend(response)
    limit -= remainder

    open_time = response[0][0]

    while limit > 0:  # loop until limit has been met, intervals of 1000 because of max limit
        open_time -= millis_interval * 1000

        response = requests.get("https://api.binance.com/api/v3/klines?symbol=" + symbol.upper() + "&interval="
                                + interval + "&limit=1000&startTime=" + str(open_time)).json()  # make the next request

        if is_code(response):
            break  # don't continue if there is an error code

        responses.extend(response)

        limit -= 1000

    # create a dataframe with all responses
    df = pd.DataFrame(sorted(responses, key=lambda x: float(x[0])),
                      columns=["Open time", "Open", "High", "Low", "Close", "Volume",
                               "Close time", "Quote asset volume", "Number of trades",
                               "Taker buy base asset volume",
                               "Taker buy quote asset volume", "Ignore."])

    return df
