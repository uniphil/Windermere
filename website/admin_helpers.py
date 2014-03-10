# -*- coding: utf-8 -*-
"""
    website.utils
    ~~~~~~~~~~~~~

    Unorganized cache of stuff to support the windermere codebase.

    :license: BSD or something
    :author: uniphil
"""

import os
from functools import wraps, partial
from tempfile import NamedTemporaryFile
from werkzeug.security import safe_join
from werkzeug.exceptions import NotFound
from wtforms import fields, widgets
from flask import url_for, send_file
from flask.ext.admin.model.helpers import prettify_name
from website import app


@app.route('/admin/uploads/<path:folder>/<filename>')
def uploaded_file(folder, filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
    filepath = safe_join(path, filename)
    if not os.path.isabs(filepath):
        filepath = os.path.join(app.root_path, filepath)
    if not os.path.isfile(filepath):
        raise NotFound()
    return send_file(filepath)


class FileInput(widgets.FileInput):
    """An input like wtforms' FileInput that shows existing filenames"""
    file_tmpl = '<div><a href="{url}">{filename}</a></div>'
    photo_tmpl = ('<div>'
                    '<a href="{url}">'
                      '<img src="{url}" alt="thumbnail for {filename}" />'
                    '</a>'
                  '</div>')

    def __init__(self, endpoint, folder, *args, **kwargs):
        self.template = self.photo_tmpl if kwargs.pop('photo', False) else self.file_tmpl
        self.endpoint = endpoint
        self.folder = folder
        super(FileInput, self).__init__(*args, **kwargs)

    def __call__(self, field, **kwargs):
        rendered_widget = super(FileInput, self).__call__(field, **kwargs)
        if field.data:
            url = url_for(self.endpoint, folder=self.folder, filename=field.data)
            current = self.template.format(url=url, filename=field.data)
            return widgets.HTMLString('{}{}'.format(current, rendered_widget))
        else:
            return rendered_widget


class FileField(fields.FileField):
    def __init__(self, label='', validators=None,
                 endpoint=None, folder=None, photo=False, **options):
        super(FileField, self).__init__(label, validators, **options)
        self.widget = FileInput(endpoint, folder=folder, photo=photo)


def wrap_method_of(cls):    
    def wrapper(new_function):
        method_name = new_function.__name__
        original_method = getattr(cls, method_name)
        @wraps(new_function)
        def wrapped(self, *args, **kwargs):
            super_ish = partial(original_method, self)
            return new_function(super_ish, self, *args, **kwargs)
        setattr(cls, method_name, wrapped)
        return wrapped
    return wrapper


def wrap_file_field(field_name, upload_dir, endpoint, photo=False):
    """Wraps a sqla.ModelView from flask_admin to pull out files"""

    drop_dir = os.path.join(app.config['UPLOAD_FOLDER'], upload_dir)

    def get_safe_filename(name):
        name, ext = os.path.splitext(name)  # pull off for later
        name = ''.join(os.path.split(name))  # take any directory tricks out
        name = safe_join('', name) or ''  # goodbye any lingering tricks
        if name not in ('', '.'):
            # atomically reserve a unique filename
            with NamedTemporaryFile(dir=drop_dir, delete=False,
                                    prefix=name, suffix=ext) as safe_file:
                safe_filepath = safe_file.name
            return os.path.split(safe_filepath)[-1]  # just the filename
        else:
            return None

    def save(incoming, filename):
        path = os.path.join(drop_dir, filename)
        incoming.save(path)

    def remove(filename):
        path = os.path.join(drop_dir, filename)
        os.remove(path)

    def wrap_view(sqla_model_view):

        @wrap_method_of(sqla_model_view)
        def create_model(super_ish, self, form):
            field = getattr(form, field_name)
            incoming = field.data
            filename = get_safe_filename(incoming.filename)
            field.data = filename  # sqla willl store this for us
            result = super_ish(form)
            if result is False:
                remove(filename)
                return False
            if filename is not None:
                save(incoming, filename)
            return True

        @wrap_method_of(sqla_model_view)
        def update_model(super_ish, self, form, model):
            field = getattr(form, field_name)
            stored_name = getattr(model, field_name)
            incoming = field.data
            filename = get_safe_filename(incoming.filename)
            field.data = filename or stored_name
            result = super_ish(form, model)
            if result is False:
                remove(filename)
                return False
            if filename is not None:
                if stored_name is not None:
                    remove(stored_name)
                save(incoming, filename)
            return True

        @wrap_method_of(sqla_model_view)
        def delete_model(super_ish, self, model):
            result = super_ish(model)
            if result is False:
                return False
            stored_name = getattr(model, field_name)
            if stored_name is not None:
                remove(stored_name)
            return True

        if sqla_model_view.form_extra_fields is None:
            sqla_model_view.form_extra_fields = {}
        if field_name not in sqla_model_view.form_extra_fields:
            nice_name = prettify_name(field_name)
            field = FileField(nice_name, photo=photo, endpoint=endpoint, folder=upload_dir)
            sqla_model_view.form_extra_fields[field_name] = field


        return sqla_model_view

    return wrap_view
