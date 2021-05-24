import dash


def init_index_page(server):
    dash_app = dash.Dash(server=server,
                         name='',
                         url_base_pathname='/')

    return dash_app
