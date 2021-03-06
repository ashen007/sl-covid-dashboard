import numpy as np
import warnings
from dash.dependencies import Input
from dash.dependencies import Output
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import datetime

import statsmodels.api as sm

full_df = pd.read_pickle('app/data/sl_full_cleaned.pkl')
subset_vac = full_df[full_df['new_vaccinations'] > 0]
district_data = pd.read_csv('app/data/disdrict distribution.csv')
district_data['Date'] = pd.to_datetime(district_data['Date'])
district_data.rename(columns={'Date': 'date'}, inplace=True)
dist = pd.merge(right=full_df[full_df['date'] > '2020-03-31'][['date', 'new_tests', 'new_cases']],
                left=district_data,
                on='date')
districts = dist.select_dtypes(include=np.number).columns[:-2]
world_data = pd.read_csv('app/data/owid-covid-data.csv')
world_data.fillna(value=0, inplace=True)

for district in districts:
    dist[district] = dist[district].diff()
    dist[district].fillna(value=0, inplace=True)

dist.drop(np.where(dist['COLOMBO'] == dist['COLOMBO'].max())[0][0], inplace=True)


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
                       gridcolor='#404040',
                       gridwidth=1,
                       showline=False,
                       color='white'),
            paper_bgcolor='#262625',
            plot_bgcolor='#262625',
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
                       gridcolor='#404040',
                       gridwidth=1,
                       showline=False,
                       color='white'),
            legend=dict(font=dict(color='#fff')),
            paper_bgcolor='#262625',
            plot_bgcolor='#262625',
            height=500,
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
                       gridcolor='#404040',
                       gridwidth=1,
                       showline=False,
                       color='white'),
            legend=dict(font=dict(color='#fff')),
            paper_bgcolor='#262625',
            plot_bgcolor='#262625',
            height=500,
            transition_duration=500)

        return fig

    @dash_app.callback(Output('district_bubble', 'figure'),
                       Input('dist-year-dropdown', 'value'),
                       Input('dist-month-dropdown', 'value'),
                       Input('dist-district-dropdown', 'value'))
    def district_distribution(year, month, select_district):
        if (isinstance(year, str)) & (year is not None):
            year = int(year)
        if (isinstance(month, str)) & (month is not None):
            month = int(month)

        if year is None:
            year = 0
        if month is None:
            month = 0

        hover_text = []

        part_1 = dist[['date', 'new_cases', 'new_tests']]
        part_2 = dist.drop(['date', 'new_cases', 'new_tests'], axis=1)
        temp = pd.concat([part_1, np.abs(part_2[select_district])], axis=1)

        for index, row in temp.iterrows():
            hover_text.append(('Date:{date}<br>' +
                               'new cases:{new_ca}<br>' +
                               'new cases for island wide:{new_ca_is}<br>' +
                               'test done:{new_ts}').format(date=row['date'],
                                                            new_ca=row[select_district],
                                                            new_ca_is=row['new_cases'],
                                                            new_ts=row['new_tests']
                                                            ))
        temp['text'] = hover_text

        if year == 0 & month == 0:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=temp['new_cases'], y=temp[select_district],
                                     name=select_district,
                                     mode='markers', marker=dict(size=np.sqrt(np.abs(temp[select_district])),
                                                                 color=temp['new_tests'],
                                                                 colorscale='PiYG'),
                                     text=temp['text']))

        if year != 0:
            if month != 0:
                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(x=temp[(temp['date'].dt.year == year) & (temp['date'].dt.month == month)]['new_cases'],
                               y=temp[(temp['date'].dt.year == year) & (temp['date'].dt.month == month)][
                                   select_district],
                               name=select_district,
                               mode='markers',
                               marker=dict(size=np.sqrt(np.abs(
                                   temp[(temp['date'].dt.year == year) & (temp['date'].dt.month == month)][
                                       select_district])),
                                   color=
                                   temp[(temp['date'].dt.year == year) & (temp['date'].dt.month == month)][
                                       'new_tests'],
                                   colorscale='PiYG'),
                               text=temp[(temp['date'].dt.year == year) & (temp['date'].dt.month == month)]['text']))
            elif month == 0:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=temp[temp['date'].dt.year == year]['new_cases'],
                                         y=temp[temp['date'].dt.year == year][select_district],
                                         name=select_district,
                                         mode='markers',
                                         marker=dict(
                                             size=np.sqrt(np.abs(temp[temp['date'].dt.year == year][select_district])),
                                             color=temp[temp['date'].dt.year == year]['new_tests'],
                                             colorscale='PiYG'),
                                         text=temp[temp['date'].dt.year == year]['text']))

        fig.update_layout(
            xaxis=dict(title='new cases island wide',
                       showgrid=False,
                       showline=False,
                       color='white',
                       zeroline=False),
            yaxis=dict(title=f'new cases in {select_district}',
                       gridcolor='#404040',
                       gridwidth=1,
                       showline=False,
                       color='white'),
            legend=dict(font=dict(color='#fff')),
            paper_bgcolor='#262625',
            plot_bgcolor='#262625',
            height=750,
            transition_duration=500)

        return fig

    @dash_app.callback(Output('dist-month-dropdown', 'options'),
                       Input('dist-year-dropdown', 'value'))
    def update_month(year):
        return [{'label': i, 'value': i} for i in
                district_data[district_data['date'].dt.year == year]['date'].dt.month.unique()]

    @dash_app.callback(Output('lock-down-effect', 'figure'),
                       Input('lock-downs', 'value'))
    def lockdown_timeline(sector):
        lockdown_data = pd.read_csv('app/data/lockdowns.csv')
        fig = px.timeline(lockdown_data[lockdown_data['type'] == sector],
                          x_start='from',
                          x_end='till',
                          y='nationwide',
                          color='level',
                          color_discrete_sequence=px.colors.diverging.delta_r,
                          )

        fig.update_layout(
            title=dict(text='Lock Downs',
                       font=dict(color='#fff')),
            xaxis=dict(title='Date',
                       showgrid=False,
                       showline=False,
                       color='white',
                       zeroline=False),
            yaxis=dict(title='',
                       gridcolor='#404040',
                       gridwidth=1,
                       showline=False,
                       color='white'),
            legend=dict(title=dict(text='levels',
                                   font=dict(color='#fff')),
                        orientation='h',
                        yanchor='top',
                        xanchor='right',
                        x=1, y=1.09,
                        font=dict(color='#fff')),
            coloraxis_showscale=False,
            paper_bgcolor='#262625',
            plot_bgcolor='#262625',
            height=500,
            transition_duration=500,
            margin=dict(l=10))

        return fig

    @dash_app.callback(Output('state-comp_infection', 'figure'),
                       Output('state-comp_death', 'figure'),
                       Output('global_state-comp_infection', 'figure'),
                       Output('global_state-comp_death', 'figure'),
                       Input('compare-tabs', 'value')
                       )
    def update_compare_graphs(tab):
        running_avg = pd.DataFrame()
        running_avg_glob = pd.DataFrame()

        global asia_stat, world_stat

        if tab == 1:
            indexes = ['location', 'total_cases', 'total_deaths']

            asia_stat = world_data[world_data['continent'] == 'Asia'][indexes].groupby(by='location').max()
            asia_stat = asia_stat * 100 / np.sum(asia_stat)
            asia_stat = asia_stat.sort_values(by=asia_stat.columns[0])
            world_stat = world_data[indexes].groupby(by='location').max()
            world_stat = world_stat.drop(
                ['Asia', 'Africa', 'Europe', 'European Union', 'North America', 'South America', 'World'])
            world_stat = world_stat * 100 / np.sum(world_stat)
            world_stat = world_stat.sort_values(by=world_stat.columns[0])

        elif tab == 2:
            indexes = ['location', 'total_cases_per_million', 'total_deaths_per_million']

            asia_stat = world_data[world_data['continent'] == 'Asia'][indexes].groupby(by='location').max()
            asia_stat = asia_stat * 100 / np.sum(asia_stat)
            asia_stat = asia_stat.sort_values(by=asia_stat.columns[0])
            world_stat = world_data[indexes].groupby(by='location').max()
            world_stat = world_stat.drop(
                ['Asia', 'Africa', 'Europe', 'European Union', 'North America', 'South America', 'World'])
            world_stat = world_stat * 100 / np.sum(world_stat)
            world_stat = world_stat.sort_values(by=world_stat.columns[0])

        elif tab == 3:
            running_avg = pd.DataFrame()
            running_avg_glob = pd.DataFrame()
            indexes = ['location', 'new_cases', 'new_deaths']

            asia_stat = world_data[world_data['continent'] == 'Asia'][indexes].groupby(by='location').ewm(
                span=2).mean().reset_index().drop('level_1', axis=1).set_index('location')

            for u_index in asia_stat.index.unique():
                running_avg = running_avg.append(asia_stat.loc[u_index].tail(1))

            asia_stat = running_avg
            asia_stat.fillna(value=0, inplace=True)

            asia_stat = asia_stat * 100 / np.sum(asia_stat)
            asia_stat = asia_stat.sort_values(by=asia_stat.columns[0])

            world_stat = world_data[indexes].groupby(by='location').ewm(span=2).mean().reset_index().drop('level_1',
                                                                                                          axis=1).set_index(
                'location')

            for u_index in world_stat.index.unique():
                running_avg_glob = running_avg_glob.append(world_stat.loc[u_index].tail(1))

            world_stat = running_avg_glob
            world_stat.fillna(value=0, inplace=True)

            world_stat = world_stat.drop(
                ['Asia', 'Africa', 'Europe', 'European Union', 'North America', 'South America', 'World'])
            world_stat = world_stat * 100 / np.sum(world_stat)
            world_stat = world_stat.sort_values(by=world_stat.columns[0])

        ############################# state competition ##############################
        state_compare_infections = go.Figure()

        for index in asia_stat.index:
            if index == 'Sri Lanka':
                color = '#E5D17F'
                width = 0.35
            else:
                color = '#7A8C7E'
                width = 0.3

            state_compare_infections.add_trace(go.Bar(name=index,
                                                      x=[asia_stat.loc[index, asia_stat.columns[0]]],
                                                      y=[asia_stat.columns[0]],
                                                      orientation='h',
                                                      marker=dict(color=color,
                                                                  ),
                                                      width=width))

        annotation = []

        if tab == 3:
            annotation.append(dict(xref='x', yref='paper',
                                   text=f'Sri Lanka {np.round(running_avg.loc["Sri Lanka", running_avg.columns[0]], 2)}',
                                   x=np.sum(
                                       asia_stat.loc[:'Sri Lanka', asia_stat.columns[0]]),
                                   y=0.65,
                                   font=dict(size=12,
                                             color='#E5D17F'),
                                   arrowcolor='#fff'))
        else:
            annotation.append(dict(xref='x', yref='paper',
                                   text=f'Sri Lanka {np.round(asia_stat.loc["Sri Lanka", asia_stat.columns[0]], 2)}%',
                                   x=np.sum(
                                       asia_stat.loc[:'Sri Lanka', asia_stat.columns[0]]),
                                   y=0.65,
                                   font=dict(size=12,
                                             color='#E5D17F'),
                                   arrowcolor='#fff'))

        state_compare_infections.update_layout(barmode='stack',
                                               title=dict(text='Infections in Asia and the Middle East',
                                                          font=dict(color='#fff'),
                                                          xanchor='left',
                                                          x=0.01,
                                                          yanchor='bottom',
                                                          y=0.8),
                                               xaxis=dict(visible=False,
                                                          showgrid=False,
                                                          showline=False,
                                                          color='white',
                                                          zeroline=False),
                                               yaxis=dict(visible=False,
                                                          gridcolor='#404040',
                                                          showgrid=False,
                                                          showline=False,
                                                          color='white'),
                                               annotations=annotation,
                                               showlegend=False,
                                               paper_bgcolor='#262625',
                                               plot_bgcolor='#262625',
                                               height=265,
                                               margin=dict(l=10, r=0, t=10, b=0),
                                               transition_duration=500)

        ############################# compare deaths #################################
        state_compare_deaths = go.Figure()
        asia_stat = asia_stat.sort_values(by=asia_stat.columns[1])

        for index in asia_stat.index:
            if index == 'Sri Lanka':
                color = '#E5D17F'
                width = 0.35
            else:
                color = '#7A8C7E'
                width = 0.3

            state_compare_deaths.add_trace(go.Bar(name=index,
                                                  x=[asia_stat.loc[index, asia_stat.columns[1]]],
                                                  y=[asia_stat.columns[1]],
                                                  orientation='h',
                                                  marker=dict(color=color),
                                                  width=width))

        annotation = []

        if tab == 3:
            annotation.append(dict(xref='x', yref='paper',
                                   text=f'Sri Lanka {np.round(running_avg.loc["Sri Lanka", running_avg.columns[1]], 2)}',
                                   x=np.sum(
                                       asia_stat.loc[:'Sri Lanka', asia_stat.columns[1]]),
                                   y=0.65,
                                   font=dict(size=12,
                                             color='#E5D17F'),
                                   arrowcolor='#fff'))
        else:
            annotation.append(dict(xref='x', yref='paper',
                                   text=f'Sri Lanka {np.round(asia_stat.loc["Sri Lanka", asia_stat.columns[1]], 2)}%',
                                   x=np.sum(
                                       asia_stat.loc[:'Sri Lanka', asia_stat.columns[1]]),
                                   y=0.65,
                                   font=dict(size=12,
                                             color='#E5D17F'),
                                   arrowcolor='#fff'))

        state_compare_deaths.update_layout(barmode='stack',
                                           title=dict(text='Deaths in Asia and the Middle East',
                                                      font=dict(color='#fff'),
                                                      xanchor='left',
                                                      x=0.01,
                                                      yanchor='bottom',
                                                      y=0.8),
                                           xaxis=dict(visible=False,
                                                      showgrid=False,
                                                      showline=False,
                                                      color='white',
                                                      zeroline=False),
                                           yaxis=dict(visible=False,
                                                      gridcolor='#404040',
                                                      showgrid=False,
                                                      showline=False,
                                                      color='white'),
                                           annotations=annotation,
                                           showlegend=False,
                                           paper_bgcolor='#262625',
                                           plot_bgcolor='#262625',
                                           height=265,
                                           margin=dict(l=10, r=0, t=10, b=0),
                                           transition_duration=500)

        ############################ Infections, globally ############################
        glob_state_compare_infections = go.Figure()

        for index in world_stat.index:
            if index == 'Sri Lanka':
                color = '#E5D17F'
                width = 0.35
            else:
                color = '#7A8C7E'
                width = 0.3

            glob_state_compare_infections.add_trace(go.Bar(name=index,
                                                           x=[world_stat.loc[index, world_stat.columns[0]]],
                                                           y=[world_stat.columns[0]],
                                                           orientation='h',
                                                           marker=dict(color=color,
                                                                       ),
                                                           width=width))

        annotation = []

        if tab == 3:
            annotation.append(dict(xref='x', yref='paper',
                                   text=f'Sri Lanka {np.round(running_avg_glob.loc["Sri Lanka", running_avg_glob.columns[0]], 2)}',
                                   x=np.sum(
                                       world_stat.loc[:'Sri Lanka', world_stat.columns[0]]),
                                   y=0.65,
                                   font=dict(size=12,
                                             color='#E5D17F'),
                                   arrowcolor='#fff'))
        else:
            annotation.append(dict(xref='x', yref='paper',
                                   text=f'Sri Lanka {np.round(world_stat.loc["Sri Lanka", world_stat.columns[0]], 2)}%',
                                   x=np.sum(
                                       world_stat.loc[:'Sri Lanka', world_stat.columns[0]]),
                                   y=0.65,
                                   font=dict(size=12,
                                             color='#E5D17F'),
                                   arrowcolor='#fff'))

        glob_state_compare_infections.update_layout(barmode='stack',
                                                    title=dict(text='Infections, globally',
                                                               font=dict(color='#fff'),
                                                               xanchor='left',
                                                               x=0.01,
                                                               yanchor='bottom',
                                                               y=0.8),
                                                    xaxis=dict(visible=False,
                                                               showgrid=False,
                                                               showline=False,
                                                               color='white',
                                                               zeroline=False),
                                                    yaxis=dict(visible=False,
                                                               gridcolor='#404040',
                                                               showgrid=False,
                                                               showline=False,
                                                               color='white'),
                                                    annotations=annotation,
                                                    showlegend=False,
                                                    paper_bgcolor='#262625',
                                                    plot_bgcolor='#262625',
                                                    height=265,
                                                    margin=dict(l=10, r=0, t=10, b=0),
                                                    transition_duration=500)

        ############################# Deaths, globally ###############################
        glob_state_compare_deaths = go.Figure()
        world_stat = world_stat.sort_values(by=world_stat.columns[1])

        for index in world_stat.index:
            if index == 'Sri Lanka':
                color = '#E5D17F'
                width = 0.35
            else:
                color = '#7A8C7E'
                width = 0.3

            glob_state_compare_deaths.add_trace(go.Bar(name=index,
                                                       x=[world_stat.loc[index, world_stat.columns[1]]],
                                                       y=[world_stat.columns[1]],
                                                       orientation='h',
                                                       marker=dict(color=color,
                                                                   ),
                                                       width=width))

        annotation = []

        if tab == 3:
            annotation.append(dict(xref='x', yref='paper',
                                   text=f'Sri Lanka {np.round(running_avg_glob.loc["Sri Lanka", running_avg_glob.columns[1]], 2)}',
                                   x=np.sum(
                                       world_stat.loc[:'Sri Lanka', world_stat.columns[1]]),
                                   y=0.65,
                                   font=dict(size=12,
                                             color='#E5D17F'),
                                   arrowcolor='#fff'))
        else:
            annotation.append(dict(xref='x', yref='paper',
                                   text=f'Sri Lanka {np.round(world_stat.loc["Sri Lanka", world_stat.columns[1]], 2)}%',
                                   x=np.sum(
                                       world_stat.loc[:'Sri Lanka', world_stat.columns[1]]),
                                   y=0.65,
                                   font=dict(size=12,
                                             color='#E5D17F'),
                                   arrowcolor='#fff'))

        glob_state_compare_deaths.update_layout(barmode='stack',
                                                title=dict(text='Deaths, globally',
                                                           font=dict(color='#fff'),
                                                           xanchor='left',
                                                           x=0.01,
                                                           yanchor='bottom',
                                                           y=0.8),
                                                xaxis=dict(visible=False,
                                                           showgrid=False,
                                                           showline=False,
                                                           color='white',
                                                           zeroline=False),
                                                yaxis=dict(visible=False,
                                                           gridcolor='#404040',
                                                           showgrid=False,
                                                           showline=False,
                                                           color='white'),
                                                annotations=annotation,
                                                showlegend=False,
                                                paper_bgcolor='#262625',
                                                plot_bgcolor='#262625',
                                                height=265,
                                                margin=dict(l=10, r=0, t=10, b=0),
                                                transition_duration=500)

        return state_compare_infections, state_compare_deaths, glob_state_compare_infections, glob_state_compare_deaths
