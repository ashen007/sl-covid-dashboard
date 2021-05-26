import dash
from flask.helpers import get_root_path
from flask import Flask


def create_app():
    server = Flask(__name__)

    from app.local.callback import register_callbacks as local_callbacks
    from app.local.layout import layout as local_layouts
    register_dash_app(app=server, title='local', base_pathname='local', layout=local_layouts,
                      register_callback_function=local_callbacks)

    # from region.callback import register_callbacks as overall_callbacks
    # from app.region.layout import layout as overall_layouts
    # register_dash_app(app=server, title='region', base_pathname='region', layout=overall_layouts,register_callback_function=)

    register_blueprints(server)

    return server


def register_dash_app(app, title, base_pathname, layout, register_callback_function):
    meta_viewport = {"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}

    dash_app = dash.Dash(__name__,
                         server=app,
                         url_base_pathname=f'/{base_pathname}/',
                         meta_tags=[meta_viewport],
                         assets_folder=f'{base_pathname}/assets/',
                         )
    with app.app_context():
        dash_app.title = title
        dash_app.layout = layout
        register_callback_function(dash_app)


def register_blueprints(server):
    from app.webapp import app_blueprint

    server.register_blueprint(app_blueprint)
