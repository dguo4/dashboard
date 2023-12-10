import json
import requests
import pandas as pd
import time


# load config data
config_file = open('./config/dashboard.json')
config = json.load(config_file)


BASE_URL = config['api']['base_url']
EQUITY_PRICE_URL = config['equity_price_url']
CRYPTO_PRICE_URL = config['crypto_price_url']
ALL_TRANSACTIONS_URL = BASE_URL + config['api']['all_transactions_url']
ALL_TRANSACTIONS_COLUMNS = config['schema']['transactions_columns']
ALL_POSITIONS_URL = BASE_URL + config['api']['all_positions_url']
ALL_POSITIONS_COLUMNS = config['schema']['positions_columns']

def return_market_data(ticker_list):
    market_data_list = []
    for one_ticker in ticker_list:
        if one_ticker == 'BTC':
            price_url = CRYPTO_PRICE_URL.format(ticker=one_ticker)
        else:
            price_url = EQUITY_PRICE_URL.format(ticker=one_ticker)
        market_price_response = requests.get(price_url)
        time.sleep(2)
        ticker_market_price = market_price_response.json()['results'][0]['c']
        market_data_list.append({'ticker': one_ticker, 'latest_price': ticker_market_price})
    # test cases
    # market_data_list = [{'ticker': 'BTC', 'latest_price': 43722.52}, {'ticker': 'QQQ', 'latest_price': 392.17}, {'ticker': 'VOO', 'latest_price': 422.92}, {'ticker': 'BND', 'latest_price': 71.82}, {'ticker': 'XLF', 'latest_price': 36.13}, {'ticker': 'SCHD', 'latest_price': 72.52}]
    marketData_df = pd.DataFrame(market_data_list)

    return marketData_df
