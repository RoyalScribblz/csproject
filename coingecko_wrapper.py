import requests


def get_cg(cg_id):  # make a web request for the coingecko.com data
    response = requests.get("https://api.coingecko.com/api/v3/coins/"
                            + cg_id
                            + "?localization=false"
                            + "&tickers=false"
                            + "&market_data=true"
                            + "&community_data=false"
                            + "&developer_data=false"
                            + "&sparkline=false").json()

    return response
