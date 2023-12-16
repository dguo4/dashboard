import json
import requests
import pandas as pd


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


def return_transactions_data():
    # transactions data
    transactions_response = requests.get(ALL_TRANSACTIONS_URL)
    if transactions_response.status_code == 200:
        df = pd.DataFrame(transactions_response.json())
    else:
        print('AWS API failed with url: ' + ALL_TRANSACTIONS_URL)

    transactions_df = df.loc[:, ALL_TRANSACTIONS_COLUMNS]
    transactions_df['date'] = pd.to_datetime(transactions_df['date'])
    transactions_df = transactions_df.sort_values(by=['date'], ascending=False)
    return transactions_df
