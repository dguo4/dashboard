import json
import requests
import pandas as pd
import numpy as np

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



def return_positions_data():
    positions_response = requests.get(ALL_POSITIONS_URL)
    if positions_response.status_code == 200:
        df = pd.DataFrame(positions_response.json())
    else:
        print('AWS API failed with url: ' + ALL_POSITIONS_COLUMNS)

    positions_df = df.loc[:, ALL_POSITIONS_COLUMNS]
    positions_df['date'] = pd.to_datetime(positions_df['date'])
    positions_df['date'] = positions_df['date'].dt.date
    positions_df = positions_df.sort_values(by=['date'], ascending=False)

    return positions_df


def rich_positions_data(transactions_df, positions_df, market_df):
    transactions_df['cost'] = transactions_df['price']*transactions_df['quantity']
    transactions_std_df = transactions_df.loc[:, ['ticker', 'price']].groupby('ticker').agg(np.std, ddof=0).reset_index()
    transactions_std_df.rename(columns={'price': 'std'}, inplace=True)
    df = transactions_df.loc[:, ['ticker', 'assetType', 'quantity', 'cost']].groupby(['ticker', 'assetType']).agg(sum).reset_index()
    df['Avg Price'] = df['cost']/df['quantity']
    df = df.merge(market_df, on='ticker', how='left')
    df['Unreal PnL'] = df['quantity'] * df['latest_price'] - df['cost']
    df = df.merge(transactions_std_df, on='ticker', how='left')
    df['Std Price'] = df['std']/df['Avg Price']
    df.rename(columns=config['summary_table_columns_rename'], inplace=True)

    return df.loc[:, config['schema']['summary_columns']]
