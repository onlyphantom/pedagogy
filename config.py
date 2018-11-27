import os
import pymysql

host = os.getenv('MYSQL_HOST')
user = os.getenv('MYSQL_USER')
password = os.getenv('MYSQL_PASSWORD')
database = os.getenv('MYSQL_DATABASE')

conn = pymysql.connect(
    host=host,
    port=int(3306),
    user=user,
    passwd=password,
    db=database)

# conn = pymysql.connect(user=user, 
#         password=password, 
#         database=database, 
#         port=int(3306),
#         host=host, 
#         ssl = {'ssl': {'ca': '/var/www/html/BaltimoreCyberTrustRoot.crt.pem'}})

# create the configuration class
class Config():
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'l3arn2t3ach'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'mysql+pymysql://Samuel:tirab33@localhost/assistants'
    FLASK_DEBUG = 0
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_RECORD_QUERIES = False
