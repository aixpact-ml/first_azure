import logging
# import datetime
# import mimetypes
# import requests
import os
# from flask import (Flask, Blueprint, redirect, request, flash, url_for, jsonify,
#                    render_template, session, current_app, make_response,
#                    send_file, send_from_directory)
from azure.storage.blob import BlobServiceClient
from config.settings import config


def _blob_client(source_file, container='hapidays'):
    """https://azuresdkdocs.blob.core.windows.net/$web/python/azure-storage-blob/12.0.0b5/azure.storage.blob.html"""
    # Instantiate a new BlobServiceClient using a connection string
    blob_service_client = BlobServiceClient.from_connection_string(config.BLOB_CONX)

    # Instantiate a new ContainerClient to create new container in the service
    container_client = blob_service_client.get_container_client(container)
    try:
        container_client.create_container()
    except Exception as err:
        pass

    # Instantiate a new BlobClient to create blobs
    try:
        blob_client = container_client.get_blob_client(source_file)
    except Exception as err:
        blob_client = None

    return blob_client


def blob_upload(source_file, data):
    """Upload the blob from a local file."""
    # Azure doesnot like load files in cwd? -> fix empty blobs
    # path = os.path.join('./data', source_file)
    # try:
    #     with open(path, "w") as f:
    #         f.write(data)
    # except:
    #     os.mkdir('./data')
    #     with open(path, "w") as f:
    #         f.write(data)

    try:
        blob_client = _blob_client(source_file)
        try:
            blob_client.delete_blob()
        except:
            pass
            # print('no existing blob to delete/replace')
        blob_client.upload_blob(data)
        # with open(path, "rb") as data:
        #     blob_client.upload_blob(data)
    except Exception as err:
        print(f'Failed to upload blob: {err}')
        logging.info(f'Failed to upload blob: {err}')


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


def blob_download(destination_file='something_temp.csv'):
    """Download the blob to a local file."""
    try:
        blob_client = _blob_client(destination_file)
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

