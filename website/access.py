#
# access.py
#
# control logins and access to the windermere website
#

from flask.ext.login import LoginManager
from website import app
from models import Partner, Admin
login_manager = LoginManager(app)

login_manager.login_view = 'unlock'
login_manager.login_message = 'Access to this page is restricted.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(userid):
    if userid.startswith('k+'):
        return Partner.query.filter_by(key=userid).first()
    else:
        return Admin.query.filter_by(auth_token=userid).first()
