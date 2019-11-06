# import logging
# import datetime
# import requests
# import os
# import mimetypes

# from flask import (Flask, Blueprint, redirect, request, flash, url_for, jsonify,
#                    render_template, session, current_app, make_response,
#                    send_file, send_from_directory)
# from flask_mail import Mail, Message, Attachment
# from flask_login import current_user
# from logging.handlers import SMTPHandler
# from werkzeug.utils import secure_filename
# from forms import LoginForm, FileForm

from flask import Flask
# from flask_login import current_user

from importlib import import_module

from config.settings import config
# from functions import _log_msg, allowed_file, send_email, block_blob
from utils.functions import mail
from extensions import db, login_manager, csrf


# import algo

# Azure configuration > general settings > Startup Command:
# gunicorn --bind=0.0.0.0 --timeout 1200 webapp.app:create_app()
# gunicorn --bind=0.0.0.0 --timeout 600 hello:app

# Local Docker
# gunicorn -w 2 -b :19000 --reload "webapp.app:create_app()"
#

def create_app():
    app = Flask(__name__)
    config_app(app)
    register_blueprints(app)
    init_extensions(app)
    return app


def register_blueprints(app):
    for module_name in ('blueprints.base',):
        module = import_module('webapp.{}.views'.format(module_name))
        app.register_blueprint(module.blueprint)


def config_app(app):
    # app.config settings
    app.config.from_object(config)
    app.config['DEV'] = False

    # Flask-Mail settings via Azure ENV and below
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False

    # Sanity check config settings
    assert app.config['MAIL_DEFAULT_SENDER'] == 'frank@aixpact.com', 'Flask-Mail settings failed'
    assert config.FRANK == 'test this environmental value', 'config settings failed'
    assert config.FRANK == app.config['FRANK'], 'config settings failed'
    assert app.config['SECRET_KEY'] == config.SECRET_KEY, 'SECRET_KEY not set'


def init_extensions(app):
    #
    csrf.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

#
app = create_app()



#######################


# @app.route('/', methods=['GET', 'POST'])
# def upload_form():
#     form = FileForm()
#     if form.validate_on_submit():
#         file = form.file.data
#         email = form.email.data
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             flash(f'File: {filename} is recieved, saving...')

#             ext = '.' + filename.split('.')[-1]
#             file_in = email.replace('@', '_').replace('.', '_').replace('-', '_') + ext
#             try:
#                 # Local dev
#                 file.save(os.path.join(app.config['LOCAL'], file_in))
#             except:
#                 # Azure
#                 file.save(file_in)
#                 block_blob(file_in, app.config['BLOB_CONX'])
#         send_email(email, file_in)
#         flash(f'thank you an email has been sent to: {email} with attachment: {file_in}')
#         return redirect(url_for('thankyou', message=file_in))
#         flash(f'Try again.....')
#     return render_template('upload.html', form=form)


# @app.route("/thankyou")
# def thankyou():
#     return jsonify(status='succes', response=request.args.get('message'))


# @app.route("/function/<function_name>")
# def function(function_name):
#     """Takes some time....."""
#     response = requests.get(f'http://www.aixpact.ml/api/{function_name}')
#     return response.text  # jsonify(response=response.content)


# # Run and debug locally in Jupyter
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', debug=True, port=8241)
