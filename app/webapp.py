import flask
from flask import Blueprint
from flask import render_template

app_blueprint = Blueprint('main', __name__)


@app_blueprint.route('/')
def main():
    return render_template('index.html', title='COVID-19 Tracker')
