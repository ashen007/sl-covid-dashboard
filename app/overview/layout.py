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

#################################### peak map ###########################
peak_map = go.Figure()
bubble_color = ['crimson', 'orange', 'lightgrey']

peaks = world_data[['location', 'new_cases']].groupby('location').max().reset_index()
weekly_rate = world_data[world_data['date'] >= last_date - datetime.timedelta(days=13)][
    ['date', 'location', 'new_cases']].set_index('date')
weekly_rate = weekly_rate.groupby(by='location').resample('7D').mean().reset_index()
current_week = weekly_rate.groupby(by='location')[['date']].max().reset_index()

weekly_rate = pd.merge(current_week, weekly_rate, how='left', on=['location', 'date'])
weekly_rate = pd.merge(weekly_rate, peaks, how='left', on=['location'])
weekly_rate.rename(columns={'new_cases_x': 'new_cases', 'new_cases_y': 'peak'}, inplace=True)
weekly_rate['proximity_to_peak'] = weekly_rate['new_cases'] * 100 / weekly_rate['peak']
weekly_rate['text'] = weekly_rate['location'] + '<br>' + np.round(weekly_rate['proximity_to_peak'], 2).astype(str) + '%'
weekly_rate.fillna(value=0, inplace=True)

condition = [weekly_rate[weekly_rate['proximity_to_peak'] > 90],
             weekly_rate[(weekly_rate['proximity_to_peak'] > 75) & (weekly_rate['proximity_to_peak'] <= 90)],
             weekly_rate[weekly_rate['proximity_to_peak'] <= 75]]
name = ['>90%', '90 to 75%', '<75%']

for i in range(len(condition)):
    temp = condition[i]
    peak_map.add_trace(go.Scattergeo(locations=temp['location'],
                                     locationmode='country names',
                                     marker=dict(size=temp['proximity_to_peak'],
                                                 color=bubble_color[i],
                                                 sizemode='area'),
                                     name=name[i],
                                     text=temp['text']))

peak_map.update_layout(showlegend=True,
                       legend=dict(orientation='h',
                                   yanchor='top',
                                   xanchor='right',
                                   x=0.6, y=0.9,
                                   font=dict(color='#fff')),
                       geo=dict(landcolor='#63686F',
                                lataxis=dict(range=[66.57, -10.046630]),
                                oceancolor='#262625',
                                showocean=True,
                                showlakes=False,
                                showcountries=True,
                                bgcolor='#262625',
                                showframe=False
                                ),
                       paper_bgcolor='#262625',
                       plot_bgcolor='#262625',
                       height=800,
                       dragmode=False,
                       transition_duration=500,
                       margin=dict(t=0, b=0, l=0, r=0)
                       )

#################################### vaccination ########################
vaccinations_given = world_data[['location', 'new_vaccinations']].groupby(by='location').sum()
vaccinations_given = pd.merge(vaccinations_given,
                              world_data[world_data['population'] > 1000000][
                                  ['location', 'population']].drop_duplicates(), how='inner', on='location')
vaccinations_given['per_population'] = vaccinations_given['new_vaccinations'] / vaccinations_given['population']
top_vaccination = vaccinations_given.sort_values(by='per_population', ascending=True).tail(20)

top_vacc = go.Figure()
annotations = []

top_vacc.add_trace(go.Bar(x=top_vaccination['per_population'] * 100,
                          y=top_vaccination['location'],
                          marker=dict(color=fill_color[2],
                                      line=dict(color=fill_color[2],
                                                width=0.5)),
                          orientation='h'))

top_vacc.add_vline(x=80,
                   line_width=3,
                   line_dash='dash',
                   line_color='#44535F',
                   annotation_text='Enough to give 2 <br>doses to 40% of the population',
                   annotation_position='top',
                   annotation_font_color='#fff')

top_vacc.add_vline(x=160,
                   line_width=3,
                   line_dash='dash',
                   line_color='#44535F',
                   annotation_text='Enough to give 2 <br>doses to 80% of the population',
                   annotation_position='top',
                   annotation_font_color='#fff')

top_vacc.update_layout(title=dict(text='Countries reporting the most doses administered per population',
                                  font=dict(color='#fff')),
                       yaxis=dict(
                           showgrid=False,
                           showline=False,
                           showticklabels=True,
                           color='white',
                       ),
                       xaxis=dict(
                           zeroline=False,
                           showline=False,
                           showticklabels=True,
                           showgrid=True,
                           gridcolor='#404040',
                           color='white',
                       ),
                       showlegend=False,
                       margin=dict(l=10, r=10, t=70, b=70),
                       paper_bgcolor='#262625',
                       plot_bgcolor='#262625',
                       height=800,
                       dragmode=False,
                       )

#################################### vaccinations given #################
vaccinations = world_data[['location', 'people_vaccinated', 'people_fully_vaccinated']].groupby(by='location').max()
vaccinations = pd.merge(vaccinations, world_data[['location', 'population']].drop_duplicates(), how='left',
                        on='location')
vaccinations['people_vaccinated'] = np.round(vaccinations['people_vaccinated'] * 100 / vaccinations['population'], 2)
vaccinations['people_fully_vaccinated'] = np.round(
    vaccinations['people_fully_vaccinated'] * 100 / vaccinations['population'], 2)
vaccinations.fillna(value=0, inplace=True)
vaccinations.replace(np.inf, 0, inplace=True)
vaccinations['text'] = vaccinations["location"] + '<br>' + vaccinations[
    "people_vaccinated"].astype(str) + '% received at least one dose<br>' + vaccinations[
                           "people_fully_vaccinated"].astype(str) + '% have been fully vaccinated'

vac_worldmap = go.Figure(go.Choropleth(locations=vaccinations['location'],
                                       locationmode='country names',
                                       text=vaccinations['text'],
                                       z=vaccinations['people_vaccinated'],
                                       colorscale='speed',
                                       showlegend=False))

vac_worldmap.update_geos(projection=dict(type='orthographic',
                                         scale=1),
                         landcolor='#595D65',
                         oceancolor='#262625',
                         showocean=True,
                         showlakes=False,
                         showcountries=True,
                         bgcolor='#262625'
                         )

vac_worldmap.update_layout(paper_bgcolor='#262625',
                           plot_bgcolor='#262625',
                           height=800,
                           margin=dict(t=0, l=0, b=0, r=0))

vac_worldmap.update_traces(showscale=False)

#################################### vaccination speed ##################
# vaccination_speed = go.Figure()
# vaccination_speed_data = world_data[(world_data['date'] > '2020-11-30') & (world_data['population'] >= 10000000)][
#     ['date', 'location', 'new_vaccinations']].set_index('date').groupby(
#     by='location').resample('7D').mean().reset_index()
# locations = vaccination_speed_data['location'].unique()
#
# for i in locations:
#     df_sub = vaccination_speed_data[vaccination_speed_data['location'] == i]
#     df_sub['text'] = '7 day rolling avg: ' + df_sub['new_vaccinations'].astype(str)
#     vaccination_speed.add_trace(go.Scatter(x=df_sub['date'],
#                                            y=np.power(df_sub['new_vaccinations'], 1 / 2),
#                                            name=i,
#                                            text=df_sub['text'],
#                                            mode='lines',
#                                            line=dict(color='rgba(189, 204, 148, 0.3)',
#                                                      width=1.2),
#                                            connectgaps=True
#                                            ))
#
#     vaccination_speed.update_layout(title=dict(text='How fast are countries vaccinating?',
#                                                font=dict(color='#fff')),
#                                     yaxis=dict(
#                                         showgrid=False,
#                                         showline=False,
#                                         showticklabels=False,
#                                         color='white',
#                                     ),
#                                     xaxis=dict(
#                                         zeroline=False,
#                                         showline=False,
#                                         showticklabels=True,
#                                         showgrid=True,
#                                         gridcolor='#404040',
#                                         color='white',
#                                     ),
#                                     showlegend=False,
#                                     margin=dict(l=10, r=10, t=70, b=70),
#                                     paper_bgcolor='#262625',
#                                     plot_bgcolor='#262625',
#                                     height=600,
#                                     dragmode=False,
#                                     )

#################################### layout #############################
topCountry = world_data[world_data['date'] >= last_date - datetime.timedelta(days=13)][
    ['date', 'location', 'new_cases', 'new_deaths']].set_index('date')
topCountry = topCountry.groupby(by='location').resample('7D').mean()
topCountry.reset_index(inplace=True)

lastweek = topCountry[topCountry['date'] == topCountry.date.unique()[0]]
thisweek = topCountry[topCountry['date'] == topCountry.date.unique()[1]]
lastweek = lastweek.sort_values(by=['new_cases', 'new_deaths'], ascending=False).reset_index().drop('index', axis=1)
thisweek = thisweek.sort_values(by=['new_cases', 'new_deaths'], ascending=False).head(8).reset_index().drop('index',
                                                                                                            axis=1)

layout = html.Div([
    html.Div([
        html.H1('COVID-19',
                style={'color': '#E5D17F',
                       'width': '50%',
                       'margin': '0 auto',
                       'text-align': 'center',
                       'font-size': '50px',
                       'line-height': '56px',
                       'font-weight': '100'}),
        html.H4('Global',
                style={'color': '#E5D17F',
                       'width': '50%',
                       'margin': '0 auto',
                       'text-align': 'center',
                       'font-size': '24px',
                       'line-height': '30px',
                       'font-weight': '100'}
                )
    ]),
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
        ]),
        html.Div([
            html.P(
                dcc.Markdown(
                    f'**{top_cases["location"].tail(1).values[0]}** is global center of spreading with weekly new cases avarage'
                    f' {int(top_cases["new_cases"].tail(1).values[0])}.'),
                style={'width': '64%',
                       'margin': '44px auto',
                       'color': '#CBCCCF',
                       'text-align': 'center',
                       'font-size': '24px'
                       }
            ),
            html.P(
                f'There have been at least {int(data[data["location"] == "World"]["total_cases"].tail(1).values[0])} reported'
                f' infections and {int(data[data["location"] == "World"]["total_deaths"].tail(1).values[0])} reported deaths '
                f'caused by the new coronavirus so far.',
                style={'width': '64%',
                       'margin': '44px auto',
                       'color': '#CBCCCF',
                       'text-align': 'center',
                       'font-size': '24px'}
            ),
        ])
    ], style={'margin': '24px'}),
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
                       'border-radius': '20px'
                       }
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
    ], style={'margin': '24px'}),
    html.Section([
        html.P(
            children=[
                dcc.Markdown(
                    '## What this chart show?'),
                dcc.Markdown('''
                Corona virus hit some countries and territories harder than others. in these charts shows overtime 
                situation of top countries with highest 7 day rolling average on new cases and deaths last month.
        '''),
            ],
            style={'width': '64%',
                   'color': '#CBCCCF',
                   'margin': '44px auto'}),
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
                      'float': 'right'})]),
        html.Div([
            html.Table(id='top-country-comp',
                       children=[html.Th(['Countries reporting the most new infections each day '],
                                         style={'font-weight': '100'}),
                                 html.Th(['Countries reporting the most deaths each day'],
                                         style={'font-weight': '100'}),
                                 html.Tr(children=[html.Td(className='case-rate',
                                                           children=[html.Span(
                                                               dcc.Markdown(
                                                                   f'**{thisweek.loc[0, "location"]}**          '),
                                                               style={'color': fill_color[3]}),
                                                               dcc.Markdown(
                                                                   f'{int(np.rint(thisweek.loc[0, "new_cases"]))}           ',
                                                                   style={'display': 'inline-block',
                                                                          'width': '48%'}
                                                               ),
                                                               dcc.Markdown(
                                                                   f'**{np.round((thisweek.loc[0, "new_cases"] - lastweek[lastweek["location"] == thisweek.loc[0, "location"]]["new_cases"].values[0]) * 100 / thisweek.loc[0, "new_cases"], 3)}%**',
                                                                   style={'display': 'inline-block',
                                                                          'margin-left': '-200px',
                                                                          'width': '48%'}
                                                               )],
                                                           style={'margin-left': '10px'}),
                                                   html.Td(className='death-rate',
                                                           children=[html.Span(
                                                               dcc.Markdown(
                                                                   f'**{thisweek.loc[0, "location"]}**          '),
                                                               style={'color': fill_color[3]}),
                                                               dcc.Markdown(
                                                                   f'{int(np.rint(thisweek.loc[0, "new_deaths"]))}          ',
                                                                   style={'display': 'inline-block',
                                                                          'width': '48%'}),
                                                               dcc.Markdown(
                                                                   f'**{np.round((thisweek.loc[0, "new_deaths"] - lastweek[lastweek["location"] == thisweek.loc[0, "location"]]["new_deaths"].values[0]) * 100 / thisweek.loc[0, "new_deaths"], 3)}%**',
                                                                   style={'display': 'inline-block',
                                                                          'margin-left': '-200px',
                                                                          'width': '48%'})],
                                                           style={'margin-left': '10px'})]),
                                 html.Tr(children=[html.Td(className='case-rate',
                                                           children=[html.Span(
                                                               dcc.Markdown(
                                                                   f'**{thisweek.loc[1, "location"]}**          '),
                                                               style={'color': fill_color[3]}),
                                                               dcc.Markdown(
                                                                   f'{int(np.rint(thisweek.loc[1, "new_cases"]))}           ',
                                                                   style={'display': 'inline-block',
                                                                          'width': '48%'}),
                                                               dcc.Markdown(
                                                                   f'**{np.round((thisweek.loc[1, "new_cases"] - lastweek[lastweek["location"] == thisweek.loc[1, "location"]]["new_cases"].values[0]) * 100 / thisweek.loc[1, "new_cases"], 3)}%**',
                                                                   style={'display': 'inline-block',
                                                                          'margin-left': '-200px',
                                                                          'width': '48%'})],
                                                           style={'margin-left': '10px'}),
                                                   html.Td(className='death-rate',
                                                           children=[html.Span(
                                                               dcc.Markdown(
                                                                   f'**{thisweek.loc[1, "location"]}**          '),
                                                               style={'color': fill_color[3]}),
                                                               dcc.Markdown(
                                                                   f'{int(np.rint(thisweek.loc[1, "new_deaths"]))}          ',
                                                                   style={'display': 'inline-block',
                                                                          'width': '48%'}),
                                                               dcc.Markdown(
                                                                   f'**{np.round((thisweek.loc[1, "new_deaths"] - lastweek[lastweek["location"] == thisweek.loc[1, "location"]]["new_deaths"].values[0]) * 100 / thisweek.loc[1, "new_deaths"], 3)}%**',
                                                                   style={'display': 'inline-block',
                                                                          'margin-left': '-200px',
                                                                          'width': '48%'})],
                                                           style={'margin-left': '10px'})]),
                                 html.Tr(children=[html.Td(className='case-rate',
                                                           children=[html.Span(
                                                               dcc.Markdown(
                                                                   f'**{thisweek.loc[2, "location"]}**          '),
                                                               style={'color': fill_color[3]}),
                                                               dcc.Markdown(
                                                                   f'{int(np.rint(thisweek.loc[2, "new_cases"]))}           ',
                                                                   style={'display': 'inline-block',
                                                                          'width': '48%'}),
                                                               dcc.Markdown(
                                                                   f'**{np.round((thisweek.loc[2, "new_cases"] - lastweek[lastweek["location"] == thisweek.loc[2, "location"]]["new_cases"].values[0]) * 100 / thisweek.loc[2, "new_cases"], 3)}%**',
                                                                   style={'display': 'inline-block',
                                                                          'margin-left': '-200px',
                                                                          'width': '48%'})],
                                                           style={'margin-left': '10px'}),
                                                   html.Td(className='death-rate',
                                                           children=[html.Span(
                                                               dcc.Markdown(
                                                                   f'**{thisweek.loc[2, "location"]}**          '),
                                                               style={'color': fill_color[3]}),
                                                               dcc.Markdown(
                                                                   f'{int(np.rint(thisweek.loc[2, "new_deaths"]))}          ',
                                                                   style={'display': 'inline-block',
                                                                          'width': '48%'}),
                                                               dcc.Markdown(
                                                                   f'**{np.round((thisweek.loc[2, "new_deaths"] - lastweek[lastweek["location"] == thisweek.loc[2, "location"]]["new_deaths"].values[0]) * 100 / thisweek.loc[2, "new_deaths"], 3)}%**',
                                                                   style={'display': 'inline-block',
                                                                          'margin-left': '-200px',
                                                                          'width': '48%'})],
                                                           style={'margin-left': '10px'})]),
                                 html.Tr(children=[html.Td(className='case-rate',
                                                           children=[html.Span(
                                                               dcc.Markdown(
                                                                   f'**{thisweek.loc[3, "location"]}**          '),
                                                               style={'color': fill_color[3]}),
                                                               dcc.Markdown(
                                                                   f'{int(np.rint(thisweek.loc[3, "new_cases"]))}           ',
                                                                   style={'display': 'inline-block',
                                                                          'width': '48%'}),
                                                               dcc.Markdown(
                                                                   f'**{np.round((thisweek.loc[3, "new_cases"] - lastweek[lastweek["location"] == thisweek.loc[3, "location"]]["new_cases"].values[0]) * 100 / thisweek.loc[3, "new_cases"], 3)}%**',
                                                                   style={'display': 'inline-block',
                                                                          'margin-left': '-200px',
                                                                          'width': '48%'})],
                                                           style={'margin-left': '10px'}),
                                                   html.Td(className='death-rate',
                                                           children=[html.Span(
                                                               dcc.Markdown(
                                                                   f'**{thisweek.loc[3, "location"]}**          '),
                                                               style={'color': fill_color[3]}),
                                                               dcc.Markdown(
                                                                   f'{int(np.rint(thisweek.loc[3, "new_deaths"]))}          ',
                                                                   style={'display': 'inline-block',
                                                                          'width': '48%'}),
                                                               dcc.Markdown(
                                                                   f'**{np.round((thisweek.loc[3, "new_deaths"] - lastweek[lastweek["location"] == thisweek.loc[3, "location"]]["new_deaths"].values[0]) * 100 / thisweek.loc[3, "new_deaths"], 3)}%**',
                                                                   style={'display': 'inline-block',
                                                                          'margin-left': '-200px',
                                                                          'width': '48%'})],
                                                           style={'margin-left': '10px'})]),
                                 html.Tr(children=[html.Td(className='case-rate',
                                                           children=[html.Span(
                                                               dcc.Markdown(
                                                                   f'**{thisweek.loc[4, "location"]}**          '),
                                                               style={'color': fill_color[3]}),
                                                               dcc.Markdown(
                                                                   f'{int(np.rint(thisweek.loc[4, "new_cases"]))}           ',
                                                                   style={'display': 'inline-block',
                                                                          'width': '48%'}),
                                                               dcc.Markdown(
                                                                   f'**{np.round((thisweek.loc[4, "new_cases"] - lastweek[lastweek["location"] == thisweek.loc[4, "location"]]["new_cases"].values[0]) * 100 / thisweek.loc[4, "new_cases"], 3)}%**',
                                                                   style={'display': 'inline-block',
                                                                          'margin-left': '-200px',
                                                                          'width': '48%'})],
                                                           style={'margin-left': '10px'}),
                                                   html.Td(className='death-rate',
                                                           children=[html.Span(
                                                               dcc.Markdown(
                                                                   f'**{thisweek.loc[4, "location"]}**          '),
                                                               style={'color': fill_color[3]}),
                                                               dcc.Markdown(
                                                                   f'{int(np.rint(thisweek.loc[4, "new_deaths"]))}          ',
                                                                   style={'display': 'inline-block',
                                                                          'width': '48%'}),
                                                               dcc.Markdown(
                                                                   f'**{np.round((thisweek.loc[4, "new_deaths"] - lastweek[lastweek["location"] == thisweek.loc[4, "location"]]["new_deaths"].values[0]) * 100 / thisweek.loc[4, "new_deaths"], 3)}%**',
                                                                   style={'display': 'inline-block',
                                                                          'margin-left': '-200px',
                                                                          'width': '48%'})],
                                                           style={'margin-left': '10px'})]),
                                 html.Tr(children=[html.Td(className='case-rate',
                                                           children=[html.Span(
                                                               dcc.Markdown(
                                                                   f'**{thisweek.loc[5, "location"]}**          '),
                                                               style={'color': fill_color[3]}),
                                                               dcc.Markdown(
                                                                   f'{int(np.rint(thisweek.loc[5, "new_cases"]))}           ',
                                                                   style={'display': 'inline-block',
                                                                          'width': '48%'}),
                                                               dcc.Markdown(
                                                                   f'**{np.round((thisweek.loc[5, "new_cases"] - lastweek[lastweek["location"] == thisweek.loc[5, "location"]]["new_cases"].values[0]) * 100 / thisweek.loc[5, "new_cases"], 3)}%**',
                                                                   style={'display': 'inline-block',
                                                                          'margin-left': '-200px',
                                                                          'width': '48%'})],
                                                           style={'margin-left': '10px'}),
                                                   html.Td(className='death-rate',
                                                           children=[html.Span(
                                                               dcc.Markdown(
                                                                   f'**{thisweek.loc[5, "location"]}**          '),
                                                               style={'color': fill_color[3]}),
                                                               dcc.Markdown(
                                                                   f'{int(np.rint(thisweek.loc[5, "new_deaths"]))}          ',
                                                                   style={'display': 'inline-block',
                                                                          'width': '48%'}),
                                                               dcc.Markdown(
                                                                   f'**{np.round((thisweek.loc[5, "new_deaths"] - lastweek[lastweek["location"] == thisweek.loc[5, "location"]]["new_deaths"].values[0]) * 100 / thisweek.loc[5, "new_deaths"], 3)}%**',
                                                                   style={'display': 'inline-block',
                                                                          'margin-left': '-200px',
                                                                          'width': '48%'})],
                                                           style={'margin-left': '10px'})]),
                                 html.Tr(children=[html.Td(className='case-rate',
                                                           children=[html.Span(
                                                               dcc.Markdown(
                                                                   f'**{thisweek.loc[6, "location"]}**          '),
                                                               style={'color': fill_color[3]}),
                                                               dcc.Markdown(
                                                                   f'{int(np.rint(thisweek.loc[6, "new_cases"]))}           ',
                                                                   style={'display': 'inline-block',
                                                                          'width': '48%'}),
                                                               dcc.Markdown(
                                                                   f'**{np.round((thisweek.loc[6, "new_cases"] - lastweek[lastweek["location"] == thisweek.loc[6, "location"]]["new_cases"].values[0]) * 100 / thisweek.loc[6, "new_cases"], 3)}%**',
                                                                   style={'display': 'inline-block',
                                                                          'margin-left': '-200px',
                                                                          'width': '48%'})],
                                                           style={'margin-left': '10px'}),
                                                   html.Td(className='death-rate',
                                                           children=[html.Span(
                                                               dcc.Markdown(
                                                                   f'**{thisweek.loc[6, "location"]}**          '),
                                                               style={'color': fill_color[3]}),
                                                               dcc.Markdown(
                                                                   f'{int(np.rint(thisweek.loc[6, "new_deaths"]))}          ',
                                                                   style={'display': 'inline-block',
                                                                          'width': '48%'}),
                                                               dcc.Markdown(
                                                                   f'**{np.round((thisweek.loc[6, "new_deaths"] - lastweek[lastweek["location"] == thisweek.loc[6, "location"]]["new_deaths"].values[0]) * 100 / thisweek.loc[6, "new_deaths"], 3)}%**',
                                                                   style={'display': 'inline-block',
                                                                          'margin-left': '-200px',
                                                                          'width': '48%'})],
                                                           style={'margin-left': '10px'})]),
                                 html.Tr(children=[html.Td(className='case-rate',
                                                           children=[html.Span(
                                                               dcc.Markdown(
                                                                   f'**{thisweek.loc[7, "location"]}**          '),
                                                               style={'color': fill_color[3]}),
                                                               dcc.Markdown(
                                                                   f'{int(np.rint(thisweek.loc[7, "new_cases"]))}           ',
                                                                   style={'display': 'inline-block',
                                                                          'width': '48%'}),
                                                               dcc.Markdown(
                                                                   f'**{np.round((thisweek.loc[7, "new_cases"] - lastweek[lastweek["location"] == thisweek.loc[7, "location"]]["new_cases"].values[0]) * 100 / thisweek.loc[7, "new_cases"], 3)}%**',
                                                                   style={'display': 'inline-block',
                                                                          'margin-left': '-200px',
                                                                          'width': '48%'})],
                                                           style={'margin-left': '10px'}),
                                                   html.Td(className='death-rate',
                                                           children=[html.Span(
                                                               dcc.Markdown(
                                                                   f'**{thisweek.loc[7, "location"]}**          '),
                                                               style={'color': fill_color[3]}),
                                                               dcc.Markdown(
                                                                   f'{int(np.rint(thisweek.loc[7, "new_deaths"]))}          ',
                                                                   style={'display': 'inline-block',
                                                                          'width': '48%'}),
                                                               dcc.Markdown(
                                                                   f'**{np.round((thisweek.loc[7, "new_deaths"] - lastweek[lastweek["location"] == thisweek.loc[7, "location"]]["new_deaths"].values[0]) * 100 / thisweek.loc[7, "new_deaths"], 3)}%**',
                                                                   style={'display': 'inline-block',
                                                                          'margin-left': '-200px',
                                                                          'width': '48%'})],
                                                           style={'margin-left': '10px'})]),
                                 ], style={'color': '#fff', 'width': '100%', 'margin': '52px auto'})
        ])
    ]),
    html.P(
        children=[
            dcc.Markdown(
                '## Who is in the peak?'),
            dcc.Markdown('''
        COVID-19 has hit some countries far harder than others, though differences in the way infections are 
        counted locally make it impossible to make a perfect apples-to-apples comparison. '''),
            html.Br(),
            dcc.Markdown('''We want to know where infections are trending up or down relative to the size of the outbreak in each country. 
        So in these charts we use a rolling 7-day average of the new infections countries report each day and compare where 
        that average is now to where it was at its peak.'''),
            html.Br(),
            dcc.Markdown('''The percent of that peak a country currently reports 
        gives us a better idea of how far it is from containing the spread of the virus relative to the worst 
        days of its outbreak.
'''),
        ],
        style={'width': '64%',
               'color': '#CBCCCF',
               'margin': '44px auto'}),
    html.Section(
        html.Div([
            dcc.Graph(id='peak-map',
                      figure=peak_map,
                      config={
                          'displayModeBar': False
                      },
                      style={
                          'width': '100%'
                      }
                      )
        ])
        , style={'margin': '24px'}),
    html.P(
        children=[
            dcc.Markdown(
                '## Vaccination'),
            dcc.Markdown(f'''
        So far, at least 198 countries have begun vaccinating people for the coronavirus and have administered at least 
        {int(data[data['location'] == 'World']['total_vaccinations'].tail(1).values[0])} doses of the vaccine.
        '''),
            html.Br(),
            dcc.Markdown(f'''
            ***{vaccinations[['location', 'people_vaccinated']].sort_values(by='people_vaccinated', ascending=False).head(1).values[0][0]}*** 
            leads the world and has administered enough vaccine doses for 
            **{vaccinations[['location', 'people_vaccinated']].sort_values(by='people_vaccinated', ascending=False).head(1).values[0][1]}%** of 
            its population, assuming every person needs two doses.
            '''),
        ],
        style={'width': '64%',
               'color': '#CBCCCF',
               'margin': '44px auto'}),
    html.Section(
        html.Div([
            dcc.Graph(id='vacc-prog-bar',
                      figure=top_vacc,
                      config={
                          'displayModeBar': False
                      },
                      style={
                          'width': '100%',
                          'margin': '0 auto'
                      }
                      )
        ], style={
            'width': '100%'
        })
        , style={'margin': '24px'}),
    html.Section([
        html.Div([
            dcc.Graph(id='vaccination-map',
                      figure=vac_worldmap,
                      config={
                          'scrollZoom': False
                      },
                      style={'margin': '24px'}
                      )
        ])
    ], style={'margin': '24px'}),
    html.Section([
        html.P(
            children=[
                dcc.Markdown(
                    '## Do some countries have an advantage?'),
                dcc.Markdown(f'''
                Yes, generally richer and more developed countries have better health care infrastructure to manufacture
                , acquire and administer doses.
    '''),
                html.Br(),
                dcc.Markdown(f'''
                About **53%** of people who have received at least one dose of a coronavirus vaccine were from high income 
                countries, and at least **50%** were from Europe and North America. 
                ##### (Again, that only includes data from countries that report these figures. income levels categorise by country GDP per-capita recorded in world bank.)
        '''),
                html.Br(),
                dcc.Markdown(f'''
                ##### what it tells,
                ##### it tells how much people get at least one dose by population in different regions and different income level countries. marker size indicate people vaccinated at least one dose.
        '''),
            ],
            style={'width': '64%',
                   'color': '#CBCCCF',
                   'margin': '44px auto'}),
        html.Div([
            dcc.Tabs(id='compare-tabs', value=1,
                     children=[
                         dcc.Tab(label='Region', value=1, style={'color': '#fff',
                                                                 'background-color': '#262625'}),
                         dcc.Tab(label='Income', value=2, style={'color': '#fff',
                                                                 'background-color': '#262625'})
                     ], style={'width': '80%',
                               'margin': '0 auto'
                               })
        ]),
        html.Div([
            dcc.Graph(id='vaccination-advantage')
        ])
    ], style={'margin': '24px'}),
    # html.Section(
    #     html.Div([
    #         dcc.Graph(id='vaccination-speed',
    #                   figure=vaccination_speed)
    #     ])
    #     , style={'margin': '24px'})
])
