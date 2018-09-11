from app import admin, db
from app.models import Employee, Workshop, Response
from flask_admin.contrib.sqla import ModelView

class AdminModelView(ModelView):
    pass

class EmployeelView(ModelView):
    column_searchable_list = ['name', 'degree', 'university']

admin.add_view(EmployeelView(Employee, db.session))
admin.add_view(ModelView(Workshop, db.session))
admin.add_view(ModelView(Response, db.session))
