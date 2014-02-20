#!/bin/bash

cd /home/windermere/Windermere
source ../venv/bin/activate

export SECRET_KEY=abc123
export SQLALCHEMY_DATABASE_URI=/home/windermere/data.sqlite3
export UPLOAD_FOLDER=/home/windermere/files
export ACCESS_SEED=WhateverMan

gunicorn xaccel:xapp -b unix:///home/windermere/app.sock -D
