from flask import Flask
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

admin = Admin(app, name='pedagogy')
db = SQLAlchemy(app)

from app import routes, models
