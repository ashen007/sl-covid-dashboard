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
vaccination_speed = go.Figure()
vaccination_speed_data = world_data[world_data['date'] > '2020-11-30'][
    ['date', 'location', 'new_vaccinations']].set_index('date').groupby(
    by='location').resample('7D').mean().reset_index()
locations = vaccination_speed_data['location'].unique()

for i in locations:
    df_sub = vaccination_speed_data[vaccination_speed_data['location'] == i]
    df_sub['text'] = '7 day rolling avg: ' + df_sub['new_vaccinations'].astype(str)
    vaccination_speed.add_trace(go.Scatter(x=df_sub['date'],
                                           y=np.power(df_sub['new_vaccinations'], 1 / 2),
                                           name=i,
                                           text=df_sub['text'],
                                           mode='lines',
                                           line=dict(color='rgba(189, 204, 148, 0.3)',
                                                     width=1.2),
                                           connectgaps=True
                                           ))

    vaccination_speed.update_layout(title=dict(text='How fast are countries vaccinating?',
                                               font=dict(color='#fff')),
                                    yaxis=dict(
                                        showgrid=False,
                                        showline=False,
                                        showticklabels=False,
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
                                    height=600,
                                    dragmode=False,
                                    )

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
        ], style={'margin': '24px'}),
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
                          'float': 'right'})]),
            html.Div([
                html.Table(id='top-country-comp',
                           children=[html.Tr(children=[html.Td(className='case-rate',
                                                               children=[html.Span(
                                                                   dcc.Markdown(
                                                                       f'**{thisweek.loc[0, "location"]}**   '),
                                                                   style={'color': fill_color[3]}),
                                                                   dcc.Markdown(
                                                                       f'{int(np.rint(thisweek.loc[0, "new_cases"]))}   '
                                                                       f'**{np.round((thisweek.loc[0, "new_cases"] - lastweek[lastweek["location"] == thisweek.loc[0, "location"]]["new_cases"].values[0]) * 100 / thisweek.loc[0, "new_cases"], 3)}%**')],
                                                               style={'margin-left': '10px'}),
                                                       html.Td(className='death-rate',
                                                               children=[html.Span(
                                                                   dcc.Markdown(
                                                                       f'**{thisweek.loc[0, "location"]}**   '),
                                                                   style={'color': fill_color[3]}),
                                                                   dcc.Markdown(
                                                                       f'{int(np.rint(thisweek.loc[0, "new_deaths"]))}   '
                                                                       f'**{np.round((thisweek.loc[0, "new_deaths"] - lastweek[lastweek["location"] == thisweek.loc[0, "location"]]["new_deaths"].values[0]) * 100 / thisweek.loc[0, "new_deaths"], 3)}%**')],
                                                               style={'margin-left': '10px'})]),
                                     html.Tr(children=[html.Td(className='case-rate',
                                                               children=[html.Span(
                                                                   dcc.Markdown(
                                                                       f'**{thisweek.loc[1, "location"]}**   '),
                                                                   style={'color': fill_color[3]}),
                                                                   dcc.Markdown(
                                                                       f'{int(np.rint(thisweek.loc[1, "new_cases"]))}   '
                                                                       f'**{np.round((thisweek.loc[1, "new_cases"] - lastweek[lastweek["location"] == thisweek.loc[1, "location"]]["new_cases"].values[0]) * 100 / thisweek.loc[1, "new_cases"], 3)}%**')],
                                                               style={'margin-left': '10px'}),
                                                       html.Td(className='death-rate',
                                                               children=[html.Span(
                                                                   dcc.Markdown(
                                                                       f'**{thisweek.loc[1, "location"]}**   '),
                                                                   style={'color': fill_color[3]}),
                                                                   dcc.Markdown(
                                                                       f'{int(np.rint(thisweek.loc[1, "new_deaths"]))}   '
                                                                       f'**{np.round((thisweek.loc[1, "new_deaths"] - lastweek[lastweek["location"] == thisweek.loc[1, "location"]]["new_deaths"].values[0]) * 100 / thisweek.loc[1, "new_deaths"], 3)}%**')],
                                                               style={'margin-left': '10px'})]),
                                     html.Tr(children=[html.Td(className='case-rate',
                                                               children=[html.Span(
                                                                   dcc.Markdown(
                                                                       f'**{thisweek.loc[2, "location"]}**   '),
                                                                   style={'color': fill_color[3]}),
                                                                   dcc.Markdown(
                                                                       f'{int(np.rint(thisweek.loc[2, "new_cases"]))}   '
                                                                       f'**{np.round((thisweek.loc[2, "new_cases"] - lastweek[lastweek["location"] == thisweek.loc[2, "location"]]["new_cases"].values[0]) * 100 / thisweek.loc[2, "new_cases"], 3)}%**')],
                                                               style={'margin-left': '10px'}),
                                                       html.Td(className='death-rate',
                                                               children=[html.Span(
                                                                   dcc.Markdown(
                                                                       f'**{thisweek.loc[2, "location"]}**   '),
                                                                   style={'color': fill_color[3]}),
                                                                   dcc.Markdown(
                                                                       f'{int(np.rint(thisweek.loc[2, "new_deaths"]))}   '
                                                                       f'**{np.round((thisweek.loc[2, "new_deaths"] - lastweek[lastweek["location"] == thisweek.loc[2, "location"]]["new_deaths"].values[0]) * 100 / thisweek.loc[2, "new_deaths"], 3)}%**')],
                                                               style={'margin-left': '10px'})]),
                                     html.Tr(children=[html.Td(className='case-rate',
                                                               children=[html.Span(
                                                                   dcc.Markdown(
                                                                       f'**{thisweek.loc[3, "location"]}**   '),
                                                                   style={'color': fill_color[3]}),
                                                                   dcc.Markdown(
                                                                       f'{int(np.rint(thisweek.loc[3, "new_cases"]))}   '
                                                                       f'**{np.round((thisweek.loc[3, "new_cases"] - lastweek[lastweek["location"] == thisweek.loc[3, "location"]]["new_cases"].values[0]) * 100 / thisweek.loc[3, "new_cases"], 3)}%**')],
                                                               style={'margin-left': '10px'}),
                                                       html.Td(className='death-rate',
                                                               children=[html.Span(
                                                                   dcc.Markdown(
                                                                       f'**{thisweek.loc[3, "location"]}**   '),
                                                                   style={'color': fill_color[3]}),
                                                                   dcc.Markdown(
                                                                       f'{int(np.rint(thisweek.loc[3, "new_deaths"]))}   '
                                                                       f'**{np.round((thisweek.loc[3, "new_deaths"] - lastweek[lastweek["location"] == thisweek.loc[3, "location"]]["new_deaths"].values[0]) * 100 / thisweek.loc[3, "new_deaths"], 3)}%**')],
                                                               style={'margin-left': '10px'})]),
                                     html.Tr(children=[html.Td(className='case-rate',
                                                               children=[html.Span(
                                                                   dcc.Markdown(
                                                                       f'**{thisweek.loc[4, "location"]}**   '),
                                                                   style={'color': fill_color[3]}),
                                                                   dcc.Markdown(
                                                                       f'{int(np.rint(thisweek.loc[4, "new_cases"]))}   '
                                                                       f'**{np.round((thisweek.loc[4, "new_cases"] - lastweek[lastweek["location"] == thisweek.loc[4, "location"]]["new_cases"].values[0]) * 100 / thisweek.loc[4, "new_cases"], 3)}%**')],
                                                               style={'margin-left': '10px'}),
                                                       html.Td(className='death-rate',
                                                               children=[html.Span(
                                                                   dcc.Markdown(
                                                                       f'**{thisweek.loc[4, "location"]}**   '),
                                                                   style={'color': fill_color[3]}),
                                                                   dcc.Markdown(
                                                                       f'{int(np.rint(thisweek.loc[4, "new_deaths"]))}   '
                                                                       f'**{np.round((thisweek.loc[4, "new_deaths"] - lastweek[lastweek["location"] == thisweek.loc[4, "location"]]["new_deaths"].values[0]) * 100 / thisweek.loc[4, "new_deaths"], 3)}%**')],
                                                               style={'margin-left': '10px'})]),
                                     html.Tr(children=[html.Td(className='case-rate',
                                                               children=[html.Span(
                                                                   dcc.Markdown(
                                                                       f'**{thisweek.loc[5, "location"]}**   '),
                                                                   style={'color': fill_color[3]}),
                                                                   dcc.Markdown(
                                                                       f'{int(np.rint(thisweek.loc[5, "new_cases"]))}   '
                                                                       f'**{np.round((thisweek.loc[5, "new_cases"] - lastweek[lastweek["location"] == thisweek.loc[5, "location"]]["new_cases"].values[0]) * 100 / thisweek.loc[5, "new_cases"], 3)}%**')],
                                                               style={'margin-left': '10px'}),
                                                       html.Td(className='death-rate',
                                                               children=[html.Span(
                                                                   dcc.Markdown(
                                                                       f'**{thisweek.loc[5, "location"]}**   '),
                                                                   style={'color': fill_color[3]}),
                                                                   dcc.Markdown(
                                                                       f'{int(np.rint(thisweek.loc[5, "new_deaths"]))}   '
                                                                       f'**{np.round((thisweek.loc[5, "new_deaths"] - lastweek[lastweek["location"] == thisweek.loc[5, "location"]]["new_deaths"].values[0]) * 100 / thisweek.loc[5, "new_deaths"], 3)}%**')],
                                                               style={'margin-left': '10px'})]),
                                     html.Tr(children=[html.Td(className='case-rate',
                                                               children=[html.Span(
                                                                   dcc.Markdown(
                                                                       f'**{thisweek.loc[6, "location"]}**   '),
                                                                   style={'color': fill_color[3]}),
                                                                   dcc.Markdown(
                                                                       f'{int(np.rint(thisweek.loc[6, "new_cases"]))}   '
                                                                       f'**{np.round((thisweek.loc[6, "new_cases"] - lastweek[lastweek["location"] == thisweek.loc[6, "location"]]["new_cases"].values[0]) * 100 / thisweek.loc[6, "new_cases"], 3)}%**')],
                                                               style={'margin-left': '10px'}),
                                                       html.Td(className='death-rate',
                                                               children=[html.Span(
                                                                   dcc.Markdown(
                                                                       f'**{thisweek.loc[6, "location"]}**   '),
                                                                   style={'color': fill_color[3]}),
                                                                   dcc.Markdown(
                                                                       f'{int(np.rint(thisweek.loc[6, "new_deaths"]))}   '
                                                                       f'**{np.round((thisweek.loc[6, "new_deaths"] - lastweek[lastweek["location"] == thisweek.loc[6, "location"]]["new_deaths"].values[0]) * 100 / thisweek.loc[6, "new_deaths"], 3)}%**')],
                                                               style={'margin-left': '10px'})]),
                                     html.Tr(children=[html.Td(className='case-rate',
                                                               children=[html.Span(
                                                                   dcc.Markdown(
                                                                       f'**{thisweek.loc[7, "location"]}**   '),
                                                                   style={'color': fill_color[3]}),
                                                                   dcc.Markdown(
                                                                       f'{int(np.rint(thisweek.loc[7, "new_cases"]))}   '
                                                                       f'**{np.round((thisweek.loc[7, "new_cases"] - lastweek[lastweek["location"] == thisweek.loc[7, "location"]]["new_cases"].values[0]) * 100 / thisweek.loc[7, "new_cases"], 3)}%**')],
                                                               style={'margin-left': '10px'}),
                                                       html.Td(className='death-rate',
                                                               children=[html.Span(
                                                                   dcc.Markdown(
                                                                       f'**{thisweek.loc[7, "location"]}**   '),
                                                                   style={'color': fill_color[3]}),
                                                                   dcc.Markdown(
                                                                       f'{int(np.rint(thisweek.loc[7, "new_deaths"]))}   '
                                                                       f'**{np.round((thisweek.loc[7, "new_deaths"] - lastweek[lastweek["location"] == thisweek.loc[7, "location"]]["new_deaths"].values[0]) * 100 / thisweek.loc[7, "new_deaths"], 3)}%**')],
                                                               style={'margin-left': '10px'})]),
                                     ], style={'color': '#fff', 'width': '100%', 'margin': '52px auto'})
            ])
        ]),
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
                          }
                          )
            ])
        ], style={'margin': '24px'}),
        html.Section([
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
        html.Section(
            html.Div([
                dcc.Graph(id='vaccination-speed',
                          figure=vaccination_speed)
            ])
            , style={'margin': '24px'})
    ])
