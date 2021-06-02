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
            go.Scatter(x=temp['date'], y=temp[indexes[1]].ewm(alpha=0.1).mean(), fill='tozeroy',mode='lines', line_color=colors[0]))
        total_situation.add_trace(
            go.Scatter(x=temp['date'], y=temp[indexes[2]], fill='tozeroy', mode='lines', line_color=colors[1]))

        new_situation.update_layout(situation_updater)
        total_situation.update_layout(situation_updater)

        return new_situation, total_situation
