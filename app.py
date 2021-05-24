import flask
from flask import Flask
from dashboards.local import init_dashboard
from dashboards.overall import init_index_page

app = Flask(__name__)
init_dashboard(app)


@app.route('/')
def main():
    init_index_page(app)


if __name__ == '__main__':
    app.run()
