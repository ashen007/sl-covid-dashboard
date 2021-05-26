import numpy as np
import warnings
from dash.dependencies import Input
from dash.dependencies import Output
import plotly.graph_objs as go
# import plotly.figure_factory as ff
import pandas as pd
import datetime

import statsmodels.api as sm

full_df = pd.read_pickle('app/data/sl_full_cleaned.pkl')


def register_callbacks(dash_app):
    @dash_app.callback(Output('area-graph', 'figure'),
                       Input('area-dropdown', 'value'),
                       Input('area-type-dropdown', 'value'))
    def update_graph(duration_value, type_of_graph):
        if duration_value == 'all-time':
            fig = go.Figure(
                go.Scatter(x=full_df['date'], y=full_df[type_of_graph], fill='tozeroy', mode='lines',
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

    @dash_app.callback(Output('vac-lines', 'figure'))
    def vaccination_line():
        subset_vac = full_df[full_df['new_vaccinations'] > 0]
        span = subset_vac.shape[0] / subset_vac['date'].dt.month.nunique()
        subset_vac['EMA'] = subset_vac.loc[:, 'new_vaccinations'].ewm(span=span, adjust=False).mean()
        current_rate = subset_vac.tail(1).EMA.values[0]
        vaccinated_pop = full_df['total_vaccinations'].max()

        to_vaccinate_by_portion = full_df['population'].head(1).values[0] * np.asarray(
            [0.1, 0.5, 0.73, 1]) - vaccinated_pop
        days_by_current_rate = np.rint(to_vaccinate_by_portion / current_rate)
        archive_date = [full_df['date'].max() + datetime.timedelta(days=int(days)) for days in days_by_current_rate]
        X = (days_by_current_rate / np.sum(days_by_current_rate)) * 100

        figure = go.Figure()

        top_label = ['10%', '50%', '73%', 'fully']
        y_name = ['vaccination amount of population']
        colors = ['#F2A488', '#F25C05', '#F24405', '#D90404']
        widths = [0.15, 0.17, 0.22, 0.25]

        for i in range(len(X)):
            figure.add_trace(go.Bar(name=top_label[i],
                                    y=['vaccination'], x=[X[i]],
                                    orientation='h',
                                    marker=dict(color=colors[i],
                                                line_color=colors[i]),
                                    width=widths[i]))

        figure.update_layout(xaxis=dict(showgrid=False,
                                        showline=False,
                                        showticklabels=False,
                                        zeroline=False),
                             yaxis=dict(showgrid=False,
                                        showline=False,
                                        showticklabels=False,
                                        zeroline=True),
                             barmode='stack',
                             showlegend=False,
                             width=1200,
                             paper_bgcolor='#2A2D40',
                             plot_bgcolor='#2A2D40',
                             margin=dict(l=40, r=10, t=40, b=40))

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

        figure.update_layout(annotations=annotations)

        return figure
