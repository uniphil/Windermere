#!/bin/bash

cd /home/windermere/Windermere
source ../venv/bin/activate
gunicorn xaccel:xapp -b unix:///home/windermere/app.sock -D
