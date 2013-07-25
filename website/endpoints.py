#
# endpoints.py
# 

from flask import render_template
from . import app


@app.route('/')
def home():
    return "hellooooooooo"


@app.route('/overview-sample')
def mock_overview():
    class Content(list):
        def __init__(self, name, stuff=[]):
            self.name = name
            super(Content, self).__init__(stuff)

    contents = [
        Content("Photos", ["lalalal", "lololo", "lelele"]),
        Content("Publications", ["one", "two", "threeeee"]),
        Content("Theses", ["un,", "deux", "troisiemme"]),
        Content("Presentations", ["blah", "blah", "bleh"]),
    ]
            
    return render_template('mock-overview.html', contents=contents)
        