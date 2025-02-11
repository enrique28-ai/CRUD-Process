from flask_wtf import FlaskForm
from wtforms import StringField,  SubmitField, PasswordField, SelectField
from wtforms.validators import Length, DataRequired, Email, ValidationError, EqualTo
from models.user_model import User

class RegisterForm(FlaskForm):

    SECURITY_QUESTIONS = [
    ("What is your mother's maiden name?", "What is your mother's maiden name?"),
    ("What was your first pet's name?", "What was your first pet's name?"),
    ("What is your favorite book?", "What is your favorite book?"),
    ("What city were you born in?", "What city were you born in?"),
]

    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists! Please try a different username')
        
    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Email address already exists please try a different email address')

    username = StringField(label='User Name:', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1', message='Passwords must match !'), DataRequired()])
    security_question = SelectField(label="Choose a Security Question", choices=SECURITY_QUESTIONS, validators=[DataRequired()])
    security_answer = StringField(label="Security Answer", validators=[DataRequired()])
    
    submit = SubmitField(label='Create Account')

class LoginForm(FlaskForm):
    username = StringField(label='User Name:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')

class SecurityQuestionForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired()])
    security_answer = StringField(label="Security Answer", validators=[DataRequired()])
    submit = SubmitField(label="Verify Answer")

class ResetPasswordForm(FlaskForm):
    password = PasswordField(label="New Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(label="Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField(label="Reset Password")



