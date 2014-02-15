"""
    website
    ~~~~~~~

    Python package for the windermere website.

    This file ties everything together. The wsgi app, 'app', is imported into
    the package namespace here.
"""

from os import environ

try:
    from flask import Flask
except ImportError as e:
    e.message += "\nHave you installed everything from requirements.txt and "\
                    "activated your virtualenv?"
    raise e


def configure(app, config):
    config = config or {}

    get = lambda key, default=None: config.get(key, environ.get(key, default))
    app.config.update(
        SECRET_KEY   = get('SECRET_KEY'),
        DEBUG        = get('DEBUG') in ('TRUE', 'True', 'true', True),
        HOST         = get('HOST', '127.0.0.1'),
        PORT         = int(get('PORT', 5000)),
        SQLALCHEMY_DATABASE_URI = get('SQLALCHEMY_DATABASE_URI', 'sqlite:///data.sqlite3'),
        UPLOAD_FOLDER= get('UPLOAD_FOLDER', 'uploads'),
        ACCESS_SEED  = get('ACCESS_SEED', 'WhiteChristmas'),
        CSRF_ENABLED = config.get('CSRF_ENABLED', True),  # for testing ONLY
    )


def create_app(config=None):
    app = Flask('website')
    configure(app, config)
    return app

app = create_app()


import models
import access
import admin
import endpoints
import filters
