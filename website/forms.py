"""
    website.forms
    ~~~~~~~~~~~~~

    user input models for the windermere website
"""

import re
from flask.ext.wtf import Form
from wtforms import fields, validators
from website import app


class PartnerForm(Form):
    key = fields.TextField('Key', validators=[validators.DataRequired()])


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

    def validate_photo(form, field):
        if field.data:
            field.data = re.sub(r'[^\w\.\-]', '_', field.data)


class PersonForm(Form):
    name = fields.TextField('Name')
    current = fields.BooleanField('Current?')
    photo = fields.FileField('Photo')
    bio = fields.TextAreaField('Bio')
    link = fields.TextField('Link', [validators.URL()])
    contact = fields.TextField('Contact')

    def validate_photo(form, field):
        if field.data:
            field.data.filename = re.sub(r'[^\w\.\-]', '_', field.data.filename)


class ScenicPhotoEditForm(Form):
    title = fields.TextField('Title', [validators.DataRequired()])
    featured = fields.BooleanField('Homepage Cover Photo')
    description = fields.TextAreaField('Description')
