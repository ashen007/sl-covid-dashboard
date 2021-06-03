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
fill_color = ['rgba(254, 252, 205,1)',
              'rgba(239, 225, 156,1)',
              'rgba(221, 201, 106,1)',
              'rgba(194, 182, 59,1)',
              'rgba(157, 167, 21,1)',
              'rgba(116, 153, 5,1)',
              'rgba(75, 138, 20,1)',
              'rgba(35, 121, 36,1)',
              'rgba(11, 100, 44,1)',
              'rgba(18, 78, 43,1)',
              'rgba(25, 56, 34,1)',
              'rgba(23, 35, 18,1)']

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

#################################### top contries ####################
top_contries_cases = go.Figure()
top_contries_deaths = go.Figure()
topCountry = world_data[world_data['date'] >= last_date - datetime.timedelta(days=14)][
    ['location', 'new_cases', 'new_deaths']].groupby(by='location').max().reset_index()
situation_updater = dict(xaxis=dict(title='',
                                    showgrid=False,
                                    showline=False,
                                    color='white',
                                    zeroline=False),
                         yaxis=dict(title='Count',
                                    gridcolor='#404040',
                                    gridwidth=1,
                                    showline=False,
                                    zeroline=False,
                                    color='white'),
                         legend=dict(orientation='h',
                                     font=dict(color='#fff')),
                         paper_bgcolor='#262625',
                         plot_bgcolor='#262625',
                         height=500,
                         transition_duration=500)

top_cases = topCountry[['location', 'new_cases']].sort_values(by='new_cases').tail(8)
top_deaths = topCountry[['location', 'new_deaths']].sort_values(by='new_deaths').tail(8)
i = 0

for loc in top_cases['location']:
    temp = world_data[world_data['location'] == loc][['date', 'new_cases']].set_index('date').ewm(alpha=0.4).mean()
    temp = temp.ewm(span=7).mean()
    top_contries_cases.add_trace(
        go.Scatter(x=temp.index, y=temp['new_cases'],
                   name=loc,
                   mode='lines',
                   line=dict(color='#262625',
                             width=0.5),
                   stackgroup='one',
                   fillcolor=fill_color[i]
                   ))
    i += 1

i = 0
for loc in top_deaths['location']:
    temp = world_data[world_data['location'] == loc][['date', 'new_deaths']].set_index('date').ewm(alpha=0.4).mean()
    temp = temp.ewm(span=7).mean()
    top_contries_deaths.add_trace(
        go.Scatter(x=temp.index, y=temp['new_deaths'],
                   name=loc,
                   mode='lines',
                   line=dict(color='#262625',
                             width=0.5),
                   stackgroup='one',
                   fillcolor=fill_color[i]
                   ))
    i += 1

top_contries_cases.update_layout(situation_updater)
top_contries_deaths.update_layout(situation_updater)

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
    ]),
    html.Section([
        html.Div([
            html.Div([
                dcc.Graph(id='country-situation-cases',
                          figure=top_contries_cases)
            ], style={'width': '48%',
                      'display': 'inline-block'}),
            html.Div([
                dcc.Graph(id='country-situation-deaths',
                          figure=top_contries_deaths)
            ], style={'width': '48%',
                      'display': 'inline-block',
                      'float': 'right'})])
    ])
])
