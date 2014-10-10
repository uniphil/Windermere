DONT'T forget to set secret key env variable bargh...


for deployment on nginx, we can d x-accel-redirect

`$ gunicorn xaccel:xapp`

see more in `deploy-configs`


remember to leave off the trailing slash for `app.config[UPLOAD_DIR]`


tricky dependencies:

  * python imaging (preferably pillow)
  * libjpeg


# Set up

1. initialize the database

2. set up an admin user (mkphil)

3. reset admin password

4. init the contributor key

5. import content from backup

6. set up contact form email destinations

7. set up the server with the config in `deploy-configs`

8. enable the app to [start up on boot](http://stackoverflow.com/questions/7221757/run-automatically-program-on-startup-under-linux-ubuntu) `sudo update-rc.d windermere defaults`

9. export all necessary further configs (see `website/__init__.py`)

10. install postfix


## updating

 * switch user to windermere
 * always `source ~/.config.sh`


## upgrading the database

flask-migrate doesn't handle package apps correctly, so you must use an
absolute path the the db for the `SQLITE_DATABASE_URL` environment config.

but then it's easy

```bash
./manage.py db upgrade
```
