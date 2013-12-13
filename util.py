#!/usr/bin/env python2
"""
    util
    ~~~~

    Some useful tools for working with the windermere site.
"""

import os

try:
    assert "venv" in os.listdir('.'), "no venv here.."
    import imp
    imp.load_source('activate_this', 'venv/bin/activate_this.py')
except AssertionError:
    print "no venv to activate. continuing..."
except IOError:
    print "could not activate virtualenv '{}' for util.py...".format('venv')


try:
    from website import app
except ImportError:
    print "could not import app..."


def details(f):
    from datetime import datetime
    from website.models import ScenicPhoto

    for line in f:
        vals = [v.strip() for v in line.split('\t')]
        photo = ScenicPhoto()
        photo.photo = os.path.join(vals[1])
        photo.added = datetime.fromtimestamp(int(vals[2]))
        photo.title = vals[3]
        photo.description = vals[4]
        photo.featured = False
        yield photo


def old_photos_import():
    from website.models import db
    deets = open('photos.csv')
    deets.readline()  # skip header
    for photo in details(deets):
        db.session.add(photo)
    db.session.commit()


def resize_old_photos():
    from PIL import Image
    f = open('photos.csv')
    f.readline()  # skip header
    for line in f:
        path = app.config['scenic'](line.split('\t')[1].strip())
        try:
            im = Image.open(path)
            print '.',
        except IOError as e:
            print
            print e
            continue
        im.thumbnail((1140, 1140), Image.ANTIALIAS)
        im.save(path + '_sized.jpg', 'JPEG')
        im.thumbnail((256, 256), Image.ANTIALIAS)
        im.save(path + '_small.jpg', 'JPEG')
        del im


def clean_dead_photos():
    from website.models import db, ScenicPhoto

    for photo in ScenicPhoto.query.all():
        exists = True
        try:
            i = open(app.config['scenic'](photo.photo))
        except IOError:
            print 'x'
            db.session.delete(photo)
    db.session.commit()



if __name__ == '__main__':
    import sys
    cmd = sys.argv[1]
    print "running '{}'...".format(cmd)

    if cmd == 'activate':
        venv_path = os.path.join('venv', 'bin', 'activate')
        os.system('/bin/bash --rcfile {}'.format(venv_path))

    elif cmd in ['initdb', 'reinitdb']:
        from website.models import db, Partner
        from datetime import datetime
        if cmd == 'reinitdb':
            print 'dropping db'
            db.drop_all()
        print 'creating db'
        db.create_all()
        print 'seeding'
        partner = Partner()
        partner.name = 'Consortium Partner'
        partner.key = app.config['ACCESS_SEED']
        partner.last_keychange = datetime.now()
        db.session.add(partner)
        db.session.commit()

    elif cmd == 'mkphil':
        from website import models
        phil = models.Admin()
        phil.name = 'Phil Schleihauf'
        phil.username = 'phil'
        phil.set_password('asdf')
        models.db.session.add(phil)
        models.db.session.commit()

    elif cmd == 'mkuploads':
        uploads = app.config['UPLOAD_FOLDER']
        paths = [
            uploads,
            os.path.join(uploads, 'scenic'),
        ]
        for path in paths:
            try:
                os.makedirs(path)
            except OSError as e:
                if e.errno != 17:
                    raise e
                print '    {}: {}'.format(path, e.strerror)

    elif cmd == 'import_photos':
        old_photos_import()

    elif cmd == 'resize_old_photos':
        resize_old_photos()

    elif cmd == 'clean_dead_photos':
        clean_dead_photos()


    elif cmd == 'server':
        #from xaccel import app
        app.run(debug=True)

    else:
        print 'command "{}" not found'.format(cmd)
