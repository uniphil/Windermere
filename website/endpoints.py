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
    photos = models.ScenicPhoto.query.order_by(models.ScenicPhoto.added.desc()).all()
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


Filter = namedtuple('Filter', 'name plural safe')
all_type_filters = (
    Filter('Presentation', 'Presentations', 'presentation'),
    Filter('Publication', 'Publications', 'publication'),
    Filter('Abstract', 'Abstracts', 'abstract'),
    Filter('Thesis', 'Theses', 'thesis'),
    Filter('High-Resolution Image', 'High-Resolution Images', 'high-resolution-image'),
)

category_tree = {
    'slope': {
        'channels': {
            'large-channels': None,
            'small-channels': None,
        },
        'levees-and-splays': None,
        'mass-transport-deposits': None,
    },
    'channel-lobe-transition-zone': None,
    'basin-floor-lobes': {
        'isolated-scour': None,
        'avulsion-spray': None,
        'feeder-channel': None,
        'distributary-channel': None,
        'terminal-splay': None,
    },
    'old-fort-point': None,
    'experimental': None,
    'miscellaneous': None,
    'current-events': None,
}
category_names = {
    ('slope',): 'Slope',
    ('slope', 'channels'): 'Channels',
    ('slope', 'channels', 'large-channels'): 'Large Channels',
    ('slope', 'channels', 'small-channels'): 'Small Channels',
    ('slope', 'levees-and-splays'): 'Levees and Splays',
    ('slope', 'mass-transport-deposits'): 'Mass Transport Deposits',
    ('channel-lobe-transition-zone',): 'Channel-Lobe Transition Zone',
    ('basin-floor-lobes',): 'Basin Floor Lobes',
    ('basin-floor-lobes', 'isolated-scour'): 'Isolated Scour',
    ('basin-floor-lobes', 'avulsion-spray'): 'Avulsion Splay',
    ('basin-floor-lobes', 'feeder-channel'): 'Feeder Channel',
    ('basin-floor-lobes', 'distributary-channel'): 'Distributary Channel',
    ('basin-floor-lobes', 'terminal-splay'): 'Terminal Splay',
    ('old-fort-point',): 'Old Fort Point',
    ('experimental',): 'Experimental',
    ('miscellaneous',): 'Miscellaneous',
    ('current-events',): 'Current Events',
}


def subtree_to_subcategories(tree):
    if tree is None:
        yield []
    else:
        for name, subtree in tree.items():
            if subtree is not None:
                for subcat in subtree_to_subcategories(subtree):
                    yield [name] + subcat
            else:
                yield [name]


def get_categories_from_parts(node_path):
    """[slope, channels] => [slope-channels-large, slope-channels-small]"""
    categories = []
    subtree = category_tree

    for node in node_path:
        # build up the root and trim the tree to the smallest subtree
        subtree = subtree[node]

    for subcategory in subtree_to_subcategories(subtree):
        category = '-'.join(node_path + subcategory)
        categories.append(category)

    return categories


@app.route('/content/')
@app.route('/content/<path:category>/')
@login_required
def topic_overview(category=None):

    title = 'Content Browser'
    page_name = 'Overview'
    grouped_documents = []

    base_query = models.Document.query.order_by(models.Document.added.asc())
    query = base_query

    if category is not None:
        selected_category_parts = category.split('/')
        categories = get_categories_from_parts(selected_category_parts)
        query = query.filter(models.db.or_(
            *(models.Document.categories.any(safe=c) for c in categories)
        ))
    else:
        selected_category_parts = []


    active_type_filter = request.args.get('filter')

    for type_filter in all_type_filters:
        documents_of_type = query.\
            filter(models.Document.type_id==models.Type.id).\
            filter(models.Type.safe==type_filter.safe)
        if active_type_filter is None:
            docs = documents_of_type.limit(3)
        elif type_filter.safe == active_type_filter:
            docs = documents_of_type.all()
            page_name = type_filter.plural
        else:
            docs = None
        docs_in_category = documents_of_type.count()
        grouped_documents.append([type_filter, docs, docs_in_category])


    return render_template('content-browser.html',
        title=title,
        page_name=page_name,
        grouped_documents=grouped_documents,
        filtered=active_type_filter is not None,
        category_tree=category_tree,
        category_names=category_names,
        selected_category_parts=selected_category_parts,
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


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/error.html', error=error)
