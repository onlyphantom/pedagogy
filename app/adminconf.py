from flask import redirect, url_for, request
from app import app, admin, db
from app.models import Employee, Workshop, Response
from app.users import User
from flask_admin import BaseView, expose
from flask_admin.form import SecureForm
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

class AdminModelView(ModelView):
    # uses the WTForm SessionCSRF class to generate and validate tokens
    form_base_class = SecureForm

    def is_accessible(self):
        return (current_user.is_authenticated and
                current_user.email in app.config['ADMINS'])
    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

class EmployeeView(ModelView):
    def is_accessible(self):
        return (current_user.is_authenticated and
                current_user.leadership is True)

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    column_searchable_list = ['name', 'email', 'degree', 'university']
    column_editable_list = ['email', 'active', 'degree', 'university', 'assigned_ta']
    column_filters = ['email', 'active', 'join_date']


class WorkshopView(ModelView):
    def is_accessible(self):
        return (current_user.is_authenticated and
                current_user.leadership is True)

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    create_modal = True
    edit_modal = True
    can_export = True

class ResponseView(ModelView):
    def is_accessible(self):
        return (current_user.is_authenticated and
                current_user.email in app.config['ADMINS'])

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))


class AnalyticsView(BaseView):
    def is_accessible(self):
        return (current_user.is_authenticated and
                current_user.leadership is True)

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    @expose('/')
    def index(self):
        return self.render('admin/analytics_index.html', user=current_user)

admin.add_view(AdminModelView(User, db.session))
admin.add_view(EmployeeView(Employee, db.session))
admin.add_view(WorkshopView(Workshop, db.session))
admin.add_view(ResponseView(Response, db.session))
admin.add_view(AnalyticsView(name='Analytics', endpoint='analytics'))
