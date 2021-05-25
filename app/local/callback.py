from dash.dependencies import Input
from dash.dependencies import Output
import plotly.graph_objs as go
import pandas as pd

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
