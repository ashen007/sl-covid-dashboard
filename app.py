from flask import Flask
from dashboards.local import init_dashboard

app = Flask(__name__)
init_dashboard(app)


@app.route('/')
def main():
    return


if __name__ == '__main__':
    app.run()
