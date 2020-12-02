import requests


def get_klines(symbol, interval):
    if interval.endswith(("m", "h", "d", "w", "M")):
        return requests.get(f"https://api.binance.com/api/v3/klines?symbol={symbol.upper()}&interval={interval}").json()
    else:
        raise Exception("Kline interval must be m, h, d, w, or M")
