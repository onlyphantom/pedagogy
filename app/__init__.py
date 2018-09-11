from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

from app import routes, models
from app.models import Employee, Workshop, Response

admin = Admin(app, name='pedagogy')
admin.add_view(ModelView(Employee, db.session))
admin.add_view(ModelView(Workshop, db.session))
admin.add_view(ModelView(Response, db.session))
