from distutils.sysconfig import get_python_lib
LIBS = get_python_lib()


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
        elif header[1].startswith(app.root_path):
            return ['X-Accel-Redirect', header[1][len(app.root_path):]]
        elif header[1].startswith(LIBS):
            return ['X-Accel-Redirect', '/libstatic' + header[1][len(LIBS):]]
        else:
            return ['X-Filesend-Error-Noooooooooo', str(header)]


from website import app
xapp = XAccelMiddleware(app)
