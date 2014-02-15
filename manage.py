#!/usr/bin/env python2
"""
    util
    ~~~~

    Some useful tools for working with the windermere site.
"""


from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from website import app
from website.models import db

migrate = Migrate(app, db)


manager = Manager(app)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()


    # elif cmd in ['initdb', 'reinitdb']:
    #     from website.models import db, Partner
    #     from datetime import datetime
    #     if cmd == 'reinitdb':
    #         print 'dropping db'
    #         db.drop_all()
    #     print 'creating db'
    #     db.create_all()
    #     print 'seeding'
    #     partner = Partner()
    #     partner.name = 'Consortium Partner'
    #     partner.key = app.config['ACCESS_SEED']
    #     partner.last_keychange = datetime.now()
    #     db.session.add(partner)
    #     db.session.commit()


    # elif cmd == 'mkphil':
    #     from website import models
    #     phil = models.Admin()
    #     phil.name = 'Phil Schleihauf'
    #     phil.username = 'phil'
    #     phil.set_password('asdf')
    #     models.db.session.add(phil)
    #     models.db.session.commit()