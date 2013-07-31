#
# __init__.py
#
# Python package for the windermere website.
#
# This file ties everything together. The wsgi app, 'app', is imported into
# the package namespace here.
#

try:
    from flask import Flask
except ImportError as e:
    e.message += "\nHave you installed everything from requirements.txt?"
    raise e

app = Flask(__name__)

try:
    import config
except ImportError as e:
    e.message += "\nHave you copied config-template.py to config.py?"

import models
import access
import admin
import endpoints
import filters
