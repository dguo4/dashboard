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


def return_cost_data(transactions_df, look_back=360):
    transactions_dff = transactions_df.copy(deep=True)
    transactions_dff['cost'] = transactions_dff['price']*transactions_dff['quantity']
    transactions_dff['date'] = pd.to_datetime(transactions_dff['date'])
    transactions_dff['date'] = transactions_dff['date'].dt.strftime('%Y-%m')

    pivot_dff = pd.pivot_table(transactions_dff.loc[:, ['date', 'ticker', 'cost']], values='cost', index=['date', 'ticker'], aggfunc='sum').reset_index()

    return pivot_dff


def rich_transactions_data(positions_df, marketHistoryDate_df):
    min_date = min(marketHistoryDate_df['date'])
    positions_df['date'] = pd.to_datetime(positions_df['date'])
    positions_df = positions_df.loc[positions_df['date'] >= min_date]
    riched_historical_positions_df = positions_df.merge(marketHistoryDate_df, on=['date', 'ticker'], how='right')

    riched_historical_positions_df.sort_values(by=['ticker', 'date'], inplace=True)

    riched_historical_positions_df_list = []
    for one_ticker in riched_historical_positions_df['ticker'].unique().tolist():
        single_ticker_riched_historical_positions_df = riched_historical_positions_df.loc[riched_historical_positions_df['ticker'] == one_ticker]
        # fill n/a with previous data
        single_ticker_riched_historical_positions_df['quantity'].fillna(method='ffill', inplace=True)
        single_ticker_riched_historical_positions_df['price'].fillna(method='ffill', inplace=True)
        riched_historical_positions_df_list.append(single_ticker_riched_historical_positions_df)

    enhanced_riched_historical_positions_df = pd.concat(riched_historical_positions_df_list)

    enhanced_riched_historical_positions_df = enhanced_riched_historical_positions_df.loc[~enhanced_riched_historical_positions_df['close'].isnull()]
    enhanced_riched_historical_positions_df = enhanced_riched_historical_positions_df.loc[~enhanced_riched_historical_positions_df['price'].isnull()]
    enhanced_riched_historical_positions_df = enhanced_riched_historical_positions_df.loc[enhanced_riched_historical_positions_df['date'] != min_date]

    enhanced_riched_historical_positions_df['pnl'] = (enhanced_riched_historical_positions_df['close'] - enhanced_riched_historical_positions_df['price'])*enhanced_riched_historical_positions_df['quantity']
    enhanced_riched_historical_positions_df = enhanced_riched_historical_positions_df.pivot_table(values='pnl', index='date', columns='ticker', aggfunc='sum', fill_value=0)
    # VOO has the longest investment history.
    for one_ticker in ['VOO']:
        enhanced_riched_historical_positions_df = enhanced_riched_historical_positions_df.loc[enhanced_riched_historical_positions_df[one_ticker] != 0.0]
    enhanced_riched_historical_positions_df.reset_index(inplace=True)

    selected_marketHistoryDate_df = marketHistoryDate_df[marketHistoryDate_df['date'].isin(enhanced_riched_historical_positions_df['date'])]
    selected_marketHistoryDate_df = selected_marketHistoryDate_df.pivot_table(values='close', index='date', columns='ticker', fill_value=0)
    selected_marketHistoryDate_df.reset_index(inplace=True)

    return enhanced_riched_historical_positions_df, selected_marketHistoryDate_df
