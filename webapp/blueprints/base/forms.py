from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, InputRequired, ValidationError
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.widgets import TextInput, FileInput, Select, CheckboxInput


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

    function = SelectField('Function', choices=functions, validators=[DataRequired('Please select a funtion!')])

    comments = StringField('Something')

    agree = BooleanField('I unconditionally participate!', validators=[])

    submit = SubmitField('Submit')

    def validate_function(form, field):
        if field.data == 'nothing_selected':
            raise ValidationError('A function must be selected!')

    def validate_agree(form, field):
        if field.data == False:
            raise ValidationError("Don't you agree?")


class UploadForm(FlaskForm):
    """HttpTrigger"""
    file = FileField('', validators=[
        FileRequired(),
        FileAllowed(['txt', 'doc', 'docx'], 'Invalid File Type! Only .txt, .doc[x] files are allowed.')])
    submit = SubmitField('Submit')

    def validate_function(form, field):
        if field.data == 'nothing_selected':
            raise ValidationError('A function must be selected!')


class ChatForm(FlaskForm):
    """HttpTrigger"""
    message = StringField('Message')
