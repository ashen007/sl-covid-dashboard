import dash


def init_dashboard(server):
    dash_app = dash.Dash(server=server,
                         name='',
                         url_base_pathname='/local/')

    return dash_app