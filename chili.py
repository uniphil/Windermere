from os import environ
from website import app
app.secret_key = environ.get('SECRET_KEY')
app.config['debug'] = True
