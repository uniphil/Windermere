#!/usr/bin/env python2

try:
    import os
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


if __name__ == '__main__':
    import sys
    cmd = sys.argv[1]
    print "running '{}'...".format(cmd)

    if cmd == 'activate':
        import os
        venv_path = os.path.join('venv', 'bin', 'activate')
        os.system('/bin/bash --rcfile {}'.format(venv_path))

    elif cmd in ['initdb', 'reinitdb']:
        from website.models import db
        if cmd == 'reinitdb':
            import os
            try:
                os.remove('dev-db.sqlite3')
            except OSError:
                print 'no database at dev-db.sqlite3. ignoring...'
        db.create_all()

    elif cmd == 'mkphil':
        from website import models
        phil = models.Admin()
        phil.name = 'Phil Schleihauf'
        phil.username = 'phil'
        phil.set_password('asdf')
        models.db.session.add(phil)
        models.db.session.commit()


    elif cmd == 'server':
        app.run(debug=True)

    else:
        print 'command "{}" not found'.format(cmd)
