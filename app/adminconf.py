from app import admin, db
from app.models import Employee, Workshop, Response
from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView

class AdminModelView(ModelView):
    pass

class EmployeelView(ModelView):
    column_searchable_list = ['name', 'degree', 'university']
    column_editable_list = ['active', 'degree', 'university', 'assigned_ta']
    column_filters = ['active', 'join_date']

class WorkshopView(ModelView):
    create_modal = True
    edit_modal = True
    can_export = True

class AnalyticsView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/analytics_index.html')

admin.add_view(EmployeelView(Employee, db.session))
admin.add_view(WorkshopView(Workshop, db.session))
admin.add_view(ModelView(Response, db.session))
admin.add_view(AnalyticsView(name='Analytics', endpoint='analytics'))
