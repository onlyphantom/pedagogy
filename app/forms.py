from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField, RadioField, TextAreaField
from wtforms.fields.html5 import IntegerRangeField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.users import User

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
    difficulty = IntegerRangeField("The lecture presented wasn't too difficult:", default=3)
    assistant = IntegerRangeField("The teaching assistants were helpful:", default=3)
    knowledgeable = IntegerRangeField("The trainer was knowledgeable about the training topics:", default=3)
    objective = IntegerRangeField("My training objectives were met:", default=3)
    time = IntegerRangeField("The time allocated for the training was sufficient:", default=3)
    venue = IntegerRangeField("Training venue and facilities were adequate and comfortable:", default=3)
    satisfaction = IntegerRangeField("With 5 being the most positive, how do you feel about the overall experience on this workshop:", default=3)
    comments = TextAreaField("If you have additional comments/ideas/improvements, please enter them below:")

    submit = SubmitField('Submit')

