import plotly.graph_objs as go

total_asset = 100
unreal_pnl = 50
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
    width=300,
    height=200,
    # Set the size of the indicators
    # You can adjust the size attribute to control the size of the indicators
    # Larger values result in larger indicators
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

# Display the figure
summary_fig.show()
