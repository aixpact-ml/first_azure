from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, InputRequired

from flask_wtf.file import FileField, FileRequired

class FileForm(FlaskForm):
    file = FileField('File', validators=[FileRequired()])
    email = EmailField('Email address', validators=[
        InputRequired("Please enter your email address."),
        Email("Please enter your email address.")])
    submit = SubmitField('Subimt')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
