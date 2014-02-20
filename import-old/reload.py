#!/usr/bin/env python

import json
import sqlite3
import dbtypes


DATABASE = 'data.sqlite'
UPLOAD_ROOT = '/srv/www/vhosts/windermere/sites/default/files/websiteuploads/'
SAVE_TO = 'data.json'

con = sqlite3.connect(DATABASE)
con.text_factory = lambda x: unicode(x, 'utf-8', 'ignore')
con.row_factory = sqlite3.Row


class Query(object):
    def __init__(self, qfilename):
        with open(qfilename) as f:
            self.query = f.read()

    def __enter__(self):
        con.__enter__()
        return con.execute(self.query)

    def __exit__(self, *args):
        con.__exit__(*args)



clean_filepath = lambda p: p[len(UPLOAD_ROOT):]


row_to_obj = lambda row: {k: row[k] for k in row.keys()}


photos = []
with Query('photos.sql') as cursor:
    for row in cursor:
        photo = row_to_obj(row)
        photo['filepath'] = clean_filepath(photo['filepath'])
        photos.append(photo)


with Query('documents.sql') as cursor:
    documents = [row_to_obj(row) for row in cursor]


data = dict(photos=photos, documents=documents)

with open(SAVE_TO, 'w') as f:
    json.dump(data, f, indent=2)

print('saved.')
