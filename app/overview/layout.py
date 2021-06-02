import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import datetime

data = pd.read_csv('app/data/owid-covid-data.csv')
world_data = data.fillna(value=0)
drop_index = []

for loc in world_data['location']:
    if loc in ['Asia', 'Africa', 'Europe', 'European Union', 'North America', 'South America', 'World']:
        drop_index.append(True)
    else:
        drop_index.append(False)

world_data.drop(world_data.index[drop_index], inplace=True)
world_data['date'] = pd.to_datetime(world_data['date'])
colors = px.colors.sequential.speed

################################# world last 7 days ####################
worldLast7Days = go.Figure()
last_date = np.max(world_data['date'])
week_ago = world_data[world_data['date'] >= last_date - datetime.timedelta(days=7)]
week_ago = week_ago[['location', 'new_cases']].groupby(by='location').sum()
week_ago.reset_index(inplace=True)
worldLast7Days.add_trace(go.Choropleth(locations=week_ago['location'],
                                       z=np.log(week_ago['new_cases']),
                                       locationmode='country names',
                                       text=week_ago['location'],
                                       colorscale=px.colors.sequential.speed))

worldLast7Days.update_geos(projection=dict(type='equirectangular',
                                           ),
                           lataxis=dict(range=[66.57, -10.046630]),
                           oceancolor='#262625',
                           showocean=True,
                           showlakes=False,
                           showcountries=True,
                           bgcolor='#262625',
                           showframe=False
                           )

worldLast7Days.update_traces(showscale=False)

worldLast7Days.update_layout(xaxis=dict(showgrid=False,
                                        showline=False,
                                        color='white',
                                        zeroline=False),
                             yaxis=dict(showgrid=False,
                                        showline=False,
                                        color='white'),
                             showlegend=False,
                             paper_bgcolor='#262625',
                             plot_bgcolor='#262625',
                             height=800,
                             dragmode=False,
                             transition_duration=500,
                             margin=dict(t=0, b=0, l=0, r=0)
                             )

#################################### layout #############################
layout = html.Div([
    html.Section([
        html.Div([
            dcc.Graph(id='world-last7days',
                      figure=worldLast7Days,
                      config={
                          'displayModeBar': False
                      },
                      style={
                          'width': '100%'
                      }
                      )
        ])
    ]),
    html.Section([
        html.Div([
            dcc.Dropdown(
                id='situation-dropdown',
                options=[
                    {'label': 'cases', 'value': 1},
                    {'label': 'death', 'value': 2},
                    {'label': 'vaccination', 'value': 3}
                ],
                value=1,
                style={'width': '40%',
                       'border-radius': '20px'}
            )
        ]),
        html.Div([
            html.Div([
                dcc.Graph(id='global-situation-new')
            ], style={'width': '48%',
                      'display': 'inline-block'}),
            html.Div([
                dcc.Graph(id='global-situation-total')
            ], style={'width': '48%',
                      'display': 'inline-block',
                      'float': 'right'})])
    ])
])
