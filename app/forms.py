from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField, RadioField, TextAreaField
from wtforms.fields.html5 import IntegerRangeField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.users import User
from joblib import load

class LoginForm(FlaskForm):
    email = StringField('Work Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    email = StringField('Work Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('This email was already tied to an existing account.')

class SurveyForm(FlaskForm):
    workshop_id = HiddenField("Workshop id", validators=[DataRequired()])
    difficulty = IntegerRangeField("The lecture presented has a reasonable difficulty curve", default=3)
    assistant = IntegerRangeField("The teaching assistants were helpful", default=3)
    knowledgeable = IntegerRangeField("The trainer was knowledgeable about the training topics", default=3)
    objective = IntegerRangeField("My training objectives were met", default=3)
    time = IntegerRangeField("The time allocated for the training was sufficient", default=3)
    venue = IntegerRangeField("Training venue and facilities were adequate and comfortable", default=3)
    satisfaction = IntegerRangeField("What is your overall experience in this workshop?", default=3)
    comments = TextAreaField("Additional comments/ideas/improvements to your lead instructor and the training organizer")

    submit = SubmitField('Submit')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Set New Password')
