import datetime as dt
from datetime import timedelta

from dash import Dash, html, dcc, callback, Output, Input, dash_table, no_update
import dash_bootstrap_components as dbc
from dash.dash_table import FormatTemplate
import json
import pytz
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# data
from data.load_transaction_data import return_transactions_data, rich_transactions_data, return_cost_data
from data.load_position_data import return_positions_data, rich_positions_data
from data.load_market_data import return_market_data, return_market_history_data

# chart
from chart.account_overview_trend_chart import account_overview_trend_chart
from chart.mkt_price_corr_matrix_chart import mkt_price_corr_matrix_chart
from chart.pnl_corr_matrix_chart import pnl_corr_matrix_chart
from chart.invest_cost_trend_chart import invest_cost_trend_chart


# load config data
config_file = open('./config/dashboard.json')
config = json.load(config_file)

# format
money = FormatTemplate.money(2)
percentage = FormatTemplate.percentage(2)
#quantity = FormatTemplate.quantity(5)

# get New York timezone
# Get the current time in UTC
utc_now = dt.datetime.utcnow()

# Set the desired time zone (New York, Eastern Time Zone)
new_york_timezone = pytz.timezone('America/New_York')

# Convert the UTC time to New York time
new_york_time = utc_now.replace(tzinfo=pytz.utc).astimezone(new_york_timezone)

# transactions data
transactions_df = return_transactions_data()
cost_trend_df = return_cost_data(transactions_df, look_back=360)

# positions data
positions_df = return_positions_data()

# market data
ticker_list = positions_df['ticker'].unique().tolist()
marketData_df = return_market_data(ticker_list)
marketHistoryDate_df = return_market_history_data(ticker_list,
                                                  (new_york_time - timedelta(days=365)).strftime('%Y-%m-%d'),
                                                  new_york_time.strftime('%Y-%m-%d'))

riched_positions_df = rich_positions_data(transactions_df, marketData_df)
riched_pnl_df, mkt_price_df = rich_transactions_data(positions_df, marketHistoryDate_df)
account_pnl_df = riched_pnl_df.copy(deep=True)
numeric_columns = account_pnl_df.drop('date', axis=1)
numeric_columns['pnl'] = numeric_columns.sum(axis=1)
pnl_corr_matrix = numeric_columns.loc[:, ticker_list+['pnl']].corr()
account_pnl_df.drop(ticker_list, axis=1, inplace=True)

# calculate mkt price correlation
mkt_price_corr_matrix = mkt_price_df.loc[:, ticker_list].corr()

account_overview_trend_chart = account_overview_trend_chart(riched_positions_df, riched_pnl_df)

# pie chart to show invest method
invest_method = []
invest_shares = []
invest_method_fig = px.pie(names=invest_method, values=invest_shares, title='Investment Method Breakdown')

# dashbaord
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
initial_active_cell = {"row": 0, "column": 0, "column_id": "Ticker", "row_id": 0}

app.layout = dbc.Container([
    # title
    dcc.Markdown('# My Investment Details', style={'textAlign': 'center'}),

    # refresh time
    html.Header('Refreshed at ' + str(new_york_time.strftime('%Y-%m-%d %H:%M:%S')), style={'textAlign': 'right'}),

    html.Br(),

    dcc.Graph(figure=account_overview_trend_chart),

    html.Br(),

    # positions table
    summary_table := dash_table.DataTable(
        id='summaryTable_id',
        columns=[
          {"name": "Ticker", "id": "Ticker", "type": "text"},
          {"name": "Asset Type", "id": "Asset Type", "type": "text"},
          {"name": "Total Share", "id": "Total Share", "type": "numeric"},
          {"name": "Total Cost", "id": "Total Cost", "type": "numeric", "format": money},
          {"name": "Avg. Price", "id": "Avg Price", "type": "numeric", "format": money},
          {"name": "Std. Price", "id": "Std Price", "type": "numeric", "format": percentage},
          {"name": "Unreal. PnL", "id": "Unreal PnL", "type": "numeric", "format": money}
        ],
        data=riched_positions_df.to_dict('records'),
        active_cell=initial_active_cell,
        editable=False,
        page_size=10,
        style_data={
            'width': '150px', 'minWidth': '150px', 'maxWidth': '150px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
        }
    ),

    # transaction time series graph
    html.Div([
        dcc.Graph(id='transaction_price_time_series_graph',
                  className='six columns',
                  config={
                      'staticPlot': False,
                      'scrollZoom': False,
                      'showTips': True,
                      'displayModeBar': False
                  }),
        dcc.Graph(id='transaction_quantity_time_series_graph',
                  className='six columns',
                  config={
                      'staticPlot': False,
                      'scrollZoom': False,
                      'showTips': False,
                      'displayModeBar': False
                  })
    ]),

    # mkt price correlation heat map
    html.Div([
        dcc.Graph(
            id='mkt_price_corr_map',
            figure=mkt_price_corr_matrix_chart(mkt_price_corr_matrix)
        )
    ], style={'width': '48%', 'display': 'inline-block'}),

    # pnl correlation heat map
    html.Div([
        dcc.Graph(
            id='pnl_corr_map',
            figure=pnl_corr_matrix_chart(pnl_corr_matrix)
        )
    ], style={'width': '48%', 'display': 'inline-block'}),

    html.Div([
        dcc.Graph(
            id='invest_cost_trend',
            figure=invest_cost_trend_chart(cost_trend_df))

    ], style={'width': '100%', 'display': 'inline-block'})

])

# ----------------------------------------------------------------------------------------------------------------------

# update transaction price time series table
@app.callback(
    [Output(component_id='transaction_price_time_series_graph', component_property='figure')],
    [Input('summaryTable_id', 'active_cell')]
)
def update_transactions_price_graph(active_cell):
    # print(active_cell)
    if active_cell is None:
        return no_update

    transactions_dff = transactions_df.copy()
    riched_positions_dff = riched_positions_df.copy()

    row = active_cell["row"]
    ticker_var = riched_positions_dff.at[row, "Ticker"]

    if ticker_var:
        transactions_dff = transactions_dff.loc[transactions_dff['ticker'] == ticker_var, :]
        ticker_market_price = marketData_df.loc[marketData_df['ticker'] == ticker_var, 'latest_price'].values[0]
        # create the chart
        fig = px.line(x=transactions_dff['date'].unique().tolist(),
                      y=transactions_dff['price'].tolist(),
                      labels=dict(x='Date', y='Purchase price'),
                      title=ticker_var+' Purchase Price Trend',
                      markers=True)
        fig.add_hline(y=ticker_market_price,
                      line_dash='dash',
                      line_color='green',
                      annotation_text='latest mkt. price = '+str(ticker_market_price),
                      annotation_position='bottom right')

    return [fig]

# update transaction quantity time series table
@app.callback(
    [Output(component_id='transaction_quantity_time_series_graph', component_property='figure')],
    [Input('summaryTable_id', 'active_cell')]
)
def update_transactions_quantity_graph(active_cell):
    riched_positions_dff = riched_positions_df.copy()
    transactions_dff = transactions_df.copy()
    positions_dff = positions_df.copy()

    row = active_cell["row"]
    ticker_var = riched_positions_dff.at[row, "Ticker"]

    if ticker_var:
        transactions_dff = transactions_dff.loc[transactions_dff['ticker'] == ticker_var, :]
        positions_dff = positions_dff.loc[positions_dff['ticker'] == ticker_var, :]
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Scatter(x=positions_dff['date'].tolist(),
                       y=positions_dff['quantity'],
                       name='Total quantity'), secondary_y=False)

        fig.add_trace(
            go.Bar(x=transactions_dff['date'].tolist(),
                   y=transactions_dff['quantity'],
                   name='Transaction quantity'), secondary_y=True)

        # Set x-axis title
        fig.update_xaxes(title_text="Date")

        # Set y-axes titles
        max_transaction_quantity = max(transactions_dff['quantity'])
        fig.update_yaxes(
            title_text="total quantity <b> (blue) </b>",
            range=[max_transaction_quantity*0.8, None],
            secondary_y=False
        )
        fig.update_yaxes(
            title_text="transaction quantity <b> (orange) </b>",
            range=[None, max_transaction_quantity*1.2],
            secondary_y=True
        )

        # legend location
        fig.update_layout(legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ))

    return [fig]


if __name__ == '__main__':
    app.run(debug=True)
