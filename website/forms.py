#
# forms.py
#
# user input models for the windermere website
#

from flask.ext.wtf import Form
from wtforms import fields, validators
from wtforms.fields import TextField, PasswordField
from wtforms.validators import DataRequired
from website import app


class PartnerForm(Form):
    key = TextField('Key', validators=[DataRequired()])


class AdminForm(Form):
    name = fields.TextField('Name', validators=[
        validators.Length(min=2, max=80),
    ])
    username = fields.TextField('Username', validators=[
        validators.Length(min=2, max=80),
    ])
    password = fields.PasswordField('Password', validators=[
        validators.DataRequired(),
    ])


class LoginForm(Form):
    username = fields.TextField('Username', validators=[
        validators.DataRequired(),
    ])
    password = fields.PasswordField('Password', validators=[
        validators.DataRequired(),
    ])


class ScenicPhotoForm(Form):
    """
    copied from the model:
    id = db.Column(db.Integer, primary_key=True)
    photo_full = db.Column(db.String(220))
    phtoo_sized = db.Column(db.String(220))
    photo_thumb = db.Column(db.String(220))
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    date = db.Column(db.DateTime)
    featured = db.Column(db.Boolean)
    """
    title = fields.TextField('Title', validators=[
        validators.DataRequired(),
    ])
    description = fields.TextField('Description')
