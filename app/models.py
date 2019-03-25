from app import db
from datetime import datetime, date
import arrow

# association table
ta_assignment = db.Table(
    'assistants',
    # ForeignKey constraints that column to only allow values that are present in
    # the corresponding table (almost always the primary key for their owning table)
    db.Column('employee_id', db.Integer, db.ForeignKey('employee.id')),
    db.Column('workshop_id', db.Integer, db.ForeignKey('workshop.id'))
)

# association table
student_enrollment = db.Table(
    'enrollment',
    # ForeignKey constraints that column to only allow values that are present in
    # the corresponding table (almost always the primary key for their owning table)
    db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
    db.Column('workshop_id', db.Integer, db.ForeignKey('workshop.id'))
)


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), db.ForeignKey('user.email'))
    name = db.Column(db.String(64), unique=True)
    join_date = db.Column(db.Date)
    active = db.Column(db.Boolean, default=True, nullable=False)
    degree = db.Column(db.String(32))
    university = db.Column(db.String(64))
    assigned_ta = db.relationship(
        'Workshop',
        secondary=ta_assignment,
        backref=db.backref('assistants', lazy='dynamic'))

    assigned_instructor = db.relationship(
        'Workshop',
        backref=db.backref('instructor'))

    def __repr__(self):
        return '{}'.format(self.name)

class Workshop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workshop_name = db.Column(db.String(64))
    workshop_category = db.Column(db.Enum(
        "Academy", "DSS", "Corporate", "Weekend", "Others", 
        name="workshop_category"), nullable=False)
    workshop_instructor = db.Column(db.Integer, db.ForeignKey(
        'employee.id'), nullable=False)
    workshop_start = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    workshop_hours = db.Column(db.Integer, nullable=False)
    workshop_venue = db.Column(db.String(64), nullable=False)
    class_size = db.Column(db.Integer, nullable=False)
    responses = db.relationship('Response', backref='workshop', lazy='dynamic')

    def __repr__(self):
        past = arrow.get(self.workshop_start).humanize()
        # return '{} on {}'.format(self.workshop_name, self.workshop_start)
        return '{}, {}'.format(self.workshop_name, past)

    def printtime(self):
        past = arrow.get(self.workshop_start).humanize()
        return past

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workshop_id = db.Column(db.Integer, db.ForeignKey('workshop.id'), nullable=False)
    difficulty = db.Column(db.Integer)
    assistants_score = db.Column(db.Integer)
    knowledge = db.Column(db.Integer)
    objectives = db.Column(db.Integer)
    timeliness = db.Column(db.Integer)
    venue_score = db.Column(db.Integer)
    satisfaction_score = db.Column(db.Integer)
    comments = db.Column(db.Text)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    dob = db.Column(db.Date)
    batch = db.Column(db.String(32), nullable=False)
    gender = db.Column(db.Enum(
        "Male", "Female", 
        name="gender"), nullable=False)
    specialization = db.Column(db.Enum(
        "FT", "DV", "ML", "Ad Hoc", 
        name="specialization"), nullable=False)
    funding = db.Column(db.Enum(
        "Self funding", "Corporate", 
        name="funding"), nullable=False)
    previous_title = db.Column(db.String(64))
    ds_related = db.Column(db.Boolean, default=False)

    student_enrollment = db.relationship(
        'Workshop',
        secondary=student_enrollment,
        backref=db.backref('enrollment', lazy='dynamic'))

class Demoday(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    participants_size = db.Column(db.Integer, nullable=False)

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    project_link = db.Column(db.String(64))
    status = db.Column(db.Enum(
        "employed", "promoted",
        name="status"))
    employer = db.Column(db.String(32))
