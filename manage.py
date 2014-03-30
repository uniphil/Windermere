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
def clear_nonscenic():
    from website.models import db, ScenicPhoto
    for photo in ScenicPhoto.query.all():
        if 'Sedimentary Structures' in photo.photo:
            db.session.delete(photo)
    db.session.commit()


@manager.command
def load_olddocs(datafile='import-old/data.json'):
    import json
    from datetime import datetime
    from website.models import db, Document, Type, Category

    with open(datafile) as f:
        data = json.load(f)

    for doc_data in data['documents']:
        doc = Document()
        doc.file = doc_data['path']
        doc.title = doc_data['title']
        doc.description = doc_data['body']
        doc.published = datetime.utcfromtimestamp(doc_data['timestamp'])
        doc.authors = doc_data['author']
        type_name = doc_data['type']
        type = Type.query.filter_by(name=type_name).first()
        if type is None and type_name is not None:
            type = Type(type_name)
            db.session.add(type)
            db.session.commit()
        doc.type = type
        for category in doc_data['categories']:
            cat = Category.query.filter_by(name=category).first()
            if cat is None:
                cat = Category(category)
                db.session.add(cat)
                db.session.commit()
            doc.categories.append(cat)
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
    phil.email = 'uniphil@gmail.com'
    phil.set_password('asdf')
    models.db.session.add(phil)
    models.db.session.commit()


@manager.command
def init_db():
    from website.models import db
    db.create_all()


if __name__ == '__main__':
    manager.run()
