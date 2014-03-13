"""
    website.models
    ~~~~~~~~~~~~~~

    Database models for content on the Windermere Consortium website
"""

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


class Type(db.Model):
    __tablename__ = 'document_types'

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
