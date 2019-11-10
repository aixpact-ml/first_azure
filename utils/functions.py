import logging
import datetime
import mimetypes
import requests
from flask import (Flask, Blueprint, redirect, request, flash, url_for, jsonify,
                   render_template, session, current_app, make_response,
                   send_file, send_from_directory)
from azure.storage.blob import BlobServiceClient

from .decorators import fire_and_forget
from config.settings import config


@fire_and_forget
def predict(file_in, file_out, function, binary=False):
    """Call serverless function and save result as blob."""
    # Call function
    url = f'https://hello-aixpact.azurewebsites.net/api/{function}'
    with open(file_in, 'r') as f:
        response = requests.post(url, files={'file': f})

    # Save as temp file
    # file_path = os.path.join(os.getcwd(), file_out)  ####### TODO
    # if binary:
    #     with open(file_out, 'wb') as f:
    #         f.write(response.content)
    # else:
    #     with open(file_out, 'w') as f:
    #         f.write(response.text)
    # Upload temp file to blob
    try:
        blob_upload(file_out, response, config.BLOB_CONX)
        print(f'Finished function and uploaded result as blob {file_out}')
    except Exception as err:
        print('blob error:', err)
    return response.text


def _log_msg(msg):
    logging.info("{}: {}".format(datetime.datetime.now(), msg))


def allowed_file(filename, allowed_extensions=['txt', 'csv']):
    _log_msg('checking allowed file ...')
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def _blob_client(source_file, connection_string, container='hapidays'):
    # from webapp.app import app
    # https://azuresdkdocs.blob.core.windows.net/$web/python/azure-storage-blob/12.0.0b5/azure.storage.blob.html
    assert connection_string != 'wtf', 'connection string undefined'

    # Instantiate a new BlobServiceClient using a connection string
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Instantiate a new ContainerClient
    container_client = blob_service_client.get_container_client(container)

    # Create new container in the service
    try:
        container_client.create_container()
    except Exception as err:
        print(f'Failed to create/list container: {err}')
        logging.info(f'Failed to create/list container: {err}')

    try:
        # Instantiate a new BlobClient
        blob_client = container_client.get_blob_client(source_file)
    except Exception as err:
        print(f'Failed to create blob: {err}')
        logging.info(f'Failed to create blob: {err}')
        return None
    return blob_client


def blob_upload(source_file, data, connection_string):
    """Upload the blob from a local file."""
    try:
        blob_client = _blob_client(source_file, connection_string)
        try:
            blob_client.delete_blob()
        except:
            print('no existing blob to delete/replace')
        # with open(source_file, "rb") as data:
        blob_client.upload_blob(data)
    except Exception as err:
        print(f'Failed to upload blob: {err}')
        logging.info(f'Failed to upload blob: {err}')


def blob_download(destination_file='something_temp.csv'):
    """Download the blob to a local file."""
    try:
        blob_client = _blob_client(destination_file, connection_string)
        with open(destination_file, "wb") as f:
            f.write(blob_client.download_blob().readall())
    except Exception as err:
        logging.info(f'Failed to download blob: {err}')


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
