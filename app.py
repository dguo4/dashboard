import datetime as dt

from dash import Dash, html, dcc, callback, Output, Input, dash_table
import dash_bootstrap_components as dbc
import json
import pandas as pd
import requests
import pytz
import plotly
import plotly.express as px

from collections import OrderedDict

# load config data
config_file = open('./config/dashboard.json')
config = json.load(config_file)

BASE_URL = config['api']['base_url']
ALL_TRANSACTIONS_URL = BASE_URL + config['api']['all_transactions_url']
ALL_TRANSACTIONS_COLUMNS = config['schema']['transactions_columns']
ALL_POSITIONS_URL = BASE_URL + config['api']['all_positions_url']
ALL_POSITIONS_COLUMNS = config['schema']['positions_columns']


# get data from AWS API
transactions_response = requests.get(ALL_TRANSACTIONS_URL)
if transactions_response.status_code == 200:
    df = pd.DataFrame(transactions_response.json())
else:
    print('AWS API failed with url: ' + ALL_TRANSACTIONS_URL)

transactions_df = df.loc[:, ALL_TRANSACTIONS_COLUMNS]
transactions_df['date'] = pd.to_datetime(transactions_df['date'])
transactions_df = transactions_df.sort_values(by=['date'], ascending=False)

positions_response = requests.get(ALL_POSITIONS_URL)
if positions_response.status_code == 200:
    df = pd.DataFrame(positions_response.json())
else:
    print('AWS API failed with url: ' + ALL_POSITIONS_COLUMNS)

positions_df = df.loc[:, ALL_POSITIONS_COLUMNS]
positions_df['date'] = pd.to_datetime(positions_df['date'])
positions_df = positions_df.sort_values(by=['date'], ascending=False)

# get New York timezone
# Get the current time in UTC
utc_now = dt.datetime.utcnow()

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

    # transaction table dropdown filter
    dbc.Row([
        dbc.Col([
            ticker_drop := dcc.Dropdown(value='VOO',
                                        options=[x for x in sorted(positions_df['ticker'].unique())],
                                        placeholder='Ticker')], width=3),
    ]),

    html.Br(),

    # positions table
    positions_table := dash_table.DataTable(
        columns=config['dash_table']['positions_dash_table_columns'],
        data=positions_df.to_dict('records'),
        filter_action='native',
        page_size=10,
        style_data={
            'width': '150px', 'minWidth': '150px', 'maxWidth': '150px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
        }
    ),

    # select row
    dbc.Label('Select # of rows: '),
    row_drop := dcc.Dropdown(value=5, clearable=False, style={'width': '35%'}, options = [5, 10, 15]),

    # transaction time series graph
    html.Div([
        dcc.Graph(id='transaction_price_time_series_graph',
                  className='six columns',
                  config={
                      'staticPlot': True,
                      'scrollZoom': False,
                      'showTips': True,
                      'displayModeBar': False
                  }),
        dcc.Graph(id='transaction_quantity_time_series_graph',
                  className='six columns',
                  config={
                      'staticPlot': True,
                      'scrollZoom': False,
                      'showTips': False,
                      'displayModeBar': False
                  })
    ])
])

# ----------------------------------------------------------------------------------------------------------------------
# update position table
@app.callback(
    Output(positions_table, 'data'),
    Output(positions_table, 'page_size'),
    Input(ticker_drop, 'value'),
    Input(row_drop, 'value')
)
def update_positions_table(ticker_var, row_var):
    positions_dff = positions_df.copy()
    if ticker_var:
        positions_dff = positions_dff.loc[positions_dff['ticker'] == ticker_var, :]

    return positions_dff.to_dict('records'), row_var

# update transaction price time series table
@app.callback(
    Output(component_id='transaction_price_time_series_graph', component_property='figure'),
    Input(ticker_drop, 'value')
)
def update_transactions_price_graph(ticker_var):
    transactions_dff = transactions_df.copy()
    if ticker_var:
        transactions_dff = transactions_df.loc[transactions_dff['ticker'] == ticker_var, :]
        ticker_market_price = 400.21
        # create the chart
        fig = px.line(x=transactions_dff['date'].unique().tolist(),
                      y=transactions_dff['price'],
                      labels=dict(x='Date', y='Purchase price'),
                      title=ticker_var+' Purchase Price Trend',
                      markers=True)
        fig.add_hline(y=ticker_market_price)

    return fig

# update transaction quantity time series table
@app.callback(
    Output(component_id='transaction_quantity_time_series_graph', component_property='figure'),
    Input(ticker_drop, 'value')
)
def update_transactions_quantity_graph(ticker_var):
    transactions_dff = transactions_df.copy()
    positions_dff = positions_df.copy()
    if ticker_var:
        transactions_dff = transactions_df.loc[transactions_dff['ticker'] == ticker_var, :]
        # create the chart
        fig = px.line(x=positions_dff['date'].tolist(),
                      y=positions_dff['quantity'],
                      labels=dict(x='Date', y='Total Quantity'),
                      title=ticker_var+' Quantity Trend',
                      markers=True)

        fig.add_bar(x=transactions_dff['date'].tolist(),
                    y=transactions_dff['quantity'],
                    name='Transactions')

    return fig


if __name__ == '__main__':
    app.run(debug=True)
