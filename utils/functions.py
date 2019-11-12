import logging
import datetime
import mimetypes
import requests
import os
from flask import (Flask, Blueprint, redirect, request, flash, url_for, jsonify,
                   render_template, session, current_app, make_response,
                   send_file, send_from_directory)
from azure.storage.blob import BlobServiceClient

from .blob import blob_upload, blob_download
from .decorators import fire_and_forget
from config.settings import config
from .email import send_email


@fire_and_forget
def predict(file_dest, email, function):
    """Call serverless function and save result as blob."""

    # Call serverless Azure function - returns blob_id
    url = f'https://hello-aixpact.azurewebsites.net/api/{function}'
    files = {'file': open(file_dest, 'rb')}
    response = requests.post(url, files=files)
    blob_uri = f'https://helloaixpact.blob.core.windows.net/hapidays/{response.text}'
    name = email.split('@')[0].lower().capitalize()

    # Send email
    try:
        template = render_template('base/email_message.html',
                                    name=name,
                                    filename=blob_uri)
        send_email(template, email, blob_uri)
    except Exception as err:
        print('email error:', err)

    return blob_uri


def _log_msg(msg):
    logging.info("{}: {}".format(datetime.datetime.now(), msg))


def allowed_file(filename, allowed_extensions=['txt', 'csv']):
    _log_msg('checking allowed file ...')
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


# def _blob_client(source_file, connection_string, container='hapidays'):
#     # from webapp.app import app
#     # https://azuresdkdocs.blob.core.windows.net/$web/python/azure-storage-blob/12.0.0b5/azure.storage.blob.html
#     assert connection_string != 'wtf', 'connection string undefined'

#     # Instantiate a new BlobServiceClient using a connection string
#     blob_service_client = BlobServiceClient.from_connection_string(connection_string)

#     # Instantiate a new ContainerClient
#     container_client = blob_service_client.get_container_client(container)

#     # Create new container in the service
#     try:
#         container_client.create_container()
#     except Exception as err:
#         print(f'Failed to create/list container: {err}')
#         logging.info(f'Failed to create/list container: {err}')

#     try:
#         # Instantiate a new BlobClient
#         blob_client = container_client.get_blob_client(source_file)
#     except Exception as err:
#         print(f'Failed to create blob: {err}')
#         logging.info(f'Failed to create blob: {err}')
#         return None
#     return blob_client


# def blob_upload(source_file, connection_string):
#     """Upload the blob from a local file."""
#     # Azure doesnot like load files in cwd? -> fix empty blobs
#     try:
#         os.mkdir('./data')
#         path = os.path.join('./data', source_file)
#         with open(path, "w") as f:
#             f.write('Hello, World!')
#     except:
#         with open(source_file, "w") as f:
#             f.write('Hello, World!')

#     try:
#         blob_client = _blob_client(source_file, connection_string)
#         try:
#             blob_client.delete_blob()
#         except:
#             print('no existing blob to delete/replace')
#         with open(path, "rb") as data:
#             blob_client.upload_blob(data)
#     except Exception as err:
#         print(f'Failed to upload blob: {err}')
#         logging.info(f'Failed to upload blob: {err}')


# def blob_upload_(source_file, connection_string):
#     """Upload the blob from a local file."""
#     try:
#         blob_client = _blob_client(source_file, connection_string)
#         try:
#             blob_client.delete_blob()
#         except:
#             print('no existing blob to delete/replace')
#         with open(source_file, "rb") as data:
#             blob_client.upload_blob(data)    # empty blob??
#     except Exception as err:
#         print(f'Failed to upload blob: {err}')
#         logging.info(f'Failed to upload blob: {err}')


# def blob_download(destination_file='something_temp.csv'):
#     """Download the blob to a local file."""
#     try:
#         blob_client = _blob_client(destination_file, connection_string)
#         with open(destination_file, "wb") as f:
#             f.write(blob_client.download_blob().readall())
#     except Exception as err:
#         logging.info(f'Failed to download blob: {err}')


# def block_blob(filename, connection_string):
#     # https://azuresdkdocs.blob.core.windows.net/$web/python/azure-storage-blob/12.0.0b5/azure.storage.blob.html
#     SOURCE_FILE = filename
#     DEST_FILE = 'something_temp.csv'
#     CONTAINER = 'hapidays'

#     # Instantiate a new BlobServiceClient using a connection string
#     from azure.storage.blob import BlobServiceClient
#     blob_service_client = BlobServiceClient.from_connection_string(connection_string)

#     # Instantiate a new ContainerClient
#     container_client = blob_service_client.get_container_client(CONTAINER)

#     try:
#         # Create new container in the service
#         container_client.create_container()

#         # List containers in the storage account
#         list_response = blob_service_client.list_containers()
#     except Exception as err:
#         logging.info(f'Failed to create/list container: {err}')

#     try:
#         # Instantiate a new BlobClient
#         blob_client = container_client.get_blob_client(SOURCE_FILE)

#         # Upload content to block blob
#         with open(SOURCE_FILE, "rb") as data:
#             blob_client.upload_blob(data)

#     except Exception as err:
#         logging.info(f'Failed to create blob: {err}')


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
