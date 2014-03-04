#!/usr/bin/env python2
"""
    xaccel
    ~~~~~~

    Middleware to use nginx X-Accel-Redirect with Flask.
    Based on https://gist.github.com/ThiefMaster/5698549
"""

from distutils.sysconfig import get_python_lib
LIBS = get_python_lib()
print('original LIBS:', LIBS)

'/home/windermere/venv/src/flask-admin/flask_admin/static/bootstrap/css/bootstrap.css'
'/home/windermere/venv/local/lib/python2.7/site-packages'

if '/local/lib/python' not in LIBS:
    import os
    assert '/lib/python' in LIBS, 'you have an odd site-packages setup or something...'
    LOCAL_LIBS = LIBS.replace('/lib/python', '/local/lib/python')
    if not os.path.isdir(LOCAL_LIBS):
        print('hrmph no local libs site-packages or something?')
    else:
        print('replacing site-packages path with /local/ one')
        LIBS = LOCAL_LIBS


# for third-party assets (namely flask-admin)
SRCS = LIBS.split('/local/lib/python', 1)[0] + '/src'


class XAccelMiddleware(object):
    def __init__(self, app):
        app.config['USE_X_SENDFILE'] = True
        app.debug = True
        self.app = app

    def __call__(self, environ, start_response):
        def _start_response(status, headers, *args, **kwargs):
            new_headers = [self.xfix(header) for header in headers]
            return start_response(status, new_headers, *args, **kwargs)
        return self.app(environ, _start_response)

    def xfix(self, header):
        if header[0].lower() != 'x-sendfile':
            return header
        else:
            _, path = header
            xar = 'X-Accel-Redirect'
            if path.startswith(app.root_path):
                return [xar, path[len(app.root_path):]]
            elif path.startswith(LIBS):
                return [xar, '/libstatic' + path[len(LIBS):]]
            elif path.startswith(SRCS):
                return [xar, '/libsrc' + path[len(SRCS):]]
            elif path.startswith(app.config['UPLOAD_FOLDER']):
                return [xar, '/uploads' + path[len(app.config['UPLOAD_FOLDER']):]]
            else:
                return ['X-Filesend-Error-Noooooooooo', str(header) + ' ..... ' + LIBS]


from website import app
xapp = XAccelMiddleware(app)
