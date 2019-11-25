from flask import Flask
from flask_caching import Cache
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Production, Development, host, user, password, database
import logging
from logging.handlers import SMTPHandler
import pymysql
import sqlite3
import os

app = Flask(__name__)

# create conditional connection
if(os.getenv('FLASK_ENV') == 'development'):
    app.config.from_object(Development)
    conn = sqlite3.connect('test.db')
    app.config.from_object(Development)
else:
    conn = pymysql.connect(
        host=host,
        port=int(3306),
        user=user,
        passwd=password,
        db=database)
    app.config.from_object(Production)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
admin = Admin(app, name='pedagogy')
mail = Mail(app)
cache = Cache(app)

# let Flask-Login know which page (function name) handles login
login.login_view = 'login'

if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = ()


from app import routes, models, adminconf, users, errors
