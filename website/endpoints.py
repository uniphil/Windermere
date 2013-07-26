#
# endpoints.py
# 

from flask import session, render_template, redirect, url_for
from flask.ext.login import (current_user, login_required, login_user,
                             logout_user)
from . import app


@app.route('/')
def home():
    return "hellooooooooo"


@app.route('/login')
def login():
    session.clear()
    from models import User
    phil = User.query.get(1)
    login_user(phil)
    return redirect(url_for('home'))
    # return "you need ta login na"

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
