import logging
import datetime
import requests
import os
import mimetypes
from flask import (Flask, Blueprint, redirect, request, flash, url_for, jsonify,
                   render_template, session, current_app, make_response,
                   send_file, send_from_directory)
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename

from forms import LoginForm, FileForm

from config.settings import config
from utils.functions import _log_msg, allowed_file, send_email, block_blob
from utils.functions import mail
# from functions import *
# import algo
# from webapp.extensions import db, login_manager, csrf #, mail

from . import blueprint


@blueprint.route("/")
def index():
    return jsonify(status='succes', response='api is online')


@blueprint.route("/function/<function_name>")
def function(function_name):
    """Takes some time....."""
    response = requests.get(f'http://www.aixpact.ml/api/{function_name}')
    return response.text  # jsonify(response=response.content)


@blueprint.route('/upload_form', methods=['GET', 'POST'])
def upload_form():
    form = FileForm()
    if form.validate_on_submit():
        file = form.file.data
        email = form.email.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            flash(f'File: {filename} is recieved, saving...')

            ext = '.' + filename.split('.')[-1]
            file_in = email.replace('@', '_').replace('.', '_').replace('-', '_') + ext
            try:
                # Local dev
                file.save(os.path.join(config.LOCAL, file_in))
            except:
                # Azure
                file.save(file_in)
                block_blob(file_in, app.config['BLOB_CONX'])
        send_email(email, file_in)
        flash(f'thank you an email has been sent to: {email} with attachment: {file_in}')
        return redirect(url_for('thankyou', message=file_in))
        flash(f'Try again.....')
    return render_template('upload.html', form=form)


@blueprint.route("/thankyou")
def thankyou():
    return jsonify(status='succes', response=request.args.get('message'))
