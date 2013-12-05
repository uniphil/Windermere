"""
    website.access
    ~~~~~~~~~~~~~~

    control logins and access to the windermere website
"""

from datetime import datetime
from flask.ext.login import LoginManager, AnonymousUserMixin
from website import app
from models import db, Partner, Admin
login_manager = LoginManager(app)

login_manager.login_view = 'unlock'
login_manager.login_message = 'Access to this page is restricted.'
login_manager.login_message_category = 'info'


AnonymousUserMixin.is_admin = False


@login_manager.user_loader
def load_user(userid):
    # try to load a partner...
    partner = Partner.query.filter_by(key=userid).first()
    if partner is not None:
        partner.last_active = datetime.now()
        db.session.add(partner)
        db.session.commit()
        return partner
    else:
        try:
            int_uid = int(userid)
        except ValueError:
            return None
        the_admin = Admin.query.filter_by(id=int_uid).first()
        if the_admin is None:
            return None
        the_admin.last_active = datetime.now()
        db.session.add(the_admin)
        db.session.commit()
        return the_admin
