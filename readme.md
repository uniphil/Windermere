DONT'T forget to set secret key env variable bargh...


for deployment on nginx, we can d x-accel-redirect


`$ gunicorn xaccel:xapp`



remember to leave off the trailing slash for `app.config[UPLOAD_DIR]`


tricky dependency:
  * python imaging (preferably pillow)
  * libjpeg


## updating

 * switch user to windermere
 * always `source ~/.config.sh`


## upgrading the database

 * copy sqlite file from ./website/ to ./
 * `./manage.py db upgrade`
 * move it back

it may be necessary to skip the first migration.
