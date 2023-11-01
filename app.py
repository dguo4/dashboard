from dash import Dash, html, dcc, callback, Output, Input, dash_table
import json
import pandas as pd
import requests

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


# dashbaord
app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1(children='My investment details', style={'textAlign':'center'}),
    dash_table.DataTable(data=df.to_dict('records'), page_size=10)
])

if __name__ == '__main__':
    app.run(debug=True)