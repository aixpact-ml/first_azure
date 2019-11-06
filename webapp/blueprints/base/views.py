import pandas as pd
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
        api_function = form.api.data

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
                block_blob(file_in, config.BLOB_CONX)

        return redirect(url_for('base_blueprint.thankyou',
            file_in=file_in,
            email=email,
            function_name=api_function))
        flash(f'Try again.....')
    return render_template('base/upload.html', form=form)


@blueprint.route("/thankyou")
def thankyou():
    file_in = request.args.get('file_in')
    email = request.args.get('email')
    function_name = request.args.get('function_name')
    file_out = f'{function_name}_file_in'
    url = f'http://www.aixpact.ml/api/{function_name}'

    # Call serverless function and save content to csv
    response = requests.post(url, files={'file': open(file_in, 'rb')})
    assert len(response.text) > 0, f'DEBUG response: {response}'
    assert len(response.text) > 0, f'DEBUG response: {response.text}'

    df = pd.read_csv(response.text, header=0)
    df.to_csv(file_out)

    # Send email
    send_email(email, file_out)
    flash(f'Thank you! \n\nAn email has been sent to: {email} \nAttachment: {file_out}')

    # return # jsonify(response=response.content)
    try:
        r = render_template('base/thankyou.html',
            email=request.args.get('email'),
            file=request.args.get('file_in'))
        return r
    except:
        return jsonify(status='succes', response=request.args.get('message'))
