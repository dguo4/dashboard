import plotly.express as px

def pnl_corr_matrix_chart(pnl_corr_matrix):
    return px.imshow(pnl_corr_matrix,
                             labels=dict(x="Ticker", y="Ticker", color="Correlation"),
                             x=pnl_corr_matrix.columns,
                             y=pnl_corr_matrix.columns,
                             color_continuous_scale="Greens").update_layout(title='Pnl Correlation')
