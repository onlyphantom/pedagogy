import os
import pymysql
import sqlite3

secretkey = os.environ.get('SECRET_KEY')
# database configuration
host = os.getenv('MYSQL_HOST')
user = os.getenv('MYSQL_USER')
password = os.getenv('MYSQL_PASSWORD')
database = os.getenv('MYSQL_DATABASE')
dburl = f'mysql+pymysql://{user}:{password}@{host}/{database}'
# create conditional connection
if(os.getenv('FLASK_ENV') == 'development'):
    conn = sqlite3.connect('test.db')
else:
    conn = pymysql.connect(
        host=host,
        port=int(3306),
        user=user,
        passwd=password,
        db=database)

adminsemail = [
    'samuel@algorit.ma',
    'tiara@algorit.ma']

# create the configuration class
class Config():
    SECRET_KEY = secretkey or 'l3arn2t3ach'
    SQLALCHEMY_DATABASE_URI = dburl
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    # 'mysql+pymysql://Samuel:tirab33@localhost/assistants'
    FLASK_DEBUG = 1
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_RECORD_QUERIES = False
    # mail server configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = adminsemail
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 86400 # 24 hours = 86400

class Development(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../test.db'
    DEBUG = True

class Production(Config):
    SQLALCHEMY_DATABASE_URI = dburl