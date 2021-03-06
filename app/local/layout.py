import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import datetime

full_df = pd.read_pickle('app/data/sl_full_cleaned.pkl')
subset_vac = full_df[full_df['new_vaccinations'] > 0]
district_data = pd.read_csv('app/data/disdrict distribution.csv')

last2weeks = full_df[['new_cases']].tail(14)
last_week = last2weeks.head(7).ewm(span=2, adjust=True).mean().tail(1).values[0][0]
this_week = last2weeks.tail(7).ewm(span=2, adjust=True).mean().tail(1).values[0][0]

situation = 0

if (this_week - last_week) < 0:
    situation = 'falling'
else:
    situation = 'rissing'

############################## map ########################################################
worldmap = go.Figure(go.Scattergeo(mode='markers',
                                   lat=[7.8731],
                                   lon=[80.7718],
                                   showlegend=False,
                                   marker=dict(color='#E5D17F', size=5)))

worldmap.update_geos(projection=dict(type='orthographic',
                                     scale=0.7,
                                     rotation=dict(lon=80.7718)),
                     landcolor='#595D65',
                     oceancolor='#262625',
                     showocean=True,
                     showlakes=False,
                     showcountries=True,
                     bgcolor='#262625'
                     )

worldmap.update_layout(paper_bgcolor='#262625',
                       plot_bgcolor='#262625',
                       height=280,
                       margin=dict(t=0, l=0, b=0, r=0))

############################## vaccination progress #######################################

span = subset_vac.shape[0] / subset_vac['date'].dt.month.nunique()
subset_vac['EMA'] = subset_vac.loc[:, 'new_vaccinations'].ewm(span=span, adjust=False).mean()
current_rate = subset_vac.tail(1).EMA.values[0]
vaccinated_pop = full_df['total_vaccinations'].max()
vaccination_by_7days = \
    full_df[full_df['date'] > '2021-01-24'][['date', 'new_vaccinations']].resample('7D', on='date').agg(
        {'max', 'min', 'mean'})['new_vaccinations']
vaccination_lag = np.abs(
    vaccination_by_7days["mean"].tail(1).values[0] - vaccination_by_7days["mean"].max())
vaccination_lag = vaccination_lag * 100 / vaccination_by_7days["mean"].max()

to_vaccinate_by_portion = full_df['population'].head(1).values[0] * np.asarray(
    [0.1, 0.5, 0.73, 1]) - vaccinated_pop
days_by_current_rate = np.rint(to_vaccinate_by_portion / current_rate)
archive_date = [full_df['date'].max() + datetime.timedelta(days=int(days)) for days in days_by_current_rate]
X = (days_by_current_rate / np.sum(days_by_current_rate)) * 100

vaccination_progress = go.Figure()

top_label = ['10%', '50%', '73%', 'fully']
y_name = ['vaccination amount of population']
colors = ['#F2A488', '#F25C05', '#F24405', '#D90404']
widths = [0.15, 0.17, 0.22, 0.25]

for i in range(len(X)):
    vaccination_progress.add_trace(go.Bar(name=top_label[i],
                                          y=['vaccination'], x=[X[i]],
                                          orientation='h',
                                          marker=dict(color=colors[i],
                                                      line_color=colors[i]),
                                          width=widths[i]))

vaccination_progress.update_layout(xaxis=dict(showgrid=False,
                                              showline=False,
                                              showticklabels=False,
                                              zeroline=False),
                                   yaxis=dict(showgrid=False,
                                              showline=False,
                                              showticklabels=False,
                                              zeroline=True),
                                   legend=dict(font=dict(color='#fff')),
                                   barmode='stack',
                                   showlegend=False,
                                   width=900,
                                   paper_bgcolor='#262625',
                                   plot_bgcolor='#262625',
                                   margin=dict(t=0, b=0, l=40, r=10))

annotations = []

annotations.append(dict(xref='paper', yref='y',
                        x=0.14, y=y_name[0],
                        xanchor='right',
                        text=str(y_name[0]),
                        font=dict(size=12,
                                  color='#fff'),
                        showarrow=False,
                        align='right'))

annotations.append(dict(xref='x', yref='paper',
                        x=X[0] / 2, y=0.35,
                        text=f'{top_label[0]}<br>{archive_date[0].date()}',
                        font=dict(color='#8C8274'),
                        showarrow=False))

space = X[0]
for i in range(1, len(X)):
    annotations.append(dict(xref='x', yref='paper',
                            x=space + (X[i] / 2), y=0.35,
                            text=f'{top_label[i]}<br>{archive_date[i].date()}',
                            font=dict(color='#8C8274'),
                            showarrow=False))
    space += X[i]

vaccination_progress.update_layout(annotations=annotations)

################################# vaccination counts #########################################

vaccination_trend = go.Figure()
vaccination_trend.add_trace(
    go.Scatter(name='people vaccinated',
               x=subset_vac['date'], y=subset_vac['people_vaccinated'],
               fill='tozeroy', mode='lines',
               line_color='#CEF2D7'))
vaccination_trend.add_trace(
    go.Scatter(name='people fully vaccinated',
               x=subset_vac['date'], y=subset_vac['people_fully_vaccinated'],
               fill='tozeroy', mode='lines',
               line_color='#94BF36'))

vaccination_trend.update_layout(
    xaxis=dict(title='Date',
               showgrid=False,
               showline=False,
               color='white',
               zeroline=False),
    yaxis=dict(title='Count',
               gridcolor='#404040',
               gridwidth=1,
               showline=False,
               color='white'),
    legend=dict(orientation='h',
                yanchor='top',
                xanchor='right',
                x=1, y=1.15,
                font=dict(color='#fff')),
    paper_bgcolor='#262625',
    plot_bgcolor='#262625',
    height=500,
    transition_duration=500)

annotations = []

annotations.append(dict(xref='paper', x=1.1, y=subset_vac['people_vaccinated'].max(),
                        xanchor='right', yanchor='middle',
                        text='{}%'.format(
                            np.round(
                                (subset_vac['people_vaccinated'].max() * 100) / full_df['population'].head(1).values[
                                    0]), 2),
                        font=dict(color='#CEF2D7'),
                        showarrow=False))

annotations.append(dict(xref='paper', x=1.1, y=subset_vac['people_fully_vaccinated'].max(),
                        xanchor='right', yanchor='middle',
                        text='{}%'.format(
                            np.round((subset_vac['people_fully_vaccinated'].max() * 100) /
                                     full_df['population'].head(1).values[
                                         0]), 2),
                        font=dict(color='#94BF36'),
                        showarrow=False))

annotations.append(dict(xref='paper', yref='paper',
                        x=0, y=1.25,
                        xanchor='left', yanchor='bottom',
                        text='Percent of population vaccinated',
                        font=dict(size=16,
                                  color='#fff'),
                        showarrow=False),
                   )

vaccination_trend.update_layout(annotations=annotations)

############################## infection rate after vaccination starts ####################
infection_trend = go.Figure()
infection_trend.add_trace(
    go.Scatter(name='rolling avg. of new infections',
               x=subset_vac['date'],
               y=((subset_vac.loc[:, 'new_cases'] / np.max(subset_vac['new_cases'])).ewm(span=5,
                                                                                         adjust=False).mean()) * 100,
               mode='lines',
               line=dict(width=2.5),
               line_color='#CEF2D7'))
infection_trend.add_trace(
    go.Scatter(name='rolling avg. of new deaths',
               x=subset_vac['date'],
               y=((subset_vac.loc[:, 'new_deaths'] / np.max(subset_vac['new_deaths'])).ewm(span=5,
                                                                                           adjust=False).mean()) * 100,
               mode='lines',
               line=dict(width=2.5),
               line_color='#94BF36'))

infection_trend.update_layout(
    xaxis=dict(title='Date',
               showgrid=False,
               showline=False,
               color='white',
               zeroline=False),
    yaxis=dict(title='Count',
               gridcolor='#404040',
               gridwidth=1,
               showline=False,
               color='white'),
    legend=dict(orientation='h',
                yanchor='top',
                xanchor='right',
                x=1, y=1.15,
                font=dict(color='#fff')),
    paper_bgcolor='#262625',
    plot_bgcolor='#262625',
    height=500,
    transition_duration=500)

annotations = []

annotations.append(dict(xref='paper', yref='paper',
                        x=0, y=1.25,
                        xanchor='left', yanchor='bottom',
                        text='Daily averages as % of peak',
                        font=dict(size=16,
                                  color='#fff'),
                        showarrow=False),
                   )

infection_trend.update_layout(annotations=annotations)

############################# vaccination efficeincy #########################
vaccination_eff = go.Figure()
vaccination_eff.add_trace(
    go.Bar(x=vaccination_by_7days.index,
           y=vaccination_by_7days['min'],
           name='minimum',
           marker=dict(color='#ADBF1F'))
)
vaccination_eff.add_trace(
    go.Bar(x=vaccination_by_7days.index,
           y=vaccination_by_7days['mean'],
           name='average',
           marker=dict(color='#537345'))
)
vaccination_eff.add_trace(
    go.Bar(x=vaccination_by_7days.index,
           y=vaccination_by_7days['max'],
           name='maximum',
           marker=dict(color='#2F591C'))
)

vaccination_eff.update_layout(
    title=dict(text='Weekly vaccinated Avg. change',
               font=dict(color='#fff')),
    xaxis=dict(title='Date',
               showgrid=False,
               showline=False,
               color='white',
               zeroline=False),
    yaxis=dict(title='Change',
               gridcolor='#404040',
               gridwidth=1,
               showline=False,
               color='white'),
    legend=dict(orientation='h',
                yanchor='top',
                xanchor='right',
                x=1, y=1.09,
                font=dict(color='#fff')),
    paper_bgcolor='#262625',
    plot_bgcolor='#262625',
    height=500,
    transition_duration=500)

############################# new vaccinations by day ########################

vaccination_day = go.Figure()
vaccination_day.add_trace(
    go.Bar(x=subset_vac['date'],
           y=subset_vac['new_vaccinations'],
           marker=dict(line=dict(width=0),
                       color='#515559'),
           )
)
vaccination_day.add_trace(
    go.Scatter(x=subset_vac['date'],
               y=subset_vac['new_vaccinations'],
               mode='lines',
               line=dict(color='#F2CE16', width=2.5)
               )
)

vaccination_day.update_layout(
    title=dict(text='New vaccinations',
               font=dict(color='#fff')),
    xaxis=dict(title='Date',
               showgrid=False,
               showline=False,
               color='white',
               zeroline=False),
    yaxis=dict(title='Change',
               gridcolor='#404040',
               gridwidth=1,
               showline=False,
               color='white'),
    showlegend=False,
    paper_bgcolor='#262625',
    plot_bgcolor='#262625',
    height=500,
    transition_duration=500)

############################# clusters duration ##############################
cluster_duration = go.Figure()

time_line = pd.DataFrame([
    dict(cluster='Random and Returned <br>from other countries',
         start='2020-05-01', end='2021-05-18', cases=4400,
         text=f'name:Random and Returned <br>from other countries<br>start:2020-05-01<br>end:2021-05-18<br>cases:4400'),
    dict(cluster='Navy Personal and <br>their close contacts',
         start='2020-05-01', end='2020-07-11', cases=1057,
         text=f'name:Navy Personal and <br>their close contacts<br>start:2020-05-01<br>end:2020-07-11<br>cases:1057'),
    dict(cluster='Kandakadu cluster & <br>their close contacts',
         start='2020-07-16', end='2020-09-23', cases=651,
         text=f'name:Kandakadu cluster & <br>their close contacts<br>start:2020-07-16<br>end:2020-09-23<br>cases:651'),
    dict(cluster='Brandix Minuwangoda', start='2020-10-05',
         end='2021-05-18', cases=98282,
         text=f'name:Brandix Minuwangoda<br>start:2021-05-18<br>end:2020-10-05<br>cases:98282'),
    dict(cluster='3rd wave (new year)', start='2021-04-28',
         end='2021-05-18', cases=47775,
         text=f'name:3rd wave (new year)<br>start:2021-05-18<br>end:2021-04-28<br>cases:47775')
])

cluster_duration = px.timeline(time_line,
                               x_start='start', x_end='end', y='cluster',
                               color=np.log(time_line['cases']), color_continuous_scale=px.colors.sequential.speed,
                               hover_data=['cluster', 'start', 'end', 'cases'])
cluster_duration.update_yaxes(autorange='reversed')
cluster_duration.update_layout(
    title=dict(text='Clusters & active period',
               font=dict(color='#fff')),
    xaxis=dict(title='Date',
               showgrid=False,
               showline=False,
               color='white',
               zeroline=False),
    yaxis=dict(gridcolor='#404040',
               gridwidth=1,
               showline=False,
               color='white'),
    showlegend=False,
    coloraxis_showscale=False,
    paper_bgcolor='#262625',
    plot_bgcolor='#262625',
    height=500,
    transition_duration=500,
    margin=dict(l=10))

############################# total cases of each clusters ###################
cluster_cases = go.Figure(go.Pie(labels=time_line['cluster'],
                                 values=np.sqrt(time_line['cases']),
                                 textinfo='label+percent',
                                 text=time_line['text'],
                                 outsidetextfont=dict(color='#fff'),
                                 insidetextorientation='radial',
                                 marker_colors=px.colors.sequential.speed))
cluster_cases.update_layout(
    title=dict(text='Clusters & total cases',
               font=dict(color='#fff')),
    xaxis=dict(showgrid=False,
               showline=False,
               color='white',
               zeroline=False),
    yaxis=dict(showgrid=False,
               showline=False,
               color='white'),
    showlegend=False,
    coloraxis_showscale=False,
    paper_bgcolor='#262625',
    plot_bgcolor='#262625',
    height=500,
    transition_duration=500,
    margin=dict(l=10))

############################# cluster grow ###################################
cluster_grow = go.Figure()
cluster = pd.read_csv('app/data/clusters.csv')
for col in cluster.select_dtypes(include=np.number).columns:
    cluster[col] = cluster[col].diff()
    cluster[col].fillna(value=0, inplace=True)
    cluster[col] = np.abs(cluster[col])
cluster.set_index('Date', inplace=True)
cluster_graw_rate = cluster.ewm(span=7, adjust=False).mean()
cluster_graw_rate.reset_index(inplace=True)
cluster_graw_rate.rename(columns={'index': 'date'}, inplace=True)
cluster_graw_rate['Date'] = pd.to_datetime(cluster_graw_rate['Date'])
line_colors = ['#95A617', '#3FA663', '#2D7345', '#25594A', '#3391A6']

cluster_grow = go.Figure(
    layout=go.Layout(updatemenus=[dict(type='buttons',
                                       direction='left',
                                       pad={'r': 10, 't': 87},
                                       x=0.1,
                                       xanchor='right',
                                       y=0,
                                       yanchor='top',
                                       )],
                     xaxis=dict(range=[cluster_graw_rate['Date'].min(), cluster_graw_rate['Date'].max()],
                                autorange=False, title_text='date'),
                     yaxis=dict(range=[0, 3000], autorange=True, title_text='change'))
)

init = 0

for i in range(1, cluster_graw_rate.shape[1]):
    cluster_grow.add_trace(
        go.Scatter(x=[cluster_graw_rate.loc[init, 'Date']],
                   y=[cluster_graw_rate.loc[init, cluster_graw_rate.columns[i]]],
                   name=cluster_graw_rate.columns[i],
                   mode='lines', line=dict(color=line_colors[i - 1],
                                           width=3.2))
    )

cluster_grow.update(frames=[go.Frame(data=[go.Scatter(x=cluster_graw_rate.loc[:k, 'Date'],
                                                      y=cluster_graw_rate.loc[:k, col]) for col in
                                           cluster_graw_rate.columns[1:]]) for k in
                            range(init + 1, cluster_graw_rate.shape[0], 5)])

cluster_grow.update_layout(updatemenus=[dict(buttons=list([dict(label='play',
                                                                method='animate',
                                                                args=[None, {'frame': {'duration': 300}}])]),
                                             font=dict(size=16,
                                                       color='#fff'),
                                             bordercolor='#fff'
                                             )])
cluster_grow.update_layout(
    title=dict(text='Cluster growing rate',
               font=dict(color='#fff')),
    xaxis=dict(title='Date',
               showgrid=False,
               showline=False,
               color='white',
               zeroline=False),
    yaxis=dict(title='Change',
               gridcolor='#404040',
               gridwidth=1,
               showline=False,
               color='white'),
    legend=dict(font=dict(color='#fff')),
    paper_bgcolor='#262625',
    plot_bgcolor='#262625',
    height=500)

############################# trace radar ####################################
first_wave = ['2020-03-11', '2020-09-23']
second_wave = ['2020-10-05', '2021-04-01']
third_wave = ['2021-04-28', '2021-05-17']
categories = ['total_cases', 'total_deaths', 'hosp_patients', 'total_tests']

first_wave = full_df[(full_df['date'] >= first_wave[0]) & (full_df['date'] <= first_wave[1])]
second_wave = full_df[(full_df['date'] >= second_wave[0]) & (full_df['date'] <= second_wave[1])]
third_wave = full_df[(full_df['date'] >= third_wave[0]) & (full_df['date'] <= third_wave[1])]
first_wave_stats = [np.max(first_wave[x]) for x in first_wave[categories]]
second_wave_stats = [np.max(second_wave[x]) for x in second_wave[categories]]
third_wave_stats = [np.max(third_wave[x]) for x in third_wave[categories]]

trace_radar = make_subplots(rows=1, cols=3,
                            specs=[[{'type': 'polar'}, {'type': 'polar'}, {'type': 'polar'}]]
                            )
stats = [first_wave_stats, second_wave_stats, third_wave_stats]
names = ['first wave', 'second wave', 'third wave']

for i in range(len(stats)):
    trace_radar.add_trace(go.Scatterpolar(r=np.power(stats[i], 1 / 5),
                                          theta=categories,
                                          fill='toself',
                                          fillcolor=line_colors[i],
                                          opacity=0.5,
                                          textfont=dict(color='#fff'),
                                          line=dict(color=line_colors[i]),
                                          name=names[i]),
                          row=1, col=i + 1)

trace_radar.update_polars(radialaxis=dict(color='#fff'),
                          angularaxis=dict(color='#fff'))

trace_radar.update_layout(
    polar=dict(radialaxis=dict(visible=True,
                               gridcolor='#404040',
                               ),
               bgcolor='#262625',
               ),
    polar2=dict(radialaxis=dict(visible=True,
                                gridcolor='#404040',
                                ),
                bgcolor='#262625',
                ),
    polar3=dict(radialaxis=dict(visible=True,
                                gridcolor='#404040',
                                ),
                bgcolor='#262625',
                ),
    title=dict(text='Waves',
               font=dict(color='#fff')),
    legend=dict(font=dict(color='#fff')),
    paper_bgcolor='#262625',
    plot_bgcolor='#262625',
    height=425
)
############################# is lockdown works #############################
examin_lockdown = go.Figure()
examin_lockdown.add_trace(go.Scatter(x=full_df['date'], y=full_df['new_cases'],
                                     mode='lines', line=dict(color='#497364', width=2.5),
                                     name='observed'))
examin_lockdown.add_trace(go.Scatter(x=full_df['date'], y=full_df['new_deaths'],
                                     mode='lines', line=dict(color='#FF1D23', width=2.5),
                                     name='observed'))

examin_lockdown.add_vrect(x0='2020-03-18', x1='2020-05-10',
                          annotation_text='island wide lockdown',
                          annotation_position='top left',
                          annotation_font_color='#fff',
                          fillcolor='#FF665A', opacity=0.25, line_width=0)

examin_lockdown.add_vrect(x0='2020-11-02', x1='2021-03-31',
                          annotation_text='some areas under lockdown',
                          annotation_position='top left',
                          annotation_font_color='#fff',
                          fillcolor='#F2B705', opacity=0.25, line_width=0)

examin_lockdown.add_vrect(x0='2021-04-01', x1='2021-05-02',
                          annotation_text='recommended travel restriction',
                          annotation_position='top left',
                          annotation_font_color='#fff',
                          fillcolor='#A6BF4B', opacity=0.25, line_width=0)

examin_lockdown.update_layout(
    xaxis=dict(title='Date',
               showgrid=False,
               showline=False,
               color='white',
               zeroline=False),
    yaxis=dict(title='Count',
               gridcolor='#404040',
               gridwidth=1,
               showline=False,
               color='white'),
    legend=dict(font=dict(color='#fff')),
    paper_bgcolor='#262625',
    plot_bgcolor='#262625',
    height=650,
    transition_duration=500)

############################# layouts ########################################
layout = html.Div([
    html.Div([
        dcc.Graph(id='location',
                  figure=worldmap,
                  style={'width': '50%',
                         'margin': '0 auto'},
                  config={'modeBarButtonsToRemove': ['pan2d']}),
        html.H1(id='country',
                children='Sri Lanka',
                style={'color': '#E5D17F',
                       'width': '50%',
                       'margin': '0 auto',
                       'text-align': 'center',
                       'font-size': '50px',
                       'line-height': '56px',
                       'font-weight': '100'}),
        html.H2(id='contry-trend',
                children=dcc.Markdown(
                    f'**{np.round(full_df["new_cases"].tail(1).values[0] * 100 / np.max(full_df["new_cases"]), 2)}**% of peak '
                    f'and {situation}'),
                style={'color': '#E5D17F',
                       'width': '50%',
                       'margin': '0 auto',
                       'text-align': 'center',
                       'font-size': '24px',
                       'line-height': '30px',
                       'font-weight': '100'}
                ),
        html.H4(id='contry-infection-rate',
                children=dcc.Markdown(
                    f'**{int(np.rint(np.sum(full_df["new_cases"].tail(7)) * 100000 / np.max(full_df["population"])))}**'
                    f' infections per 100K people reported last 7 days'),
                style={'width': '50%',
                       'margin': '44px auto',
                       'color': '#fff',
                       'font-weight': '100',
                       'text-align': 'center'}
                )
    ]),
    html.Div([
        html.H2(
            id='local-header',
            children=f'Average number of new infections reported in Sri Lanka each day reaches new high: '
                     f'Now reporting more than {int(np.rint(full_df["new_cases"].tail(7).mean()))} daily.'
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
                style={'width': '76%',
                       'border-radius': '20px'}
            ),
            dcc.Dropdown(
                id='area-type-dropdown',
                options=[
                    {'label': 'total cases', 'value': 'total_cases'},
                    {'label': 'total deaths', 'value': 'total_deaths'},
                    {'label': 'total tests', 'value': 'total_tests'},
                ],
                value='total_cases',
                style={'width': '76%',
                       'border-radius': '20px'}
            )
        ],
            style={'width': '30%',
                   'display': 'flex',
                   'justify-content': 'space-between'}),
        dcc.Graph(id='area-graph')
    ]),
    # html.Hr(className='section-divider',
    #         style={'padding': '0 0', 'margin': '44px auto'}),
    html.P(
        dcc.Markdown(
            f'There have been **{int(full_df["total_cases"].max())}** infections and **{int(full_df["total_deaths"].max())}** '
            f'coronavirus-related deaths reported in the country since the pandemic began.'),
        style={'width': '64%',
               'margin': '44px auto',
               'color': '#fff'}),
    html.Div([
        html.H3('Daily reported trends', style={'color': '#fff',
                                                'margin': '44px auto',
                                                'width': '64%'}),
        html.Div([
            html.Label('New infections', style={'color': '#fff'}),
            dcc.Graph(id='new-case-dist'),
        ], style={'width': '50%',
                  'display': 'inline-block'}),
        html.Div([
            html.Label('Deaths', style={'color': '#fff'}),
            dcc.Graph(id='new-death-dist'),
        ], style={'width': '50%',
                  'display': 'inline-block',
                  'float': 'right'}),
        html.Div([
            dcc.Slider(
                id='predict-for',
                min=0,
                max=28,
                value=0,
                marks={'0': 0, '7': 7, '14': 14, '21': 21, '28': 28},
                step=None
            )
        ], style={'width': '50%',
                  'margin': '0 auto'})
    ]),
    # html.Hr(className='section-divider',
    #         style={'padding': '0 0', 'margin': '44px auto'}),
    html.Div([
        html.H3('Vaccination', style={'color': '#fff',
                                      'margin': '44px auto',
                                      'width': '64%'}),
        html.P(
            dcc.Markdown(
                f'Sri Lanka has administered at least **{int(full_df["people_vaccinated"].max())}**'
                f' doses of COVID vaccines so far. Assuming every person needs 2 doses, that???s enough to have vaccinated about '
                f'**{np.round((full_df["people_vaccinated"].max() * 100) / (2 * full_df["population"].head(1).values[0]), 3)}%** of the country???s population.',
                style={'color': '#fff',
                       'margin': '44px auto',
                       'width': '64%'})),
        html.Div([html.P(),
                  dcc.Graph(id='vac-area',
                            figure=vaccination_trend)], style={'width': '50%',
                                                               'display': 'inline-block'}),
        html.Div([html.P(),
                  dcc.Graph(id='infec-trand',
                            figure=infection_trend)], style={'width': '50%',
                                                             'float': 'right',
                                                             'display': 'inline-block'}),
        html.Div([
            html.P(
                dcc.Markdown(
                    f'During the last week reported, Sri Lanka averaged about '
                    f'**{int(np.rint(current_rate))}** doses administered '
                    f'each day. At that rate, it will take a further **{int(np.rint(full_df["population"].head(1) * 0.1 / current_rate))}** days to administer enough doses '
                    f'for another **{10}%** of the population.'),
                style={'width': '64%',
                       'margin': '44px auto'}),
            html.P(
                dcc.Markdown(
                    f'It is going at a rate of about **{int(np.rint(np.mean(full_df["new_vaccinations"].tail(7))))}** '
                    f'doses per day during the last week which is about **{np.round(vaccination_lag, 3)}%** '
                    f'slower than its fastest 7-day pace.'),
                style={'width': '64%',
                       'margin': '44px auto'}),
            html.H5([
                'This vaccine rollout data is reported by the number of doses of coronavirus vaccines administered, not '
                'the number of people who have been vaccinated. Because most vaccines require two doses and many countries'
                ' have different schedules to deliver the second dose, we don???t know with this data how many people have '
                'ultimately received both doses.',
            ], style={'color': '#fff',
                      'margin': '44px auto',
                      'width': '64%'}),
            dcc.Graph(id='vac-prog',
                      figure=vaccination_progress)], style={'width': '80%',
                                                            'margin': '0 auto'})
    ]),
    html.Div([
        html.P(
            children=[dcc.Markdown(
                'Vaccines offered: **Oxford-AstraZeneca**, **Sinopharm**, **Sputnik V**, **Pfizer-BioNTech**'),
                dcc.Markdown(
                    'Vaccination priority groups People are being offered a vaccine based on ??? occupation and age.')],
            style={'width': '64%',
                   'margin': '44px auto'}),
        html.Div([
            dcc.Graph(id='vaccination-eff',
                      figure=vaccination_eff)
        ], style={'width': '50%',
                  'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='new-vaccination-by-day',
                      figure=vaccination_day)
        ], style={'width': '50%',
                  'float': 'right',
                  'display': 'inline-block'})
    ]),
    html.Div([
        html.P(
            children=[
                dcc.Markdown(
                    '## What this chart show?'),
                dcc.Markdown('''
                This graph compare new cases recorded in  each administrate district with overall island record. through
                out pandemic western province and it's district are hit harder than other district in sri lanka. this cause
                a huge impact to country economy because western province give more than 60% contribution to economy in 
                sri lanka.
                * color of bubble indicate amount of test done in each day
                * new cases reported indicate by size of the bubbles
                '''),
            ],
            style={'width': '64%',
                   'margin': '44px auto'}),
        html.Div([
            dcc.Graph(id='district_bubble')
        ], style={'width': '80%',
                  'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(id='dist-year-dropdown',
                         options=[
                             {'label': '2020', 'value': 2020},
                             {'label': '2021', 'value': 2021},
                         ],
                         value=0,
                         style={'width': '76%',
                                'border-radius': '20px',
                                'margin-top': '12px'}
                         ),
            dcc.Dropdown(id='dist-month-dropdown',
                         options=[],
                         value=0,
                         style={'width': '76%',
                                'border-radius': '20px',
                                'margin-top': '12px'}),
            dcc.Dropdown(id='dist-district-dropdown',
                         options=[{'label': dist, 'value': dist} for dist in
                                  district_data.select_dtypes(include=np.number).columns],
                         value='COLOMBO',
                         style={'width': '76%',
                                'border-radius': '20px',
                                'margin-top': '12px'})
        ], style={'width': '20%',
                  'display': 'inline-block',
                  'float': 'right'})
    ]),
    html.Div([
        html.H3('Clusters', style={'color': '#fff',
                                   'margin': '44px auto',
                                   'width': '64%'}),
        html.P(
            children=[
                dcc.Markdown('''
                Other than first two clusters major clusters are Minuwangoda Branidx and third wave (new year) clusters
                report very quick spread all over the country and more deaths. in third wave reported 33% present of all
                cases less than month wih setting new recorded . 
        '''),
            ],
            style={'width': '64%',
                   'margin': '44px auto'}),
        html.Div([
            dcc.Graph(id='cluster-duration',
                      figure=cluster_duration)
        ], style={'width': '60%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='cluster-proportion',
                      figure=cluster_cases)
        ], style={'width': '40%',
                  'display': 'inline-block',
                  'float': 'right'})
    ]),
    html.Div([
        dcc.Graph(id='cluster-growing-rate',
                  figure=cluster_grow)
    ]),
    html.P(
        dcc.Markdown('''
        ### what it tells,
        
        these radars provide simple numerical scale for each wave occurred so far and indicate each wave's magnitude
         on various factors. to get clear idea compare numbers in circular axis in each radar.
    '''),
        style={'width': '64%',
               'margin': '44px auto'}
    ),
    html.Div([
        dcc.Graph(id='wave-trace',
                  figure=trace_radar)
    ]),
    html.H3('Lockdowns', style={'color': '#fff',
                                'margin': '44px auto',
                                'width': '64%'}),
    html.P(
        dcc.Markdown('''
        As COVID-19 infections began to be reported around the world, many countries responded by shutting down places 
        like schools, workplaces and international borders in order to contain the spread of the virus. 
        This chart shows how different lockdown measures were implemented during the course of the pandemic. education
        sector is most effected by pandemic. major examinations postponed several times and grade one administration also
        postponed. still country do not open for tourists after ukraine tourists group visited country recorded new variations
        of virus and again boarders were close to tourists.
        '''),
        style={'width': '64%',
               'margin': '44px auto'}
    ),
    html.Div([
        dcc.Dropdown(id='lock-downs',
                     options=[
                         {'label': 'education', 'value': 'education'},
                         {'label': 'workplaces', 'value': 'workplaces'},
                         {'label': 'borders', 'value': 'borders'},
                     ],
                     value='education',
                     style={'width': '34%',
                            'border-radius': '20px',
                            'margin-bottom': '12px'}
                     ),
        dcc.Graph(id='lock-down-effect'),
        html.H3('Is lockdown a solution ?', style={'color': '#fff',
                                                   'margin': '44px auto',
                                                   'width': '64%'}),
        html.P(
            dcc.Markdown('''
            not a full solution but a part of a solution, how? lockdown helps to low the curve which getting higher by day
            then give breathing space to health crew to do their work. but this happens when decision made at right time.
    '''),
            style={'width': '64%',
                   'margin': '44px auto'}
        ),
        dcc.Graph(id='is-lockdown-works',
                  figure=examin_lockdown)
    ]),
    html.Div([
        html.H3('How Sri Lanka compares', style={'color': '#fff',
                                                 'margin': '44px auto',
                                                 'width': '64%'}),
        html.P(
            dcc.Markdown('''
            There is no one perfect statistic to compare the outbreaks different countries have experienced during this 
            pandemic. Looking at a variety of metrics gives you a more complete view of the virus??? toll on each country. 
            These charts show several different statistics, each with their own strengths and weaknesses, that mark the 
            various ways each country???s outbreak compares in its region and the world.
        '''),
            style={'width': '64%',
                   'margin': '44px auto'}
        ),
        html.Div([
            dcc.Tabs(id='compare-tabs', value=1,
                     children=[
                         dcc.Tab(label='Total infections and deaths', value=1, style={'color': '#fff',
                                                                                      'background-color': '#262625'}),
                         dcc.Tab(label='Total per population', value=2, style={'color': '#fff',
                                                                               'background-color': '#262625'}),
                         dcc.Tab(label='Average daily reported', value=3, style={'color': '#fff',
                                                                                 'background-color': '#262625'}),
                     ], style={'width': '80%',
                               'margin': '0 auto'
                               }),
            html.Div([
                html.Div([
                    dcc.Graph(id='state-comp_infection',
                              ),
                    dcc.Graph(id='state-comp_death',
                              )
                ], style={'width': '40%',
                          'display': 'inline-block'}),
                html.Div([
                    dcc.Graph(id='global_state-comp_infection',
                              ),
                    dcc.Graph(id='global_state-comp_death',
                              )
                ], style={'width': '40%',
                          'display': 'inline-block',
                          'float': 'right'})
            ])
        ]),
    ])
])
