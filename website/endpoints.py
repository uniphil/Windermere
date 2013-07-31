#
# endpoints.py
# 

from flask import request, session, render_template, redirect, url_for, flash
from flask.ext.login import (current_user, login_required, login_user,
                             logout_user)
from . import app, models, forms


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/unlock', methods=['GET', 'POST'])
def unlock():
    form = forms.PartnerForm(request.form)
    if form.validate_on_submit():
        partner = models.Partner.query.filter_by(key=form.key.data).first()
        if partner is not None:
            if partner.is_active():
                login_user(partner)
                flash('Full access unlocked for {}'.format(partner.name),
                      'success')
                return redirect(request.args.get('next') or url_for('home'))
            else:
                form.key.errors.append('This access key for {} is currently '
                                       'disabled.'.format(partner.name))
        else:
            form.key.errors.append('That key could not be found.')
    return render_template('unlock.html', form=form)


@app.route('/lock')
def lock():
    logout_user()
    return redirect(url_for('home'))


@app.route('/restricted')
@login_required
def restricted():
    return "lalala"


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
