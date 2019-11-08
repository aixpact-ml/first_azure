import logging
import datetime
# import requests
# import os
import mimetypes
from flask import (Flask, Blueprint, redirect, request, flash, url_for, jsonify,
                   render_template, session, current_app, make_response,
                   send_file, send_from_directory)
from flask_mail import Message
# from werkzeug.utils import secure_filename
# from forms import LoginForm, FileForm

# import algo
from webapp.extensions import mail


# # Flask-Mail settings via Azure ENV and below
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = False
# assert app.config['MAIL_DEFAULT_SENDER'] == 'frank@aixpact.com', 'Flask-Mail settings failed'

# from flask_mail import Mail, Message, Attachment
# mail = Mail()
# mail.init_app(app)


def _log_msg(msg):
    logging.info("{}: {}".format(datetime.datetime.now(), msg))


def allowed_file(filename, allowed_extensions=['txt', 'csv']):
    _log_msg('checking allowed file ...')
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def send_email(recipients, filename):
    try:
        msg = Message('hAPIdays from AIxPact',
            sender='frank@aixpact.com',
            recipients=[recipients])
        name = recipients.split('@')[0].lower().capitalize()
        try:
            msg.body = render_template('email_message.txt', recipients=name)
        except:
            msg.body = 'Hello ' + name + ', \n Thank you for joining hAPIdays, enjoy your result!\n'
        msg.html = None  # render_template('email_message.html', recipients=recipients)

        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Complete_list_of_MIME_types
        mime = mimetypes.guess_type(filename, strict=False)[0] or 'text/txt'
        with open(filename, 'r') as f:
            msg.attach(filename, mime, f.read())
        f.close()
        print(msg)  # create timeout to solve 'downloading issue'
        mail.send(msg)
    except Exception as err:
        print(err)


def block_blob(filename, connection_string):
    # https://azuresdkdocs.blob.core.windows.net/$web/python/azure-storage-blob/12.0.0b5/azure.storage.blob.html
    SOURCE_FILE = filename
    DEST_FILE = 'something_temp.csv'
    CONTAINER = 'hapidays'

    # Instantiate a new BlobServiceClient using a connection string
    from azure.storage.blob import BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

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

        # Upload content to block blob
        with open(SOURCE_FILE, "rb") as data:
            blob_client.upload_blob(data)

    except Exception as err:
        logging.info(f'Failed to create blob: {err}')


def binary2csv(text, path):
    """"""
    import ast
    import pandas as pd
    lines = []
    for i, x in enumerate(text.decode('utf-8').split()):
        try:
            sample = ast.literal_eval(x)
            # Ignore duplicate headers
            if i == 0:
                lines.append(sample)
            else:
                if ''.join(sample) != ''.join(lines[0]):
                    lines.append(sample)
        except:
            continue
    df = pd.DataFrame(lines)
    df.columns = df.iloc[0]
    df = df[1:]
    df.to_csv(path, index=False)
    with open(path, 'r') as f:
        logging.info((f.read()))
    return pd.read_csv(path)
