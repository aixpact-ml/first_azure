import pandas as pd
import logging
import datetime
import requests
import os
import uuid
import mimetypes
from flask import (Flask, Blueprint, redirect, request, flash, url_for, jsonify,
                   render_template, session, current_app, make_response,
                   send_file, send_from_directory)
from flask_mail import Message
from werkzeug.utils import secure_filename

from .forms import FileForm

from config.settings import config
from utils.functions import _log_msg, allowed_file, binary2csv, predict
from utils.email import send_email, mail
from utils.decorators import fire_and_forget

from webapp.extensions import mail
from . import blueprint


def handle_uploaded_file(file):
    # Azure vs. local, web form vs. POST
    try:
        os.mkdir('./data')
    except:
        pass
    file_temp = f'temp_in.{file.filename.split(".")[-1]}'
    file_dest = os.path.join('./data', file_temp)
    try:
        # When file in is raw data
        with open(file_dest, "wb") as dest:
            dest.write(file)
        print('DEBUG write to file', type(file))
        logging.info('DEBUG write to file', type(file))
    except:
        # When file_in is <class 'werkzeug.datastructures.FileStorage'>
        file.save(file_dest)
        file.close()
        print('DEBUG save as file', type(file))
        logging.info('DEBUG save as file', type(file))
    return file_dest


@blueprint.route('/hello', methods=['GET', 'POST'])
def hello():
    # return jsonify(status='succes', response='webapp is running')
    if request.method == 'POST':
        # https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request
        return jsonify(status='succes', response=f'Hello, {request.form.get("name")}!')
    else:
        return render_template('base_empty.html')
        # TODO jsonify(status='succes', response='webapp is running')


@blueprint.route('/debug', methods=['GET', 'POST'])
def debug():
    # POST function
    # url = f'https://hello-aixpact.azurewebsites.net/api/{function}'
    # response = requests.post(url, data={'name': request.args.get('name')})
    # GET function
    url = f'https://hello-aixpact.azurewebsites.net/api/{function}?name={request.args.get("name")}'
    response = requests.get(url)
    return jsonify(status='succes',
                   response=str(response))


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    """HttpTrigger"""
    form = FileForm()

    # Set csrf token in hidden field - avoid error message
    csrf_token = eval(str(form.csrf_token).split('=')[-1][:-1])
    form.csrf_token.data = csrf_token

    if form.validate_on_submit():
        file = form.file.data
        email = form.email.data
        function = form.function.data

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # Predict - HttpTrigger
            try:
                file_dest = handle_uploaded_file(file)
                blob_uri = predict(file_dest, email, function)
            except Exception as err:
                return jsonify(status='failed', error=str(err))
        logging.info('DEBUG log', blob_uri)
        print('DEBUG print', blob_uri)
        #     return redirect(url_for('base_blueprint.thankyou', name=email.split('@')[0]))
        # else:
        #     return render_template('base/upload.html', form=form)

        return redirect(url_for('base_blueprint.thankyou', name=email.split('@')[0]))

    return render_template('base/upload.html', form=form)


@blueprint.route("/thankyou")
def thankyou():
    name = request.args.get('name')
    return render_template('base/thank_you.html', name=name)


@blueprint.route("/function/<function_name>")
def function(function_name):
    """Takes some time....."""
    response = requests.get(f'http://www.aixpact.ml/api/{function_name}')
    return response.text
