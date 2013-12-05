"""
    website.forms
    ~~~~~~~~~~~~~

    user input models for the windermere website
"""

from flask.ext.wtf import Form
from wtforms import fields, validators
from wtforms.validators import DataRequired
from website import app


class PartnerForm(Form):
    key = fields.TextField('Key', validators=[DataRequired()])


class AdminForm(Form):
    name = fields.TextField('Name', [validators.Length(min=2, max=80)])
    username = fields.TextField('Username', [validators.Length(min=2, max=80)])
    password = fields.PasswordField('Password', [validators.DataRequired()])


class LoginForm(Form):
    username = fields.TextField('Username', [validators.DataRequired()])
    password = fields.PasswordField('Password', [validators.DataRequired()])


class ScenicPhotoForm(Form):
    photo = fields.FileField('Photo')
    title = fields.TextField('Title', [validators.DataRequired()])
    featured = fields.BooleanField('Homepage Cover Photo')
    description = fields.TextAreaField('Description')


class ScenicPhotoEditForm(Form):
    title = fields.TextField('Title', [validators.DataRequired()])
    featured = fields.BooleanField('Homepage Cover Photo')
    description = fields.TextAreaField('Description')
