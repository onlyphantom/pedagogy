from app import db
from datetime import datetime

# association table
ta_assignment = db.Table(
    'assistants',
    db.Column('employee_id', db.Integer, db.ForeignKey('employee.employee_id')),
    db.Column('workshop_id', db.Integer, db.ForeignKey('workshop.workshop_id'))
)

inst_assignment = db.Table(
    'instructors',
    db.Column('employee_id', db.Integer, db.ForeignKey('employee.employee_id')),
    db.Column('workshop_id', db.Integer, db.ForeignKey('workshop.workshop_id'))
)

class Employee(db.Model):
    employee_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    degree = db.Column(db.String(32))
    university = db.Column(db.String(32))
    assigned_ta = db.relationship(
        'Workshop',
        secondary=ta_assignment,
        backref=db.backref('assistants', lazy='dynamic'))

    assigned_instructor = db.relationship(
        'Workshop',
        secondary=inst_assignment,
        backref=db.backref('instructor', lazy='dynamic'))

    def __repr__(self):
        return '<Employee {}, join date: {}>'.format(self.name, self.join_date)

class Workshop(db.Model):
    workshop_id = db.Column(db.Integer, primary_key=True)
    workshop_name = db.Column(db.String(32))
    workshop_category = db.Column(db.String(32))
    workshop_date = db.Column(db.DateTime, default=datetime.utcnow)
    workshop_venue = db.Column(db.String(32))
    class_size = db.Column(db.Integer)
    responses = db.relationship('Response', backref='workshop', lazy='dynamic')

class Response(db.Model):
    response_id = db.Column(db.Integer, primary_key=True)
    difficulty = db.Column(db.Integer)
    assistants_score = db.Column(db.Integer)
    knowledge = db.Column(db.Integer)
    objectives = db.Column(db.Integer)
    timeliness = db.Column(db.Integer)
    venue_score = db.Column(db.Integer)
    satisfaction_score = db.Column(db.Integer)
    comments = db.Column(db.String(256))
