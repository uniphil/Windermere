"""
    website.endpoints
    ~~~~~~~~~~~~~~~~~
"""

import os
import random
from collections import namedtuple
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


Filter = namedtuple('Filter', 'name plural active')
filters = (
    Filter('Presentation', 'Presentations', False),
    Filter('Publication', 'Publications', False),
    Filter('Abstract', 'Abstracts', False),
    Filter('Thesis', 'Theses', False),
    Filter('High-Resolution Image', 'High-Resolution Images', False),
)

Category = namedtuple('Category', 'name safe')
categories = (
  
)



@app.route('/content/')
@app.route('/content/<string:category>/')
#@login_required
def topic_overview(category=None):

    filter = request.args.get('filter', None)

    sel_filters = []
    for f in filters:
        if f.name == filter:
            f = Filter(f.name, f.plural, True)
        sel_filters.append(f)

    data = []
    base_q = models.Document.query.order_by(models.Document.added.asc())
    if category:
        base_q = base_q.filter(models.db.and_(
            models.DocCategory.safe == category,
            models.DocCategory.document_id == models.Document.id,
        ))

    print base_q

    for f in sel_filters:
        q = base_q.filter_by(type=f.name)
        if f.name == filter:
            recs = q.all()
        elif filter == None:
            recs = q.limit(3)
        else:
            recs = None
        count = q.count()
        data.append((f, recs, count))

    return render_template('content-overview.html',
        title='Content Browser',
        category=category,
        data=data,
        filtered=filter is not None,
    )


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
