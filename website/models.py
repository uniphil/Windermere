#
# models.py
#
# Database models for content on the Windermere Consortium website
#

from math import ceil
from os import urandom
from base64 import urlsafe_b64encode as b64encode
from passlib.hash import pbkdf2_sha256
from flask.ext.login import UserMixin
from flask.ext.sqlalchemy import SQLAlchemy
from website import app
db = SQLAlchemy(app)


def keygen(chars):
    """Get a string of random safe characters"""
    num_bytes = int(ceil(chars * 3.0 / 4))
    key = b64encode(urandom(num_bytes))
    return key[:chars]


class Partner(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(24), unique=True)
    name = db.Column(db.String(80), unique=True)
    disabled = db.Column(db.Boolean())

    def __init__(self):
        # self.name = name
        self.new_key()
        self.disabled = False

    def new_key(self):
        self.key = 'k+' + keygen(18)

    def get_id(self):
        return self.key

    def is_active(self):
        return False if self.disabled else True


class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password_hash = db.Column(db.String(87))
    disabled = db.Column(db.Boolean())

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


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file = 'lalala'


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
