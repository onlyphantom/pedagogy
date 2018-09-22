from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user
from app import app, db
from app.users import User
from app.forms import LoginForm, RegistrationForm
from datetime import datetime

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/index')
def index():
    workshops = [
        {'name': 'BCA Cohort 3 Visualization',
         'instructor':'Ajeng'},
        {'name': 'Academy Neural Network',
         'instructor':'Tiara'}
    ]
    return render_template('index.html', workshops=workshops)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).one()
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
    form = RegistrationForm()
    return render_template('register.html', form=form)
