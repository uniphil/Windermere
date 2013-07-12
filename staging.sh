#!/bin/bash

cd /home/phil/py/windermere/
source venv/bin/activate

HOST_BIND=127.0.0.1:9001
WORKERS=2

gunicorn -w $WORKERS -b $HOST_BIND website:app

