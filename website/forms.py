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
