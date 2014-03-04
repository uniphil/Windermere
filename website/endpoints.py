"""
    website.endpoints
    ~~~~~~~~~~~~~~~~~
"""

import os
import random
from collections import namedtuple
from werkzeug.exceptions import NotFound
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

Category = namedtuple('Category', 'name safe selected children')
categories = (
    Category('Slope', 'slope', False, (
        Category('Channels', 'slope-channels', False, (
             Category('Large Channels', 'slope-channels-large-channels', False, None),
             Category('Small Channels', 'slope-channels-small-channels', False, None),
        )),
        Category('Levees and Splays', 'slope-levees-and-splays', False, None),
        Category('Mass Transport Deposits', 'slope-mass-transport-deposits', False, None),
    )),
    Category('Channel Lobe Transition Zone', 'channel-lobe-transition-zone', False, None),
    Category('Basin Floor Lobes', 'basin-floor-lobes', False, (
        Category('Isolated Scour', 'basin-floor-lobes-isolated-scour', False, None),
        Category('Avulsion Spray', 'basin-floor-lobes-avulsion-spray', False, None),  # TOFIX spray -> splay
        Category('Feeder Channel', 'basin-floor-lobes-feeder-channel', False, None),
        Category('Distributary Channel', 'basin-floor-lobes-distributary-channel', False, None),
        Category('Terminal Splay', 'basin-floor-lobes-terminal-splay', False, None),
    )),
    Category('Old Fort Point', 'old-fort-point', False, None),
    Category('Current Events', 'current-events', False, None),
)


@app.route('/content/')
@app.route('/content/<string:category>/')
#@login_required
def topic_overview(category=None):

    cat_name = 'Overview'
    cat_filters = []

    sel_cats = []
    for cat in categories:
        name, safe = cat.name, cat.safe
        scats = None

        if cat.safe == category:
            sel = True
            cat_name = cat.name
        else:
            sel = False

        if cat.children is not None:
            scats = []
            for scat in cat.children:
                sname, ssafe = scat.name, scat.safe
                mcats = None

                if scat.safe == category:
                    sel = ssel = True
                    cat_name = scat.name
                else:
                    ssel = False

                if scat.children is not None:
                    mcats = []
                    for mcat in scat.children:
                        mname, msafe = mcat.name, mcat.safe
                        if mcat.safe == category:
                            sel = ssel = msel = True
                            cat_name = mcat.name
                        else:
                            msel = False
                        if msel and mcat.children is None:
                            cat_filters.append(mcat.safe)

                        mcats.append(Category(mname, msafe, msel, None))

                if ssel and scat.children is None:
                    cat_filters.append(scat.safe)
                scats.append(Category(sname, ssafe, ssel, mcats))

        if sel and cat.children is None:
            cat_filters.append(cat.safe)
        sel_cats.append(Category(name, safe, sel, scats))


    filter = request.args.get('filter', None)

    sel_filters = []
    for f in filters:
        if f.name == filter:
            f = Filter(f.name, f.plural, True)
        sel_filters.append(f)

    data = []
    base_q = models.Document.query \
                .distinct() \
                .order_by(models.Document.added.asc())
    if category:
        base_q = base_q.filter(models.db.and_(
            models.db.or_(
                *(models.DocCategory.safe == c for c in cat_filters)
            ),
            models.DocCategory.document_id == models.Document.id,
        ))

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
        categories=sel_cats,
        cat_name=cat_name,
        list_details=(filter is not None),
    )


@app.route('/content/document/<int:id>')
def document(id):
    document = models.Document.query.get(id) or abort(404)
    return render_template('content-detail.html', doc=document)


@app.route('/photo/<filename>')
def photo(filename):
    filepath = app.config['scenic'](filename)
    return send_file(filepath)


@app.route('/data/<path:filepath>')
def files(filepath):
    folder, filename = filepath.rsplit('/', 1)
    path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
    filepath = safe_join(path, filename)
    if not os.path.isabs(filepath):
        filepath = os.path.join(app.root_path, filepath)
    if not os.path.isfile(filepath):
        raise NotFound()
    return send_file(filepath)


@app.errorhandler(404)
def not_found(error):
    err_dir = os.path.join(app.root_path, 'static', 'errors')
    not_found_resp = send_from_directory(err_dir, 'not-found.html')
    not_found_resp.status_code = 404
    return not_found_resp
