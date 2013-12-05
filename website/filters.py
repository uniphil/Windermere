"""
    website.filters
    ~~~~~~~~~~~~~~~

    Template filters for the Windermere site
"""

from datetime import datetime
from humanize import naturaltime
from . import app


@app.template_filter()
def since(then):
    return 'new' if then is None else naturaltime(datetime.now() - then)
