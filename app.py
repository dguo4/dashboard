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

from data.load_transaction_data import return_transactions_data, rich_transactions_data
from data.load_position_data import return_positions_data, rich_positions_data
from data.load_market_data import return_market_data, return_market_history_data


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


# some useful info to included in dashboard
# total asset value + unrealized pnl
total_asset = riched_positions_df['Total Cost'].sum()
unreal_pnl = riched_positions_df['Unreal PnL'].sum()
summary_fig_layout = go.Layout(
    # Set the size of indicators
    # Adjust the size value to limit the size of indicators
    # Higher size values result in larger indicators
    # You can also use a list to specify different sizes for different indicators
    # For example: size=[20, 30, 15, 25]
    # This would set different sizes for each indicator respectively
    # Check the Plotly documentation for more customization options:
    # https://plotly.com/python/reference/indicator/
    template="plotly_white",
    width=1300,
    height=200,
    # Set the size of the indicators
    # You can adjust the size attribute to control the size of the indicators
    # Larger values result i
    # For example, size=100 would make the indicators much larger
    # You can set it to smaller values like size=20 to limit the size of the indicators
    # Experiment with different values to achieve the desired size
    margin=dict(l=0, r=0, t=20, b=5),
    paper_bgcolor='LightSteelBlue', # LightSteelBlue
    plot_bgcolor='rgba(0,0,0,0)',
    showlegend=False
)

summary_fig = go.Figure(layout=summary_fig_layout)
summary_fig.add_trace(go.Indicator(
    mode="number+delta",
    value=total_asset,
    title= {"text": "Account Overview"},
    number={'prefix': "$"},
    delta={'position': "bottom", 'reference': total_asset-unreal_pnl},
    domain={'x': [0, 0]}))
riched_pnl_dff = riched_pnl_df.copy(deep=True)
riched_pnl_dff['Unreal PnL'] = riched_pnl_dff.drop(columns=['date']).sum(axis=1)
summary_fig.add_trace(go.Scatter(y=riched_pnl_dff['Unreal PnL'], x=riched_pnl_dff['date']))

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

    dcc.Graph(figure=summary_fig),

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

    # # investment method pie graph
    # dcc.Graph(
    #     id='invest_method_pie_graph'
    # )

    # # unrealized pnl bar graph
    # dcc.Graph(
    #     id='pnl_trend_bar_graph'
    # ),

    html.Div([
        # mkt price correlation heat map
        dcc.Graph(
            id='mkt_price_corr_map',
            figure=px.imshow(mkt_price_corr_matrix,
                             labels=dict(x="Variables", y="Variables", color="Correlation"),
                             x=mkt_price_corr_matrix.columns,
                             y=mkt_price_corr_matrix.columns,
                             color_continuous_scale="YlOrRd").update_layout(title='Market Price Correlation')
        )
    ], style={'width': '48%', 'display': 'inline-block'}),

    html.Div([
        # pnl correlation heat map
        dcc.Graph(
            id='pnl_corr_map',
            figure=px.imshow(pnl_corr_matrix,
                             labels=dict(x="Ticker", y="Ticker", color="Correlation"),
                             x=pnl_corr_matrix.columns,
                             y=pnl_corr_matrix.columns,
                             color_continuous_scale="Greens").update_layout(title='Pnl Correlation')
        )
    ], style={'width': '48%', 'display': 'inline-block'}),



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
            range=[None, max_transaction_quantity*2],
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

# update unrealized pnl time series bar chart
# @app.callback(
#     [Output(component_id='pnl_trend_bar_graph', component_property='figure')],
#     [Input('summaryTable_id', 'active_cell')]
# )
# def update_pnl_trend_graph(active_cell):
#     riched_positions_dff = riched_positions_df.copy()
#     riched_pnl_dff = riched_pnl_df.copy()
#     mkt_price_dff = mkt_price_df.copy()
#
#     row = active_cell["row"]
#     ticker_var = riched_positions_dff.at[row, "Ticker"]
#
#     if ticker_var:
#         # Create figure with secondary y-axis
#         fig = make_subplots(specs=[[{"secondary_y": True}]])
#
#         fig.add_trace(
#             go.Scatter(x=account_pnl_df['date'].tolist(),
#                        y=account_pnl_df['pnl'],
#                        name='Market Price'), secondary_y=False)
#
#         fig.add_trace(
#             go.Bar(x=riched_pnl_dff['date'].tolist(),
#                    y=riched_pnl_dff[ticker_var],
#                    name='PnL'), secondary_y=True)
#
#         # Set x-axis title
#         fig.update_xaxes(title_text="Date")
#
#         fig.update_yaxes(
#             title_text="account pnl <b>(blue)</b>",
#             secondary_y=False
#         )
#         fig.update_yaxes(
#             title_text=ticker_var+" PnL <b>(orange)</b>",
#             secondary_y=True
#         )
#
#         # legend location
#         fig.update_layout(legend=dict(
#             yanchor="top",
#             y=0.99,
#             xanchor="left",
#             x=0.01
#         ))
#
#     return [fig]


if __name__ == '__main__':
    app.run(debug=True)
