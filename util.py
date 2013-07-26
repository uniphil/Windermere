#!/usr/bin/env python2

try:
    import imp
    imp.load_source('activate_this', 'venv/bin/activate_this.py')
except ImportError:
    print "could not activate virtualenv for util.py..."


try:
    from website import app
except ImportError:
    print "could not import app..."

if __name__ == '__main__':
    import sys
    cmd = sys.argv[1]

    if cmd == 'activate':
        import os
        venv_path = os.path.join('venv', 'bin', 'activate')
        os.system('/bin/bash --rcfile {}'.format(venv_path))

    elif cmd in ['initdb', 'reinitdb']:
        from website.models import db
        if cmd == 'reinitdb':
            import os
            try:
                os.remove('website/dev-db.sqlite3')
            except OSError:
                print 'no database at website/dev-db.sqlite3. ignoring...'
        db.create_all()

    elif cmd == 'server':
        app.run(debug=True)

    else:
        print 'command "{}" not found'.format(cmd)
