from flask import render_template
from . import app


@app.route('/')
def home():
    return "hellooooooooo"


@app.route('/overview-sample')
def mock_overview():
    return render_template('mock-overview.html')
