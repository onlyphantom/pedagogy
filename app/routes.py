from flask import render_template, flash, redirect, url_for, g
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db, cache
from app.analytics import global_total_stats, person_total_stats
from app.users import User
from app.models import Employee, Workshop, Response
from app.forms import LoginForm, RegistrationForm, SurveyForm, ResetPasswordRequestForm, ResetPasswordForm
from app.email import send_pw_reset_email
from datetime import datetime
from sqlalchemy import func

@app.before_request
def before_request():
    g.employee = None
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        g.employee = Employee.query.filter_by(email=current_user.email).first()

@app.route('/')
@app.route('/index')
def index():
    stats=global_total_stats()
    return render_template('index.html', stats=stats)

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
@cache.cached(timeout=86400*7)
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

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_pw_reset_email(user)
            flash('Instructions have been sent to your email')
        else:
            flash('Email is not registered with Pedagogy yet!')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)        

@app.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/<int:id>/qualitative/<int:page_num>')
@login_required
def qualitative(id, page_num):
    if g.employee is None:
        flash('Not registered as a Product team member yet. Check back later!')
        return redirect(url_for('index'))
    # return all qualitative comments for this user
    # qualitative.html is then embedded intlo the accomplishment template
    workshops = Workshop.query.filter_by(workshop_instructor=id).order_by(Workshop.workshop_start.desc())
    reviews = Response.query.filter(Response.workshop_id.in_(w.id for w in workshops), Response.comments != '').paginate(per_page=8, page=page_num, error_out=True)

    return render_template('sub/qualitative.html', id=id, page_num=page_num, reviews=reviews)

@app.route('/survey/<int:workshop_id>', methods=['GET', 'POST'])
def rate(workshop_id):
    workshop = Workshop.query.filter_by(id=workshop_id).first()
    timediff = datetime.utcnow() - workshop.workshop_start
    if workshop is None or timediff.days > 10:
        flash('Workshop survey is not available at the moment!')
        return redirect(url_for('index'))

    form = SurveyForm()
    form.workshop_id.data = workshop_id

    if form.validate_on_submit():
        response = Response(
            workshop_id=form.workshop_id.data,
            difficulty=form.difficulty.data,
            assistants_score=form.assistant.data,
            knowledge=form.knowledgeable.data,
            objectives=form.objective.data,
            timeliness=form.time.data,
            venue_score=form.venue.data,
            satisfaction_score=form.satisfaction.data,
            comments=form.comments.data
        )
        db.session.add(response)
        db.session.commit()
        return render_template('response.html')
    
    return render_template('survey.html', form=form, workshop_name=workshop.workshop_name, workshop_category=workshop.workshop_category)
