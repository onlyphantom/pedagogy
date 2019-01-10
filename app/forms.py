from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField, RadioField
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
    # workshop_id = HiddenField("Workshop id", validators=[DataRequired()])
    difficulty = RadioField("Course Difficulty", 
                    choices=[(1, 'Strongly Disagree'), (2, 'Disagree'), (5, 'Strongly Agree')],
                    validators=[DataRequired()])
    assistants_score = RadioField("Assistants Helpfulness", 
                    choices=[(1, 'Strongly Disagree'), (2, 'Disagree'), (5, 'Strongly Agree')],
                    validators=[DataRequired()])

    # def __init__(self, *args, **kwargs):
    #     super(SurveyForm, self).__init__(*args, **kwargs)
    #     self.fields['workshop_id'] = workshop_id

