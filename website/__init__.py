#
# __init__.py
#
# Python package for the windermere website.
#
# This file ties everything together. The wsgi app, 'app', is imported into
# the package namespace here.
#

from flask import Flask

app = Flask(__name__)

import config
from . import endpoints

