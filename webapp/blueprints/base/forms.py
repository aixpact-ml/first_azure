from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, InputRequired
from flask_wtf.file import FileField, FileRequired


functions = [('HttpTrigger', 'Forecast POS'),
             ('ForecastAPI', 'Forecast temperature'),
             ('Hello', 'Hello, World!')]


class FileForm(FlaskForm):
    file = FileField('File', validators=[FileRequired()])
    email = EmailField('Email address', validators=[
        InputRequired("Please enter your email address."),
        Email("Please enter your email address.")])
    function = SelectField('API name', choices=functions, validators=[DataRequired()])
    submit = SubmitField('Submit')

    # TODO in-field validation
    def __init__(self, *args, **kwargs):
        super(FileForm, self).__init__(*args, **kwargs)

    def validate(self):
        initial_validation = super(FileForm, self).validate()
        if not initial_validation:
            return False

        if not self.file:
            self.file.errors.append('Please select file.')
            return False

        if not self.email:
            self.email.errors.append('Please enter email.')
            return False

        if not self.function:
            self.function.errors.append('Please choose function.')
            return False

        return True


# class LoginForm(FlaskForm):
#     username = StringField('Username', validators=[DataRequired()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     remember_me = BooleanField('Remember Me')
#     submit = SubmitField('Sign In')
