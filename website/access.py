#
# access.py
#
# control logins and access to the windermere website
#


from flask.ext.login import LoginManager
from website import app
from models import User
login_manager = LoginManager(app)


login_manager.login_view = 'endpoints.login'
login_manager.login_message = 'Access to this page is restricted.'


@login_manager.token_loader
def load_user(token):
    return User.query.filter_by(auth_token=token).first()

@login_manager.user_loader
def load_user(userid):
    int_uid = int(userid)
    return User.query.filter_by(id=int_uid).first()
