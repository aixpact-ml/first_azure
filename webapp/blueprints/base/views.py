import pandas as pd
import logging
import datetime
import requests
import os
import mimetypes
from flask import (Flask, Blueprint, redirect, request, flash, url_for, jsonify,
                   render_template, session, current_app, make_response,
                   send_file, send_from_directory)
from flask_mail import Message
from werkzeug.utils import secure_filename

from .forms import FileForm  # , LoginForm

from config.settings import config
from utils.functions import _log_msg, allowed_file, send_email, block_blob, binary2csv, blob_upload, blob_download
from utils.functions import mail
# from functions import *
# import algo
# from webapp.extensions import db, login_manager, csrf #, mail

from . import blueprint


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    # return jsonify(status='succes', response='webapp is running')
    if request.method == 'POST':
        # https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request
        return jsonify(status='succes', response=f'Hello, {request.form.get("name")}!')
    else:
        return render_template('base_empty.html')  # TODO jsonify(status='succes', response='webapp is running')


@blueprint.route("/function/<function_name>")
def function(function_name):
    """Takes some time....."""
    response = requests.get(f'http://www.aixpact.ml/api/{function_name}')
    return response.text  # jsonify(response=response.content)


@blueprint.route('/debug', methods=['GET', 'POST'])
def debug():
    from werkzeug.datastructures import CombinedMultiDict
    # https://stackoverflow.com/questions/38079288/flask-file-not-detecting-on-upload
    form = FileForm(CombinedMultiDict((request.files, request.form)))
    # form = FileForm(request.form)
    csrf_token = eval(str(form.csrf_token).split('=')[-1][:-1])
    form.csrf_token.data = csrf_token
    # print('DEBUG:')
    # print(request.values)
    # print('file', form.file.data)
    # print('form.validate', form.validate())
    # print('form.errors', form.errors)
    # print('request.files', request.files)
    # print('form.function.data', form.function.data)
    if form.validate_on_submit():
        file = form.file.data
        email = form.email.data
        function = form.function.data
        ext = '.' + file.filename.split('.')[-1]
        file_in = email.replace('@', '_').replace('.', '_').replace('-', '_') + ext

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            try:
                # Local dev
                file.save(os.path.join(config.LOCAL, file_in))
            except:
                # Azure
                file.save(file_in)
                blob_upload(file_in)
                # block_blob(file_in, config.BLOB_CONX)
                blob_download('some_temp.txt')

        else:
            return render_template('base/upload.html', form=form)  # TODO

        return redirect(url_for('base_blueprint.thankyou',
            file_in=file_in,
            email=email,
            function=function))
        flash(f'Try again.....')
    return render_template('base/upload.html', form=form)
    # return jsonify(status='succes', token=csrf_token, errors=form.errors, files=request.files==None)

    # if form.validate_on_submit():
    #     file = form.file.data
    #     email = form.email.data
    #     function = form.function.data
    #     print(file, email, function)
    #     return jsonify(status='succes', response=email)
    # else:
    #     return render_template('base/upload.html', form=form)


@blueprint.route('/upload_form', methods=['GET', 'POST'])
def upload_form():
    form = FileForm()
    if form.validate_on_submit():
        file = form.file.data
        email = form.email.data
        function_ = form.function.data
        print('DEBUG function:', form.function.data)
        ext = '.' + file.filename.split('.')[-1]
        file_in = email.replace('@', '_').replace('.', '_').replace('-', '_') + ext

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            try:
                # Local dev
                file.save(os.path.join(config.LOCAL, file_in))
            except:
                # Azure
                file.save(file_in)
                # blob_upload(file_in)
                block_blob(file_in, config.BLOB_CONX)
        else:
            return render_template('base/upload.html', form=form)  # TODO

        # assert file_in is None, f'file_in: {file_in} \n {open(file_in, "rb")}\n'
        assert function_ is None, f'function is {function_}'
        return redirect(url_for('base_blueprint.thankyou',
            file_in=file_in,
            email=email,
            function_=function_))
        flash(f'Try again.....')
    return render_template('base/upload.html', form=form)


@blueprint.route("/thankyou")
def thankyou():
    file_in = request.args.get('file_in')
    email = request.args.get('email')
    function = request.args.get('function')
    file_out = f'{function}.txt'

    # Call serverless function
    url = f'https://hello-aixpact.azurewebsites.net/api/{function}'
    with open(file_in, 'rb') as f:
        response = requests.post(url, files={'file': f})
    # print('DEBUG:', response.ok, response.status_code, response.text[:10]+'....')

    # Save as file
    with open(file_out, 'w') as f:
        f.write(response.text)

    # Send email
    send_email(email, file_out)
    flash(f'Thank you! \n\nAn email has been sent to: {email} \nAttachment: {file_out}')

    try:
        r = render_template('base/thankyou.html',
            email=email.split('@')[0],
            file=file_out)
        return r
    except:
        return jsonify(status='succes', response='....')
