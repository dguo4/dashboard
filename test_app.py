import plotly.graph_objs as go

# Sample data
categories = ['Category A', 'Category B', 'Category C']
values1 = [20, 30, 40]  # Values for stack 1
values2 = [15, 25, 35]  # Values for stack 2

# Create traces for each stack
trace1 = go.Bar(
    x=categories,
    y=values1,
    name='Stack 1'
)

trace2 = go.Bar(
    x=categories,
    y=values2,
    name='Stack 2'
)

# Define layout
layout = go.Layout(
    title='Stacked Bar Chart',
    barmode='stack'  # Ensure bars are stacked on top of each other
)

# Create figure
fig = go.Figure(data=[trace1, trace2], layout=layout)

# Display the plot
fig.show()
