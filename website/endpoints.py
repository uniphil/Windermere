"""
    website.endpoints
    ~~~~~~~~~~~~~~~~~
"""

import os
import random
from flask import (request, session, render_template, redirect, url_for, flash,
                   send_from_directory, send_file, abort)
from flask.helpers import safe_join
from flask.ext.login import (current_user, login_required, login_user,
                             logout_user)
from . import app, models, forms


@app.route('/')
def home():
    form = forms.PartnerForm(request.form)
    feature_query = models.ScenicPhoto.query.filter_by(featured=True)
    try:
        featurenum = random.randrange(0, feature_query.count())
        featurefile = url_for('photo', filename=feature_query[featurenum].photo + '_sized.jpg')
    except ValueError:
        featurefile = ''
    return render_template('home.html', form=form, bg=featurefile)


@app.route('/people')
def people():
    return render_template('people.html')


@app.route('/unlock', methods=['GET', 'POST'])
def unlock():
    form = forms.PartnerForm(request.form)
    if form.validate_on_submit():
        partner = models.Partner.query.filter_by(key=form.key.data).first()
        if partner is not None:
            if partner.is_active():
                login_user(partner)
                flash('Restricted access unlocked for {}'.format(partner.name),
                      'success')
                return redirect(request.args.get('next') or url_for('topic_overview', coarse="asdf"))
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


@app.route('/content/<string:coarse>/')
@app.route('/content/<string:coarse>/<string:medium>/')
@app.route('/content/<string:coarse>/<string:medium>/<string:fine>/')
#@login_required
def topic_overview(coarse, medium=None, fine=None):
    return render_template('content-overview.html', title='Content Browser',
                           coarse=coarse, medium=medium, fine=fine)


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


@app.route('/photo/<filename>')
def photo(filename):
    filepath = app.config['scenic'](filename)
    return send_file(filepath)


@app.route('/files/<path:filename>')
def files(filename):
    print('yo', filename)
    filepath = safe_join(app.config['UPLOAD_FOLDER'], filename)
    print('yo2', filepath)
    if not os.path.isabs(filepath):
        filepath = os.path.join(app.root_path, filepath)
    print('yo3', filepath)
    # if not os.path.isfile(filepath):
    #     raise abort(404)
    print('yo4', filepath)
    return send_file(filepath)


@app.errorhandler(404)
def not_found(error):
    err_dir = os.path.join(app.root_path, 'static', 'errors')
    return send_from_directory(err_dir, 'not-found.html'), 404
