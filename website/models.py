#
# models.py
#
# Database models for content on the Windermere Consortium website
#

from passlib.hash import pbkdf2_sha256
from flask.ext.login import UserMixin, make_secure_token
from flask.ext.sqlalchemy import SQLAlchemy
from website import app
db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password_hash = db.Column(db.String(87))
    auth_token = db.Column(db.String(40))
    disabled = db.Column(db.Boolean())

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.disabled = False

    def set_password(self, plain_password):
        self.password_hash = pbkdf2_sha256.encrypt(plain_password)
        self.auth_token = make_secure_token(str(self.id), self.password_hash)

    def check_password(self, plain_password):
        return pbkdf2_sha256.verify(plain_password, self.password_hash)

    def get_auth_token(self):
        return self.auth_token

    def is_active(self):
        return False if self.disabled else True

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file = 'lalala'


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
