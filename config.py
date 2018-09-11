import os

# /Users/Samuel/Dropbox/Projects/Python/Pedagogy
basedir = os.path.abspath(os.path.dirname(__file__))

# create the configuration class
class Config():
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'l3arn2t3ach'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'mysql+pymysql://Samuel:tirab33@localhost/assistants'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ECHO = True
