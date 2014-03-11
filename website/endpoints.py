"""
    website.endpoints
    ~~~~~~~~~~~~~~~~~
"""

import os
import random
from collections import namedtuple
from werkzeug.exceptions import NotFound
from flask import (request, session, render_template, redirect, url_for, flash,
                   send_from_directory, send_file, abort, jsonify)
from flask.helpers import safe_join
from flask.ext.login import (current_user, login_required, login_user,
                             logout_user)
from flask.ext.mail import Mail, Message
from . import app, models, forms, photo_utils


mail = Mail()
mail.init_app(app)  # eventually move to website.create_app


@app.route('/', methods=['GET', 'POST'])
def home():
    form = forms.ContactForm(request.form)
    people = models.Person.query.order_by(models.Person.current).all()
    message_sent = False
    if form.validate_on_submit():
        message = Message("[No Reply] Windere Contact Form Message",
                          sender='contact-form@windermere.uottawa.ca')
        content = 'from: {}\nmessage:\n{}'.format(form.sender.data,
                                                 form.message.data)
        message.body = content
        for recpi in models.Admin.query.filter_by(receives_messages=True):
            message.add_recipient(recpi.email)
        try:
            mail.send(message)
        except AssertionError:
            return "Email configuration problem (no recipients), sorry :(", 500
        message_sent = True
    feature_query = models.ScenicPhoto.query.filter_by(featured=True)
    try:
        featurenum = random.randrange(0, feature_query.count())
        featureobj = feature_query[featurenum]
        featurefile = url_for('photo', type='scenic', size=1140, filename=featureobj.photo)
        featuredesc = featureobj.title
    except ValueError:
        featuredesc = featurefile = ''
    return render_template('home.html', form=form, message_sent=message_sent,
                           bg=featurefile, banner_photo_title=featuredesc,
                           people=people)


@app.route('/random-feature-photo')
def random_feature_photo():
    feature_query = models.ScenicPhoto.query.filter_by(featured=True)
    random_index = random.randrange(0, feature_query.count())
    photo = feature_query[random_index]
    return jsonify({ 'photo': url_for('photo', type='scenic', filename=photo.photo),
                     'title': photo.title })


@app.route('/photos')
def photo_gallery():
    photos = models.ScenicPhoto.query.all()
    return render_template('photo-gallery.html', photos=photos)


@app.route('/people')
def people():
    query = models.Person.query
    current_count = query.filter_by(current=True).count()
    alum_count = query.filter_by(current=False).count()
    people_filter = request.args.get('filter')
    if people_filter is not None and people_filter in ('current', 'alum'):
        current = True if people_filter == 'current' else False
        query = query.filter_by(current=current)
    people = query.all()
    return render_template('people.html', people=people, alum_count=alum_count,
                           current_count=current_count, filter=people_filter)


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
@login_required
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
@login_required
def document(id):
    document = models.Document.query.get(id) or abort(404)
    return render_template('content-detail.html', doc=document)


@app.route('/photo/<type>/<path:filename>')
def photo(type, filename):
    photosize = request.args.get('size')
    sub_path = os.path.join(type, filename)
    filepath = safe_join(app.config['UPLOAD_FOLDER'], sub_path)
    if not os.path.isabs(filepath):
        filepath = os.path.join(app.root_path, filepath)
    if not os.path.isfile(filepath):
        raise NotFound()
    if photosize is not None:
        photosize = int(photosize)
        filepath = photo_utils.scaled_cached(filepath, photosize)
    return send_file(filepath)


@app.route('/data/<path:filepath>')
@login_required
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
    return render_template('errors/not-found.html'), 404
