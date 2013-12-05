DONT'T forget to set secret key env variable bargh...


for deployment on nginx, we can d x-accel-redirect


`$ gunicorn xaccel:xapp`



remember to leave off the trailing slash for `app.config[UPLOAD_DIR]`

... should probably urljoin or something so that's not an issue, some day...
