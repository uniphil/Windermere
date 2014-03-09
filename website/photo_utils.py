# -*- coding: utf-8 -*-
"""
    website.photo_utils
    ~~~~~~~~~~~~~~~~~~~

    tools for dealing with photos, namely cacheing resized versions.

    :copyright: 2014 Windermere Consortium
    :author: uniphil
    :license: MIT
"""

import os
from PIL import Image
from . import app


cache_folder = app.config['PHOTO_CACHE_FOLDER']


def init(app):
    global cache_folder
    if not os.path.isabs(cache_folder):
        cache_folder = os.path.join(app.root_path, cache_folder)
    if not os.path.isdir(cache_folder):
        os.makedirs(cache_folder)


def scale_image(source, dest, size):
    """Scale images to a maximum width and save them in a specified location.

    The destination folder must exist before calling this function
    """
    im = Image.open(source)
    if im.mode in ('1', 'L', 'P'):
        im = im.convert('RGB')
    im.thumbnail((size, size*2), Image.ANTIALIAS)  # try to always get the width right
    im.save(dest, 'JPEG')


def scaled_cached(fp, size):
    rel_path = fp.replace(app.config['UPLOAD_FOLDER'], '')
    if rel_path.startswith('/'):
        rel_path = rel_path[1:]
    scaled_fp = os.path.join(cache_folder, str(size), rel_path)
    if not os.path.isfile(scaled_fp):
        scaled_folder = os.path.dirname(scaled_fp)
        if not os.path.isdir(scaled_folder):
            os.makedirs(scaled_folder)
        scale_image(fp, scaled_fp, size)
    return scaled_fp


init(app)  # eventually this should be migrated to website.__init__.py
