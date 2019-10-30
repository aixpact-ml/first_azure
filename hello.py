import logging
import requests
import os
from flask import (Flask, Blueprint, redirect, request, flash, url_for, jsonify,
                   render_template, session, current_app, make_response,
                   send_file, send_from_directory)
from werkzeug.utils import secure_filename

import algo

app = Flask(__name__)

HTTP_BAD_REQUEST = 400
ALLOWED_EXTENSIONS = set(['txt', 'csv'])
SHARED = 'https://helloaixpact.file.core.windows.net/'
LOCAL_PATH = '/home/jovyan/aixpact/project/'
app.config['SHARED'] = SHARED
app.config['LOCAL_PATH'] = LOCAL_PATH
app.config['DEV'] = False


def _log_msg(msg):
    logging.info("{}: {}".format(datetime.now(),msg))


def allowed_file(filename):
    logging.info('some logging ....')
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

try:
    # https://docs.microsoft.com/en-us/azure/storage/files/storage-python-how-to-use-file-storage
    from azure.storage.file import FileService, ContentSettings
    from azure.storage.blob import BlockBlobService

    storageAccount = 'helloaixpact'
    accountKey = '/K/UXeclbEGQ6qxVEEXLrD47hwrxHGJGJnpGPVNZXu2dEEhJWSJ9G4+iDsvWDx4IfDYpIBW9OM+EX/4iNFbR1g=='
    directory_name = 'sampledir'
    file_in = f'https://helloaixpact.file.core.windows.net/myshare/myfile2'

    file_service = FileService(account_name=storageAccount, account_key=accountKey)
    file_service.create_share('myshare')
    file_service.create_directory('myshare', 'sampledir')

    # Create the BlockBlockService that the system uses to call the Blob service for the storage account.
    # https://docs.microsoft.com/nl-nl/azure/storage/blobs/storage-quickstart-blobs-python
    block_blob_service = BlockBlobService(
        account_name=storageAccount, account_key=accountKey)

    # Create a container called 'quickstartblobs'.
    container_name = 'quickstartblobs'
    block_blob_service.create_container(container_name)

    # Set the permission so the blobs are public.
    # block_blob_service.set_container_acl(
    #     container_name, public_access=PublicAccess.Container)
except:
    print('local debug')


def to_blob(file, container_name='quickstartblobs', blob_name='myblob', app_name='helloaixpact'):
    """"""
    # Save file to root dir in Azure - create path
    file_name = file.filename
    file.save(file_name)

    # Upload the file from path
    block_blob_service.create_blob_from_path(container_name, blob_name, file_name)
    http = f'https://{app_name}.blob.core.windows.net/{container_name}/{blob_name}'
    logging.info(f'Blob upload finished @ {http}')
    return http


@app.route("/")
def index():
    """"""
    text = 'woh'
    logging.info(f'some logging {text}')
    r = requests.get('http://www.aixpact.ml/api/httptrigger?name=frank')
    # print(r.content, r.status_code)
    return r.text


@app.route("/files")
def files():
    """"""
    # if the file in the root path of the share, please let the directory name as ''
    # file = file_service.get_file_to_text(share_name, directory_name, file_name)
    # print(file.content)
    fs = []
    generator = file_service.list_directories_and_files('myshare')
    for file_or_dir in generator:
        print(file_or_dir.name)
        logging.info(file_or_dir.name)
        fs.append(file_or_dir.name)
    return jsonify(status='completed', response=fs)


@app.route('/filename', methods=['GET', 'POST'])
def filename():
    if request.method == 'POST':
        # check if the post request has the file part
        for x in request.files['file']:
            print(x)
        try:
            return jsonify(status='completed', response=request.files['file'].filename)
        except:
            return jsonify(status='uncompleted', response='something went wrong')
    else:
        return jsonify(status='uncompleted', response='no file uploaded')


@app.route('/upload', methods=['GET', 'POST'])
def upload():

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # file_in = os.path.join(app.config['SHARED'], f'in_{filename}')

        #
        # return jsonify(status='completed', response=os.path.getsize(filename))
            if app.config['DEV']:
                file_in = os.path.join(app.config['LOCAL_PATH'], f'in_{filename}')
                logging.info('Local upload ....')
                file.save(file_in)
            else:
                file_in = to_blob(file)

            # return jsonify(status='completed', response=file_in)
            try:
                # Create forecast object
                app.config['ROOT'] = ''
                file_out = os.path.join(app.config['ROOT'], 'forecast.csv')
                model = algo.Model(filename=file_in, sep=',', header=0, filename_out=file_out)
                # Model
                response = model.predict(window=0, horizon=12, slen=6)
            except Exception as err:
                print('ooops... something went wrong')
                message = ('Failed to score the model. Exception: {}'.format(err))
                response = jsonify(status='error', error_message=message)
                response.status_code = HTTP_BAD_REQUEST
    # #         # FTUP(file_out)
            # return send_from_directory(app.config['ROOT'], 'forecast.csv', as_attachment=True)
            # return send_from_directory(app.config['LOCAL_PATH'],
            #                            'forecast.csv', as_attachment=True)
            return response  # jsonify(status='completed', response=response, filename=file_in)
    else:
        return jsonify(status='uncompleted', response='no response')


# Run and debug locally
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8241)
