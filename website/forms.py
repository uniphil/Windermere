#
# forms.py
#
# user input models for the windermere website
#

from flask.ext.wtf import Form
from wtforms.fields import TextField, PasswordField
from wtforms.validators import DataRequired
from website import app


class PartnerForm(Form):
    key = TextField('Key', validators=[DataRequired()])


class AdminForm(Form):
    username = TextField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
