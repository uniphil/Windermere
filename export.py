from __future__ import print_function
import os
import shutil
import sqlite3
import datetime

EXPORT_FOLDER = '__export'

conn = sqlite3.connect('data.sqlite3')
c = conn.cursor()

if os.path.exists(EXPORT_FOLDER):
    print('clearing old export folder {}/'.format(EXPORT_FOLDER))
    shutil.rmtree(EXPORT_FOLDER)
os.makedirs(EXPORT_FOLDER)

n = 0
for file, in c.execute('SELECT file FROM documents'):
    src = 'files/documents/{}'.format(file)
    if not os.path.exists(src):
        print('document does not seem to exist: {}'.format(file))
        continue
    dst = '{}/{}'.format(EXPORT_FOLDER, file)
    dst_path = dst.rsplit('/', 1)[0]
    if not os.path.exists(dst_path):
        os.makedirs(dst_path)

    shutil.copyfile(src, dst)
    n += 1

print('copied {} files. compressing...'.format(n))

output = 'export-{}.tar.gz'.format(datetime.date.today().isoformat())
os.system('tar czf files/{} {}'.format(output, EXPORT_FOLDER))

print('saved compressed documents to {}'.format(output))
