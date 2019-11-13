from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, InputRequired, ValidationError
from flask_wtf.file import FileField, FileRequired, FileAllowed


functions = [('nothing_selected', 'Select your Function...'),
             ('HttpTrigger', 'Forecast Sales'),
             ('ForecastAPI', 'Forecast Temperature'),
             ('Hello', 'Hello, World!')]


class FileForm(FlaskForm):
    """HttpTrigger"""
    file = FileField('File', validators=[
        FileRequired(),
        FileAllowed(['txt', 'csv'], 'Invalid File Type! Only .txt, .csv files are allowed.')])

    email = EmailField('Email address', validators=[
        InputRequired("Please enter your email address!"),
        Email("Please check your email address!")])

    function = SelectField('function', id='function', choices=functions, validators=[DataRequired('Please select a funtion!')])

    comments = StringField('Something')

    submit = SubmitField('Submit')

    def validate_function(form, field):
        if field.data == 'nothing_selected':
            raise ValidationError('A function must be selected!')
