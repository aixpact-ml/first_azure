import logging
import datetime
import requests
import os
import mimetypes
from flask import (Flask, Blueprint, redirect, request, flash, url_for, jsonify,
                   render_template, session, current_app, make_response,
                   send_file, send_from_directory)
from werkzeug.utils import secure_filename
from forms import LoginForm, FileForm

from utils.functions import *
# import algo
from .extensions import db, login_manager, csrf, mail

# CONFIG SETTINGS
from config.settings import config
app = Flask(__name__)
app.config.from_object(config)

HTTP_BAD_REQUEST = 400
ALLOWED_EXTENSIONS = set(['txt', 'csv'])
app.config['DEV'] = False


# Sanity check config settings
assert config.FRANK == 'test this environmental value', 'config settings failed'
assert config.FRANK == app.config['FRANK'], 'config settings failed'


# Set SECRET_KEY for Flask/wtforms
from flask_wtf.csrf import CsrfProtect
assert app.config['SECRET_KEY'] == config.SECRET_KEY, 'SECRET_KEY not set'
CsrfProtect(app)


# Flask-Mail settings via Azure ENV and below
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
assert app.config['MAIL_DEFAULT_SENDER'] == 'frank@aixpact.com', 'Flask-Mail settings failed'


from flask_mail import Mail, Message, Attachment
mail = Mail()
mail.init_app(app)


def send_email(recipients, filename):
    try:
        msg = Message('hAPIdays from AIxPact',
            sender='frank@aixpact.com',
            recipients=[recipients])
        try:
            msg.body = render_template('email_message.txt', recipients=recipients)
        except:
            msg.body = 'Hello ' + recipients + ',\nblahblahblah'
        msg.html = None  # render_template('email_message.html', recipients=recipients)

        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Complete_list_of_MIME_types
        mime = mimetypes.guess_type(filename, strict=False)[0]
        with open(filename, 'r') as f:
            msg.attach(filename, mime, f.read())
        mail.send(msg)
    except Exception as err:
        print(err)


def _log_msg(msg):
    logging.info("{}: {}".format(datetime.datetime.now(), msg))


def allowed_file(filename):
    _log_msg('checking allowed file ...')
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def block_blob(filename):
    # https://azuresdkdocs.blob.core.windows.net/$web/python/azure-storage-blob/12.0.0b5/azure.storage.blob.html
    SOURCE_FILE = filename
    DEST_FILE = 'something_temp.csv'
    CONTAINER = 'hapidays'

    # Instantiate a new BlobServiceClient using a connection string
    from azure.storage.blob import BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(config.BLOB_CONX)

    # Instantiate a new ContainerClient
    container_client = blob_service_client.get_container_client(CONTAINER)

    try:
        # Create new container in the service
        container_client.create_container()

        # List containers in the storage account
        list_response = blob_service_client.list_containers()
    except Exception as err:
        logging.info(f'Failed to create/list container: {err}')

    try:
        # Instantiate a new BlobClient
        blob_client = container_client.get_blob_client(SOURCE_FILE)
        # blob_client = blob_service_client.get_blob_client(CONTAINER, SOURCE_FILE)

        # [START upload_a_blob]
        # Upload content to block blob
        with open(SOURCE_FILE, "rb") as data:
            blob_client.upload_blob(data)
        # [END upload_a_blob]

        # [START download_a_blob]
        # with open(DEST_FILE, "wb") as my_blob:
        #     download_stream = blob_client.download_blob()
        #     my_blob.write(download_stream.readall())
        # [END download_a_blob]

        # [START delete_blob]
        # blob_client.delete_blob()
        # [END delete_blob]
    except Exception as err:
        logging.info(f'Failed to create blob: {err}')


@app.route("/")
def index():
    return jsonify(status='succes', response='api is online')


@app.route("/function/<function_name>")
def function(function_name):
    """Takes some time....."""
    response = requests.get(f'http://www.aixpact.ml/api/{function_name}')
    return response.text  # jsonify(response=response.content)


@app.route('/upload_form', methods=['GET', 'POST'])
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
                block_blob(file_in)
        send_email(email, file_in)
        flash(f'thank you an email has been sent to: {email} with attachment: {file_in}')
        return redirect(url_for('thankyou', message=file_in))
        flash(f'Try again.....')
    return render_template('upload.html', form=form)


@app.route("/thankyou")
def thankyou():
    return jsonify(status='succes', response=request.args.get('message'))


# Run and debug locally in Jupyter
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8241)
