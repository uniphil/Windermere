"""
    website.models
    ~~~~~~~~~~~~~~

    Database models for content on the Windermere Consortium website
"""

from math import ceil
from os import urandom
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
    username = db.Column(db.String(80), unique=True)
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
        return '<Admin {}>'.format(self.username)


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    photo_full = db.Column(db.String(220))
    phtoo_sized = db.Column(db.String(220))
    photo_thumb = db.Column(db.String(220))
    bio = db.Column(db.Text)
    href = db.Column(db.String(120))
    contact = db.Column(db.Text)
    current = db.Column(db.Boolean)


class ScenicPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo_full = db.Column(db.String(220))
    photo_sized = db.Column(db.String(220))
    photo_thumb = db.Column(db.String(220))
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    added = db.Column(db.DateTime)
    featured = db.Column(db.Boolean)


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file = db.Column(db.String(220))


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
