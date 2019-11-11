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

# from webapp.extensions import db, login_manager, csrf #, mail
from webapp.extensions import mail
from . import blueprint


def handle_uploaded_file(file, file_dest):
    # Azure vs. local, web form vs. POST
    try:
        os.mkdir('./data')
    except:
        pass
    file_in = os.path.join('./data', file_dest)
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


@blueprint.route('/hello', methods=['GET', 'POST'])
def hello():
    # return jsonify(status='succes', response='webapp is running')
    if request.method == 'POST':
        # https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request
        return jsonify(status='succes', response=f'Hello, {request.form.get("name")}!')
    else:
        return render_template('base_empty.html')
        # TODO jsonify(status='succes', response='webapp is running')


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    # https://stackoverflow.com/questions/38079288/flask-file-not-detecting-on-upload
    # When using email with file attached
    from werkzeug.datastructures import CombinedMultiDict
    form = FileForm(CombinedMultiDict((request.files, request.form)))

    # If email without file upload
    # form = FileForm(request.form)

    # Set csrf token in hidden field - avoid error message
    csrf_token = eval(str(form.csrf_token).split('=')[-1][:-1])
    form.csrf_token.data = csrf_token

    if form.validate_on_submit():
        file = form.file.data
        email = form.email.data
        name = email.split('@')[0].lower().capitalize()
        function = form.function.data
        ext = '.' + file.filename.split('.')[-1]
        file_in = email.replace('@', '_').replace('.', '_').replace('-', '_') + ext
        file_out = f'{function}_{uuid.uuid4()}.txt'  # random filename

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            handle_uploaded_file(request.files['file'], file_in)

            print('DEBUG', type(file), '\n', request.files['file']) #, isinstance(file))
            logging.info('DEBUG', type(file), '\n', request.files["file"]) #, isinstance(file))
            assert 1 == 0, f'{request.files["file"]}'
            # local: DEBUG <class 'werkzeug.datastructures.FileStorage'>
            # Azure: DEBUG <class

            # Send email
            try:
                download = f'https://helloaixpact.blob.core.windows.net/hapidays/{file_out}'
                template = render_template('base/email_message.html',
                                            name=name,
                                            filename=download)
                send_email(template, email, download)
            except Exception as err:
                print('email error:', err)

            # Call serverless function
            data = predict(file_in, file_out, function)
            # data = predict(file, file_out, function)  # test this

        else:
            return render_template('base/upload.html', form=form)  # TODO

        return redirect(url_for('base_blueprint.thankyou',
                        file_in=file_in,
                        file_out=file_out,
                        email=email,
                        function=function,
                        data=data[:10]))  # Check/debug data from within Azure
        flash(f'Try again.....')
    return render_template('base/upload.html', form=form)


@blueprint.route("/thankyou")
def thankyou():
    file_in = request.args.get('file_in')
    email = request.args.get('email')
    function = request.args.get('function')
    file_out = request.args.get('file_out')
    data = request.args.get('data')

    flash(f'Thank you! \n\nAn email has been sent to: {email} \nAttachment: {file_out}')
    try:
        r = render_template('base/thankyou.html',
                            email=email.split('@')[0],
                            file=file_out)
        return r
    except:
        return jsonify(status='succes',
                       response=f'Thank you! \n\nAn email has been sent to: {email} \n \
                                  Attachment: {file_out}',
                       data=data)  # Check/debug data from within Azure


@blueprint.route("/function/<function_name>")
def function(function_name):
    """Takes some time....."""
    response = requests.get(f'http://www.aixpact.ml/api/{function_name}')
    return response.text  # jsonify(response=response.content)


################ OLD
# @blueprint.route('/upload_form', methods=['GET', 'POST'])
# def upload_form():
#     form = FileForm()
#     if form.validate_on_submit():
#         file = form.file.data
#         email = form.email.data
#         function_ = form.function.data
#         print('DEBUG function:', form.function.data)
#         ext = '.' + file.filename.split('.')[-1]
#         file_in = email.replace('@', '_').replace('.', '_').replace('-', '_') + ext

#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             try:
#                 # Local dev
#                 file.save(os.path.join(config.LOCAL, file_in))
#             except:
#                 # Azure
#                 file.save(file_in)
#                 # blob_upload(file_in)
#                 # block_blob(file_in, config.BLOB_CONX)
#         else:
#             return render_template('base/upload.html', form=form)  # TODO

#         # assert file_in is None, f'file_in: {file_in} \n {open(file_in, "rb")}\n'
#         assert function_ is None, f'function is {function_}'
#         return redirect(url_for('base_blueprint.thankyou',
#                         file_in=file_in,
#                         email=email,
#                         function_=function_))
#     return render_template('base/upload.html', form=form)
