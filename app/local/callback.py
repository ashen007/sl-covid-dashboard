import numpy as np
import warnings
from dash.dependencies import Input
from dash.dependencies import Output
import plotly.graph_objs as go
import pandas as pd
import datetime

import statsmodels.api as sm

full_df = pd.read_pickle('app/data/sl_full_cleaned.pkl')
subset_vac = full_df[full_df['new_vaccinations'] > 0]


def register_callbacks(dash_app):
    @dash_app.callback(Output('area-graph', 'figure'),
                       Input('area-dropdown', 'value'),
                       Input('area-type-dropdown', 'value'))
    def update_graph(duration_value, type_of_graph):
        if duration_value == 'all-time':
            fig = go.Figure(
                go.Scatter(x=full_df['date'], y=full_df[type_of_graph], fill='tozeroy', mode='lines',
                           line_color='#568C6D'))

        else:
            temp = full_df[full_df['year'] == int(duration_value)]
            fig = go.Figure(go.Scatter(x=temp['date'], y=temp[type_of_graph], fill='tozeroy', mode='lines',
                                       line_color='#568C6D'))

        fig.update_layout(
            xaxis=dict(title='Date',
                       showgrid=False,
                       showline=False,
                       color='white',
                       zeroline=False),
            yaxis=dict(title='Count',
                       gridcolor='#3B3659',
                       gridwidth=1,
                       showline=False,
                       color='white'),
            paper_bgcolor='#2A2D40',
            plot_bgcolor='#2A2D40',
            height=600,
            transition_duration=500)

        return fig

    @dash_app.callback(Output('new-case-dist', 'figure'),
                       Input('predict-for', 'value'))
    def forecast_cases(selected_peried):
        last_update = full_df['date'].max()
        end_date = last_update + datetime.timedelta(days=selected_peried)
        selected_peried = int(selected_peried)

        if selected_peried == 0:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=full_df['date'], y=full_df['new_cases'],
                                     mode='lines', line=dict(color='#497364', width=2.5),
                                     name='observed'))
        else:
            warnings.filterwarnings("ignore")
            mod = sm.tsa.statespace.SARIMAX(full_df.set_index('date')['new_cases'],
                                            order=(0, 1, 1),
                                            seasonal_order=(1, 1, 1, 12),
                                            enforce_stationarity=False,
                                            enforce_invertibility=False)

            results = mod.fit()
            new_cases = results.get_prediction(start=last_update, end=end_date, dynamic=False).conf_int()

            new_cases.loc[last_update] = [
                full_df[full_df['date'] == last_update]['new_cases'].values[0],
                full_df[full_df['date'] == last_update]['new_cases'].values[0]]
            new_cases = new_cases.reset_index().rename(columns={'index': 'date'})

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=full_df['date'].tail(28), y=full_df['new_cases'].tail(28),
                                     mode='lines', line=dict(color='#497364', width=2.5),
                                     name='observed'),
                          )
            fig.add_trace(go.Scatter(x=new_cases['date'], y=new_cases['upper new_cases'],
                                     mode='lines', line=dict(color='#F2620F', width=3),
                                     name='worse'))
            fig.add_trace(go.Scatter(x=new_cases['date'], y=[np.mean(row) for row in np.asarray(
                new_cases[['lower new_cases', 'upper new_cases']])],
                                     mode='lines', line=dict(color='#7BA65D', width=2.5),
                                     name='normal'))
            fig.add_trace(go.Scatter(x=new_cases['date'], y=new_cases['lower new_cases'],
                                     mode='lines', line=dict(color='#F2E205', width=2.5),
                                     name='better'))

        fig.update_layout(
            xaxis=dict(title='Date',
                       showgrid=False,
                       showline=False,
                       color='white',
                       zeroline=False),
            yaxis=dict(title='Count',
                       gridcolor='#3B3659',
                       gridwidth=1,
                       showline=False,
                       color='white'),
            legend=dict(font=dict(color='#fff')),
            paper_bgcolor='#2A2D40',
            plot_bgcolor='#2A2D40',
            height=600,
            transition_duration=500)

        return fig

    @dash_app.callback(Output('new-death-dist', 'figure'),
                       Input('predict-for', 'value'))
    def forecast_deaths(selected_peried):
        last_update = full_df['date'].max()
        end_date = last_update + datetime.timedelta(days=selected_peried)
        selected_peried = int(selected_peried)
        if selected_peried == 0:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=full_df['date'], y=full_df['new_deaths'],
                                     mode='lines', line=dict(color='#497364', width=2.5),
                                     name='observed'))
        else:
            warnings.filterwarnings("ignore")
            mod_death = sm.tsa.statespace.SARIMAX(full_df.set_index('date')['new_deaths'],
                                                  order=(1, 1, 1),
                                                  seasonal_order=(0, 1, 1, 12),
                                                  enforce_stationarity=False,
                                                  enforce_invertibility=False)

            results_death = mod_death.fit()
            new_deaths = results_death.get_prediction(start=last_update, end=end_date, dynamic=False).conf_int()
            new_deaths['lower new_deaths'] = new_deaths['lower new_deaths'].apply(lambda x: 0 if x < 0 else x)

            new_deaths.loc[last_update] = [
                full_df[full_df['date'] == last_update]['new_deaths'].values[0],
                full_df[full_df['date'] == last_update]['new_deaths'].values[0]]
            new_deaths = new_deaths.reset_index().rename(columns={'index': 'date'})

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=full_df['date'].tail(28), y=full_df['new_deaths'].tail(28),
                                     mode='lines', line=dict(color='#497364', width=2.5),
                                     name='observed'),
                          )
            fig.add_trace(go.Scatter(x=new_deaths['date'], y=new_deaths['upper new_deaths'],
                                     mode='lines', line=dict(color='#F2620F', width=3),
                                     name='worse'))
            fig.add_trace(go.Scatter(x=new_deaths['date'], y=[np.mean(row) for row in np.asarray(
                new_deaths[['lower new_deaths', 'upper new_deaths']])],
                                     mode='lines', line=dict(color='#7BA65D', width=2.5),
                                     name='normal'))
            fig.add_trace(go.Scatter(x=new_deaths['date'], y=new_deaths['lower new_deaths'],
                                     mode='lines', line=dict(color='#F2E205', width=2.5),
                                     name='better'))

        fig.update_layout(
            xaxis=dict(title='Date',
                       showgrid=False,
                       showline=False,
                       color='white',
                       zeroline=False),
            yaxis=dict(title='Count',
                       gridcolor='#3B3659',
                       gridwidth=1,
                       showline=False,
                       color='white'),
            legend=dict(font=dict(color='#fff')),
            paper_bgcolor='#2A2D40',
            plot_bgcolor='#2A2D40',
            height=600,
            transition_duration=500)

        return fig

    # @dash_app.callback(Output('vac-lines', 'figure'))
    # def vaccination_progress():
    #
    #
    #     return fig
    #
    # @dash_app.callback(Output('vac-area', 'figure'))
    # def vaccination_area():

    #
    #     return fig
