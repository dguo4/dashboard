import plotly.express as px

def mkt_price_corr_matrix_chart(mkt_price_corr_matrix):
    return px.imshow(mkt_price_corr_matrix,
                             labels=dict(x="Variables", y="Variables", color="Correlation"),
                             x=mkt_price_corr_matrix.columns,
                             y=mkt_price_corr_matrix.columns,
                             color_continuous_scale="YlOrRd").update_layout(title='Market Price Correlation')
