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

if '/local/lib/python' not in LIBS:
    import os
    assert '/lib/python' in LIBS, 'you have an odd site-packages setup or something...'
    LOCAL_LIBS = LIBS.replace('/lib/python', '/local/lib/python')
    if not os.path.isdir(LOCAL_LIBS):
        print('hrmph no local libs site-packages or something?')
    else:
        print('replacing site-packages path with /local/ one')
        LIBS = LOCAL_LIBS


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
            print(header)
            if header[1].startswith(app.root_path):
                return ['X-Accel-Redirect', header[1][len(app.root_path):]]
            elif header[1].startswith(LIBS):
                return ['X-Accel-Redirect', '/libstatic' + header[1][len(LIBS):]]
            elif header[1].startswith(app.config['UPLOAD_FOLDER']):
                return ['X-Accel-Redirect', '/uploads' + header[1][len(app.config['UPLOAD_FOLDER']):]]
            else:
                return ['X-Filesend-Error-Noooooooooo', str(header) + ' ..... ' + LIBS]


from website import app
xapp = XAccelMiddleware(app)
