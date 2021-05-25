import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd

full_df = pd.read_pickle('app/data/sl_full_cleaned.pkl')

layout = html.Div([
    html.H2(
        id='local-header',
        children=f'Average number of new infections reported in Sri Lanka each day reaches new high: Now reporting more than '
                 f'{int(np.rint(full_df["new_cases"].tail(7).mean()))} daily.'
    ),
    html.Div([
        dcc.Dropdown(
            id='area-dropdown',
            options=[
                {'label': '2020', 'value': 2020},
                {'label': '2021', 'value': 2021},
                {'label': 'all-time', 'value': 'all-time'}
            ],
            value='all-time',
            style={'width': '76%', 'border-radius': '20px'}
        ),
        dcc.Dropdown(
            id='area-type-dropdown',
            options=[
                {'label': 'total cases', 'value': 'total_cases'},
                {'label': 'total deaths', 'value': 'total_deaths'},
                {'label': 'total tests', 'value': 'total_tests'},
            ],
            value='total_cases',
            style={'width': '76%', 'border-radius': '20px'}
        )
    ],
        style={'width': '30%', 'display': 'flex', 'justify-content': 'space-between'}),
    dcc.Graph(id='area-graph'),
])
