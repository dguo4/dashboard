import plotly.graph_objects as go

def account_overview_trend_chart(riched_positions_df, riched_pnl_df):

    # some useful info to included in dashboard
    # total asset value + unrealized pnl
    total_asset = riched_positions_df['Total Cost'].sum()
    unreal_pnl = riched_positions_df['Unreal PnL'].sum()
    summary_fig_layout = go.Layout(
        template="plotly_white",
        width=1300,
        height=200,

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

    return summary_fig
