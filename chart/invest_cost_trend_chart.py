import plotly.graph_objects as go


def invest_cost_trend_chart(cost_trend_df):
    fig = go.Figure()

    tickers = cost_trend_df['ticker'].unique()

    for ticker in tickers:
        ticker_df = cost_trend_df[cost_trend_df['ticker'] == ticker]
        fig.add_trace(go.Bar(x=ticker_df['date'], y=ticker_df['cost'], name=ticker))

    fig.update_layout(barmode='stack', title='Invest Cost Trend by Ticker', xaxis_title='Date', yaxis_title='Cost')

    return fig
