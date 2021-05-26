import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd

full_df = pd.read_pickle('app/data/sl_full_cleaned.pkl')

layout = html.Div([
    html.Div([
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
        dcc.Graph(id='area-graph')
    ]),
    html.Hr(className='section-divider',
            style={'padding': '0 0', 'margin': '32px 0'}),
    html.Div([
        html.P(
            f'There have been {int(full_df["total_cases"].max())} infections and {int(full_df["total_deaths"].max())} '
            f'coronavirus-related deaths reported in the country since the pandemic began.',
            style={'width': '64%', 'margin': '0 auto', 'color': '#fff'}),
        html.H3('Daily reported trends', style={'color': '#fff'}),
        html.Div([
            html.Label('New infections', style={'color': '#fff'}),
            dcc.Graph(id='new-case-dist'),
        ], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            html.Label('Deaths', style={'color': '#fff'}),
            dcc.Graph(id='new-death-dist'),
        ], style={'width': '50%', 'display': 'inline-block', 'float': 'right'}),
        html.Div([
            dcc.Slider(
                id='predict-for',
                min=0,
                max=28,
                value=0,
                marks={'0': 0, '7': 7, '14': 14, '21': 21, '28': 28},
                step=None
            )
        ], style={'width': '50%', 'margin': '0 auto'})
    ])
])
