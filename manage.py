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


@manager.command
def load_oldphotos(datafile='import-old/data.json'):
    import json
    from datetime import datetime
    from website.models import db, ScenicPhoto

    with open(datafile) as f:
        data = json.load(f)

    for photo_data in data['photos']:
        photo = ScenicPhoto()
        photo.photo = photo_data['filepath']
        photo.title = photo_data['title']
        photo.description = photo_data['body']
        photo.added = datetime.utcfromtimestamp(photo_data['timestamp'])
        photo.featured = False
        db.session.add(photo)

    db.session.commit()


@manager.command
def load_olddocs(datafile='import-old/data.json'):
    import json
    from datetime import datetime
    from website.models import db, Document, DocCategory

    with open(datafile) as f:
        data = json.load(f)

    def nice_to_safe(name):
        return name.replace('/ ', '').lower().replace(' ', '-')

    for doc_data in data['documents']:
        doc = Document()
        doc.file = doc_data['path']
        doc.title = doc_data['title']
        doc.description = doc_data['body']
        doc.added = datetime.utcfromtimestamp(doc_data['timestamp'])
        doc.type = doc_data['type']
        doc.authors = doc_data['author']
        for category in doc_data['categories']:
            cat = DocCategory()
            cat.name = category
            cat.safe = nice_to_safe(category)
            cat.document = doc
            db.session.add(cat)
        db.session.add(doc)

    db.session.commit()


@manager.command
def seed_key():
    from website.models import db, Partner
    from datetime import datetime
    partner = Partner()
    partner.name = 'Consortium Partner'
    partner.key = app.config['ACCESS_SEED']
    partner.last_keychange = datetime.now()
    db.session.add(partner)
    db.session.commit()


@manager.command
def mkphil():
    from website import models
    phil = models.Admin()
    phil.name = 'Phil Schleihauf'
    phil.username = 'phil'
    phil.set_password('asdf')
    models.db.session.add(phil)
    models.db.session.commit()


if __name__ == '__main__':
    manager.run()
