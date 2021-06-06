import numpy as np
import warnings
from dash.dependencies import Input
from dash.dependencies import Output
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import datetime

data = pd.read_csv('app/data/owid-covid-data.csv')
data.fillna(value=0, inplace=True)
data['date'] = pd.to_datetime(data['date'])
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


def register_callbacks(dash_app):
    @dash_app.callback(Output('global-situation-new', 'figure'),
                       Output('global-situation-total', 'figure'),
                       Input('situation-dropdown', 'value'))
    def global_situation(measure):
        new_situation = go.Figure()
        total_situation = go.Figure()
        situation_updater = dict(xaxis=dict(title='Date',
                                            showgrid=False,
                                            showline=False,
                                            color='white',
                                            zeroline=False),
                                 yaxis=dict(title='Count',
                                            gridcolor='#404040',
                                            gridwidth=1,
                                            showline=False,
                                            color='white'),
                                 paper_bgcolor='#262625',
                                 plot_bgcolor='#262625',
                                 height=500,
                                 transition_duration=500)

        if measure == 1:
            indexes = ['date', 'new_cases', 'total_cases']
        elif measure == 2:
            indexes = ['date', 'new_deaths', 'total_deaths']
        else:
            indexes = ['date', 'new_vaccinations', 'total_vaccinations']

        temp = data[data['location'] == 'World'][indexes]

        new_situation.add_trace(
            go.Scatter(x=temp['date'], y=temp[indexes[1]].ewm(alpha=0.1).mean(), fill='tozeroy', mode='lines',
                       line_color=colors[0]))
        total_situation.add_trace(
            go.Scatter(x=temp['date'], y=temp[indexes[2]], fill='tozeroy', mode='lines', line_color=colors[1]))

        new_situation.update_layout(situation_updater)
        total_situation.update_layout(situation_updater)

        return new_situation, total_situation

    @dash_app.callback(Output('vaccination-advantage', 'figure'),
                       Input('compare-tabs', 'value'))
    def vaccination_advantage(level):
        vaccinations_bubble = world_data[['continent', 'location', 'people_vaccinated']].groupby(
            by=['continent', 'location']).max()
        # vaccinations_bubble.drop(0, inplace=True)
        continent_pop = world_data[['continent', 'location', 'population']].groupby(by=['continent', 'location']).max()
        # continent_pop.drop(0, inplace=True)
        vacc_by_continent = pd.merge(vaccinations_bubble.reset_index(), continent_pop.reset_index(), how='left',
                                     on=['continent', 'location'])
        vacc_by_continent['text'] = vacc_by_continent['location'].astype(str) + '<br>' + vacc_by_continent[
            'population'].astype(str) + '<br>' + np.round(
            vacc_by_continent['people_vaccinated'] * 100 / vacc_by_continent['population'], 2).astype(str)

        def levels(x):
            if x >= 12630:
                return 'high'
            elif 12630 > x >= 4050:
                return 'upper middle'
            elif 4050 > x >= 1080:
                return 'lower middle'
            else:
                return 'low'

        country_income = world_data[['location', 'gdp_per_capita']].groupby(by='location').max().reset_index()
        country_income['level'] = country_income['gdp_per_capita'].apply(levels)
        vaccinations_bubble_income = world_data[['location', 'people_vaccinated']].groupby(
            by=['location']).max().reset_index()
        by_income = pd.merge(vaccinations_bubble_income, country_income, how='left', on='location')
        by_income = pd.merge(by_income, vacc_by_continent[['location', 'population']], how='left', on='location')
        by_income['text'] = by_income['location'].astype(str) + '<br>' + by_income[
            'population'].astype(str) + '<br>' + np.round(
            by_income['people_vaccinated'] * 100 / by_income['population'], 2).astype(str)

        if level == 1:
            vac_advantage = go.Figure()
            vac_advantage.add_trace(
                go.Scatter(x=vacc_by_continent['people_vaccinated'] * 100 / vacc_by_continent['population'],
                           y=vacc_by_continent['continent'],
                           text=vacc_by_continent['text'],
                           marker_size=np.power(vacc_by_continent['people_vaccinated'], 1 / 2.5)))
        else:
            vac_advantage = go.Figure()
            vac_advantage.add_trace(go.Scatter(x=by_income['people_vaccinated'] * 100 / by_income['population'],
                                               y=by_income['level'],
                                               text=by_income['text'],
                                               marker_size=np.power(by_income['people_vaccinated'], 1 / 2.5)))

        vac_advantage.update_traces(mode='markers',
                                    marker=dict(color=colors[4],
                                                sizemode='area',
                                                line_width=1))
        vac_advantage.update_layout(xaxis=dict(title='',
                                               showgrid=True,
                                               showline=False,
                                               gridcolor='#404040',
                                               gridwidth=1,
                                               color='white',
                                               zeroline=False),
                                    yaxis=dict(title='',
                                               showgrid=False,
                                               showline=False,
                                               color='white'),
                                    paper_bgcolor='#262625',
                                    plot_bgcolor='#262625',
                                    height=800,
                                    transition_duration=500)

        return vac_advantage
