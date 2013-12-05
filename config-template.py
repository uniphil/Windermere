"""
    config-template
    ~~~~~~~~~~~~~~~

    Copy this file to config.py in this directory, and fill in the blanks

    This file is part of the Windermere Consortium (Created for Bill Arnott,
    University of Ottawa Geology Dept)
"""


from website import app


app.config.update(
    # make sure the secret key is not guessable!
    SECRET_KEY='',
    # database stuff. see here: http://pythonhosted.org/Flask-SQLAlchemy/config.html
    SQLALCHEMY_DATABASE_URI='',
    UPLOAD_FOLDER='',
)
