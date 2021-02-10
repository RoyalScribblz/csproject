import requests
import pandas as pd

millis_time = {"m": 60000, "h": 3600000, "d": 86400000, "w": 604800000, "M": 2592000000}


def get_klines(symbol, interval_num, interval_letter, limit):
    interval = str(interval_num) + interval_letter
    if not interval.endswith(("m", "h", "d", "w", "M")):  # require interval format
        raise Exception("Kline interval must be m, h, d, w, or M")

    millis_interval = interval_num * millis_time[interval_letter]

    remainder = limit % 1000
    remainder = remainder if remainder != 0 else 1000  # make sure the request gets data

    responses = []

    response = requests.get("https://api.binance.com/api/v3/klines?symbol=" + symbol.upper() + "&interval="
                            + interval + "&limit=" + str(remainder)).json()
    responses.extend(response)
    limit -= remainder

    open_time = response[0][0]

    while limit > 0:
        open_time -= millis_interval * 1000

        response = requests.get("https://api.binance.com/api/v3/klines?symbol=" + symbol.upper() + "&interval="
                                + interval + "&limit=1000&startTime=" + str(open_time)).json()
        responses.extend(response)

        limit -= 1000

    df = pd.DataFrame(sorted(responses, key=lambda x: float(x[0])),
                      columns=["Open time", "Open", "High", "Low", "Close", "Volume",
                               "Close time", "Quote asset volume", "Number of trades",
                               "Taker buy base asset volume",
                               "Taker buy quote asset volume", "Ignore."])

    return df
