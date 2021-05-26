import dash_core_components as dcc
import dash_html_components as html

layout = html.Div([
    html.H1('Stock Tickers'),
    dcc.Dropdown(
        id='area-dropdown',
        options=[
            {'label': '2020', 'value': 2020},
            {'label': '2021', 'value': 2021},
            {'label': 'overall', 'value': 'AAPL'}
        ],
        value='overall'
    ),
    dcc.Graph(id='area-graph')
], style={'width': '500'})
