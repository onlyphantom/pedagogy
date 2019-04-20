import os
import pymysql

secretkey = os.environ.get('SECRET_KEY')
# database configuration
host = os.getenv('MYSQL_HOST')
user = os.getenv('MYSQL_USER')
password = os.getenv('MYSQL_PASSWORD')
database = os.getenv('MYSQL_DATABASE')
dburl = os.environ.get('DATABASE_URL')

adminsemail = ['samuel@algorit.ma']

conn = pymysql.connect(
    host=host,
    port=int(3306),
    user=user,
    passwd=password,
    db=database)
# create the configuration class
class Config():
    SECRET_KEY = secretkey or 'l3arn2t3ach'
    SQLALCHEMY_DATABASE_URI = dburl
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
    CACHE_DEFAULT_TIMEOUT = 86400 # 24 hours

