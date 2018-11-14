from flask import render_template, flash, redirect, url_for, g
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.analytics import global_total_stats, person_total_stats
from app.users import User
from app.models import Employee, Workshop, Response
from app.forms import LoginForm, RegistrationForm
from datetime import datetime
from sqlalchemy import func

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        g.employee = Employee.query.filter_by(email=current_user.email).first()
        db.session.commit()

@app.route('/')
@app.route('/index')
@login_required
def index():
    workshops = [
        {'name': 'BCA Cohort 3 Visualization',
         'instructor':'Ajeng'},
        {'name': 'Academy Neural Network',
         'instructor':'Tiara'}
    ]
    stats=global_total_stats()
    return render_template('index.html', employee=g.employee, workshops=workshops, stats=stats)

print(current_user)
@app.route('/accomplishment')
@login_required
def accomplishment():
    # handle case of employee not found in database
    if g.employee is None:
        flash('Not registered as a Product team member yet. Check back later!')
        return redirect(url_for('index'))
    personstats=person_total_stats()
    return render_template('accomplishment.html', personstats=personstats)

@app.route('/analytics')
@login_required
def analytics():
    return render_template('analytics.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Welcome to Pedagogy. You\'re now registered. Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)
