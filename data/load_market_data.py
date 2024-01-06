import json
import requests
import pandas as pd
import time
import ccxt
import yfinance as yf
from datetime import timedelta


# load config data
config_file = open('./config/dashboard.json')
config = json.load(config_file)


BASE_URL = config['api']['base_url']
EQUITY_PRICE_URL = config['equity_price_url']
CRYPTO_PRICE_URL = config['crypto_price_url']
CRYPTO_HISTORICAL_PRICE_URL = config['crypto_history_price_url']
ALL_TRANSACTIONS_URL = BASE_URL + config['api']['all_transactions_url']
ALL_TRANSACTIONS_COLUMNS = config['schema']['transactions_columns']
ALL_POSITIONS_URL = BASE_URL + config['api']['all_positions_url']
ALL_POSITIONS_COLUMNS = config['schema']['positions_columns']

def return_market_data(ticker_list):
    market_data_list = []
    for one_ticker in ticker_list:
        if one_ticker == 'BTC':
            price_url = CRYPTO_PRICE_URL.format(ticker=one_ticker)
            market_price_response = requests.get(price_url)
            ticker_market_price = market_price_response.json()['results'][0]['c']
        else:
            ticker_market_price = yf.Ticker(one_ticker).history_metadata['regularMarketPrice']

        market_data_list.append({'ticker': one_ticker, 'latest_price': ticker_market_price})
    # test cases
    # market_data_list = [{'ticker': 'BTC', 'latest_price': 43722.52}, {'ticker': 'QQQ', 'latest_price': 392.17}, {'ticker': 'VOO', 'latest_price': 422.92}, {'ticker': 'BND', 'latest_price': 71.82}, {'ticker': 'XLF', 'latest_price': 36.13}, {'ticker': 'SCHD', 'latest_price': 72.52}]
    marketData_df = pd.DataFrame(market_data_list)

    return marketData_df


def return_market_history_data(ticker_list, start_date, end_date):
    market_history_data = []
    for one_ticker in ticker_list:
        if one_ticker == 'BTC':
            history_price_url = CRYPTO_HISTORICAL_PRICE_URL.format(ticker=one_ticker, start_date=start_date, end_date=end_date)
            market_price_response = requests.get(history_price_url)
            ticker_market_price = pd.DataFrame(market_price_response.json()['results'])
            ticker_market_price = ticker_market_price.loc[:, ['c']]
            ticker_market_price.rename(columns={'c': 'close'}, inplace=True)
            date_series = pd.date_range(pd.to_datetime(start_date), pd.to_datetime((pd.to_datetime(end_date)).strftime('%Y-%m-%d')))
            ticker_market_price['date'] = date_series[:len(ticker_market_price)]
            ticker_market_price['ticker'] = one_ticker
        else:
            ticker_market_price = yf.download(one_ticker, start=start_date, end=end_date)
            ticker_market_price.reset_index(inplace=True)
            ticker_market_price = ticker_market_price.loc[:, ['Date', 'Adj Close']]
            ticker_market_price.rename(columns={'Adj Close': 'close', 'Date': 'date'}, inplace=True)
            # ticker_market_price['date'] = ticker_market_price['date'].dt.strftime('%Y-%m-%d')
            ticker_market_price['ticker'] = one_ticker
        market_history_data.append(ticker_market_price)

    return pd.concat(market_history_data)

