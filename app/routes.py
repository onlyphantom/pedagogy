from flask import render_template
from app import app

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
