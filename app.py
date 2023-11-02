import datetime

from dash import Dash, html, dcc, callback, Output, Input, dash_table
import dash_bootstrap_components as dbc
import json
import pandas as pd
import requests
import pytz
from collections import OrderedDict

# load config data
config_file = open('./config/dashboard.json')
config = json.load(config_file)

BASE_URL = config['api']['base_url']
ALL_TRANSACTIONS_URL = BASE_URL + config['api']['all_transactions_url']
ALL_TRANSACTIONS_COLUMNS = config['transactions_columns']


# get data from AWS API
response = requests.get(ALL_TRANSACTIONS_URL)
if response.status_code == 200:
    df = pd.DataFrame(response.json())
else:
    print('AWS API failed with url: ' + ALL_TRANSACTIONS_URL)

df = df.loc[:, ALL_TRANSACTIONS_COLUMNS]
df = df.sort_values(by=['date'], ascending=False)

# get New York timezone
# Get the current time in UTC
utc_now = datetime.datetime.utcnow()

# Set the desired time zone (New York, Eastern Time Zone)
new_york_timezone = pytz.timezone('America/New_York')

# Convert the UTC time to New York time
new_york_time = utc_now.replace(tzinfo=pytz.utc).astimezone(new_york_timezone)


# dashbaord
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container([
    # title
    dcc.Markdown('# My Investment Details', style={'textAlign': 'center'}),

    # refresh time
    html.Header('Refreshed at ' + str(new_york_time.strftime('%Y-%m-%d %H:%M:%S')), style={'textAlign': 'right'}),

    # transaction table dropdown fitler
    dbc.Row([
        dbc.Col([
            account_drop := dcc.Dropdown([x for x in sorted(df['account'].unique())], placeholder='Account')
        ], width=3),
        dbc.Col([
            ticker_drop := dcc.Dropdown([x for x in sorted(df['ticker'].unique())], placeholder='Ticker')
        ], width=3),
    ]),

    html.Br(),

    # transactions table
    transaction_table := dash_table.DataTable(
        columns = [
            {'name': 'Date', 'id': 'date', 'type': 'text'},
            {'name': 'Account', 'id': 'account', 'type': 'text'},
            {'name': 'Ticker', 'id': 'ticker', 'type': 'text'},
            {'name': 'Price', 'id': 'price', 'type': 'numeric'},
            {'name': 'Quantity', 'id': 'quantity', 'type': 'numeric'}
        ],
        data = df.to_dict('records'),
        filter_action = 'native',
        page_size = 10,
        style_data={
            'width': '150px', 'minWidth': '150px', 'maxWidth': '150px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
        }
    ),

    # select row
    dbc.Label('Select # of rows: '),
    row_drop := dcc.Dropdown(value=5, clearable=False, style={'width': '35%'}, options = [5, 10, 15]),
])

@callback(
    Output(transaction_table, 'data'),
    Output(transaction_table, 'page_size'),
    Input(account_drop, 'value'),
    Input(ticker_drop, 'value'),
    Input(row_drop, 'value')
)
def update_dropdown_options(account_var, ticker_var, row_var):
    dff = df.copy()

    if account_var:
        dff = dff.loc[dff['account'] == account_var, :]
    if ticker_var:
        dff = dff.loc[dff['ticker'] == ticker_var, :]

    return dff.to_dict('records'), row_var


if __name__ == '__main__':
    app.run(debug=True)
