"""
    website.models
    ~~~~~~~~~~~~~~

    Database models for content on the Windermere Consortium website
"""

from collections import namedtuple
from math import ceil
from PIL import Image
from os import urandom, path
from base64 import urlsafe_b64encode as b64encode
from passlib.hash import pbkdf2_sha256
from flask.ext.login import UserMixin
from flask.ext.sqlalchemy import SQLAlchemy
from website import app


db = SQLAlchemy(app)


class Partner(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(24), unique=True)
    name = db.Column(db.String(80), unique=True)
    last_active = db.Column(db.DateTime)
    last_keychange = db.Column(db.DateTime)
    is_admin = False

    def get_id(self):
        return self.key


class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    # username not email in the db because sqlalchemy migrations suck
    email = db.Column('username', db.String(80), unique=True)
    receives_messages = db.Column(db.Boolean)
    password_hash = db.Column(db.String(87))
    disabled = db.Column(db.Boolean())
    last_active = db.Column(db.DateTime)
    is_admin = True

    def __init__(self, *args, **kwargs):
        super(Admin, self).__init__(*args, **kwargs)
        self.disabled = False

    def set_password(self, plain_password):
        self.password_hash = pbkdf2_sha256.encrypt(plain_password)

    def check_password(self, plain_password):
        return pbkdf2_sha256.verify(plain_password, self.password_hash)

    def is_active(self):
        return False if self.disabled else True

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<Admin {}>'.format(self.email)


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    photo = db.Column(db.String(220))
    bio = db.Column(db.Text)
    href = db.Column(db.String(120))
    contact = db.Column(db.Text)
    current = db.Column(db.Boolean)


class ScenicPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.String(220))
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    added = db.Column(db.DateTime)
    featured = db.Column(db.Boolean)


document_categories = db.Table('document_categories', db.Model.metadata,
    db.Column('document_id', db.Integer, db.ForeignKey('documents.id')),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'))
)


def safeify(name):
    return name.replace('/ ', '').lower().replace(' ', '-')


Filter = namedtuple('Filter', 'name plural safe')

class Type(db.Model):
    __tablename__ = 'document_types'

    all_filters = (
        Filter('Presentation', 'Presentations', 'presentation'),
        Filter('Publication', 'Publications', 'publication'),
        Filter('Abstract', 'Abstracts', 'abstract'),
        Filter('Thesis', 'Theses', 'thesis'),
        Filter('High-Resolution Image', 'High-Resolution Images', 'high-resolution-image'),
    )

    id = db.Column(db.Integer, primary_key=True)
    safe = db.Column(db.String(128), unique=True)
    name = db.Column(db.String(128))

    def __init__(self, name):
        self.name = name
        self.safe = safeify(name)

    def __repr__(self):
        return '<Type of document: {}>'.format(self.safe)

    def __str__(self):
        return self.name


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    safe = db.Column(db.String(128), unique=True)
    name = db.Column(db.String(128))

    def __init__(self, name):
        self.name = name
        self.safe = safeify(name)

    def __repr__(self):
        return '<Category: {}>'.format(self.safe)

    def __str__(self):
        return self.name

    tree = {
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
    names = {
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

    @staticmethod
    def list_from_subtree(tree):
        if tree is None:
            yield []
        else:
            for name, subtree in tree.items():
                if subtree is not None:
                    for subcat in Category.list_from_subtree(subtree):
                        yield [name] + subcat
                else:
                    yield [name]

    @staticmethod
    def list_from_parts(node_path):
        """[slope, channels] => [slope-channels-large, slope-channels-small]"""
        categories = []
        subtree = Category.tree
        for node in node_path:
            # build up the root and trim the tree to the smallest subtree
            subtree = subtree[node]
        for subcategory in Category.list_from_subtree(subtree):
            category = '-'.join(node_path + subcategory)
            categories.append(category)
        return categories


class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    file = db.Column(db.String(220))
    title = db.Column(db.String(128))
    description = db.Column(db.Text)
    added = db.Column(db.DateTime)
    authors = db.Column(db.String(128))
    type_id = db.Column(db.Integer, db.ForeignKey('document_types.id'))

    type = db.relationship('Type', backref=db.backref('documents'))
    categories = db.relationship('Category', secondary=document_categories,
                                 backref='documents')

    def __repr__(self):
        return '<Document: {}...>'.format(self.title[:21])

    @property
    def filename(self):
        return path.split(self.file)[-1]


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
